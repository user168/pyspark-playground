# Generate random events data
import datetime
import time
import uuid
import random
import json
import yfinance as yf

#given a list of ticker symbols, get the stock data, every 2 seconds
def get_stock_data(tickers):
    data={}
    while True:
        for ticker in tickers:
            data[ticker]= yf.download(ticker, start="2021-01-01", end="2021-01-10")
            
            

event_status: list = ["SUCCESS", "ERROR", "STANDBY"] + [None]
device_id: list = ['D' + str(_id).rjust(3, '0') for _id in range(1, 6)] + [None]
customer_id: list = ["CI" + str(_id).rjust(5, '0') for _id in range(100, 121)]


# Generate event data from devices
def generate_events(offset=0):
    _event = {
        "eventId": str(uuid.uuid4()),
        "eventOffset": offset,
        "eventPublisher": "device",
        "customerId": random.choice(customer_id),
        "data": {
            "tickers": [
                {
                    "deviceId": random.choice(device_id),
                    "temperature": random.randint(0, 30),
                    "measure": "C",
                    "status": random.choice(event_status)
                } for i in range(random.randint(0, 3))
            ],
        },
        "eventTime": str(datetime.datetime.now())
    }

    return json.dumps(_event)



if __name__ == "__main__":
    _offset = 10000
    while True:
        print(generate_events(offset=_offset))
        time.sleep(random.randint(0, 5))
        _offset += 1