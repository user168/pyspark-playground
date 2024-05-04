FROM python:3.10-bullseye as spark-base

ARG SPARK_VERSION=3.5.1
ARG DELTA_VERSION=3.1.0

# Install tools required by the OS
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      curl \
      vim \
      unzip \
      rsync \
      openjdk-11-jdk \
      build-essential \
      software-properties-common \
      ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Setup the directories for our Spark and Hadoop installations
ENV SPARK_HOME=${SPARK_HOME:-"/opt/spark"}
ENV HADOOP_HOME=${HADOOP_HOME:-"/opt/hadoop"}

RUN mkdir -p ${HADOOP_HOME} && mkdir -p ${SPARK_HOME}
WORKDIR ${SPARK_HOME}

# Download and install Spark
RUN curl https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz -o spark.tgz && \
tar -xf  spark.tgz  && \
mkdir -p /opt/spark && \
mv ./spark-${SPARK_VERSION}-bin-hadoop3/* /opt/spark && \
rm -rf spark.tgz && \
rm -rf spark-${SPARK_VERSION}-bin-hadoop3


FROM spark-base as pyspark

# Install python deps
COPY requirements/requirements.txt .
RUN pip3 install -r requirements.txt

# Setup Spark related environment variables
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"
ENV SPARK_MASTER="spark://spark-master:7077"
ENV SPARK_MASTER_HOST spark-master
ENV SPARK_MASTER_PORT 7077
ENV PYSPARK_PYTHON python3

# Copy the default configurations into $SPARK_HOME/conf
COPY conf/spark-defaults.conf "$SPARK_HOME/conf"

RUN chmod u+x /opt/spark/sbin/* && \
    chmod u+x /opt/spark/bin/*

ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH

RUN wget https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.1.0/delta-spark_2.12-3.1.0.jar && \
    mv delta-spark_2.12-3.1.0.jar /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/io/delta/delta-storage/3.1.0/delta-storage-3.1.0.jar && \
    mv delta-storage-3.1.0.jar /opt/spark/jars/
RUN wget https://repo1.maven.org/maven2/io/delta/delta-standalone_2.12/3.1.0/delta-standalone_2.12-3.1.0.jar && \
    mv delta-standalone_2.12-3.1.0.jar /opt/spark/jars/
    
RUN export PACKAGES="io.delta:delta-spark_2.12-3.1.0"
RUN export PYSPARK_SUBMIT_ARGS="--packages ${PACKAGES} pyspark-shell"

# Copy appropriate entrypoint script
COPY entrypoint.sh .

ENTRYPOINT ["./entrypoint.sh"]
