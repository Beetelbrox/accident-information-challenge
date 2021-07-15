  
FROM apache/airflow:2.1.1
USER root

RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean

USER airflow
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
