import argparse
import concurrent.futures
import json
import time

from dotenv import dotenv_values
from kafka import KafkaProducer
import pandas as pd
import yfinance as yf


class Producer:
    """Kafka producer to send stock price data."""

    def __init__(self, config, topic, symbol):
        self.serv_addr = config["KAFKA_SERV_ADDR"]
        self.topic = topic
        self.symbol = symbol
        self._producer = None

    def __enter__(self):
        # Initialise the Kafka producer
        self._producer = KafkaProducer(bootstrap_servers=self.serv_addr)
        return self

    def __exit__(self, type, value, traceback):
        # Close the Kafka producer
        self._producer.close()

    def run(self):
        """Produce messages to a Kafka topic."""

        # Raise an Expection if self._producer is not initialised
        if self._producer is None:
            raise Exception("Producer has not been initialised")

        try:
            # Download and save 5 days worth of minute stock data
            # into a data frame
            self._log("Downloading stock data")
            df = yf.download(tickers=self.symbol, period="1mo", interval="1h")

            # Insert column for timestamp into data
            start = int(time.time())
            end = int(start + df.shape[0])
            df.insert(0, "Timestamp", range(start, end), True)
            
            # Publish messages
            self._stream(df)
        
        except Exception as exc:
            self._log(f"Error: {exc}")
            raise exc

    def _stream(self, df):
        """Publish data from the given dataframe to a Kafka topic."""
        self._log(f"({self.symbol}) Streaming data")
        for _, row in df.iterrows():
            message = json.dumps(list(row.values))
            self._publish(message)
            time.sleep(1)

    def _publish(self, message):
        """Publish Kafka message to a topic."""
        self._producer.send(self.topic, message.encode('utf-8'))
        self._log(f"({self.symbol}) Published: {message}")

    def _log(self, text):
        """Print a message."""
        print(f"({self.symbol}) {text}")

def stream_data(config, symbol):
    """Runs a Kafka producer for the given stock symbol."""
    topic = f"stock_data_{symbol.lower()}"
    with Producer(config, topic=topic, symbol=symbol) as producer:
        producer.run()

def main(config):
    """
        Runs a Kafka producer for each stock symbol.
        Each producer is run concurrently in a separate thread.

        Args:
            config (dict): Config dictionary, must contain the
                folling values:
                > SYMBOLS (list): List of stock symbols
                > KAFKA_SERV_ADDR (str): Kafka server address

        Returns:
            None

        Raises:
            Exception: Raised with any unexpected error.
    """
    symbols = [symbol.upper() for symbol in config["SYMBOLS"]]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(stream_data, config, symbol): symbol for symbol in symbols}
        for future in concurrent.futures.as_completed(futures):
            future.result()

if __name__ == "__main__":
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="""
        A Kafka producer which use historical stock price data 
        from Yahoo Finance to publish as real-time stock data.
    """)
    parser.add_argument(
        'symbols',
        metavar='symbols',
        type=str,
        nargs='+',
        help='stock symbols to produce messages for',
    )
    args = parser.parse_args()

    # Get .env config
    config = dotenv_values(".env.kafka")
    config["SYMBOLS"] = args.symbols

    # Run main function
    main(config)