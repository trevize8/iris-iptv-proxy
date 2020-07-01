FROM python:3-alpine

ADD . /app

RUN pip install -U python-dotenv

ENV IRIS_DEVICE_HOST ${IRIS_DEVICE_HOST:-192.168.1.101}
ENV IRIS_PROXY_HOST ${IRIS_PROXY_HOST:-localhost}
ENV IRIS_PROXY_PORT ${IRIS_PROXY_PORT:-8000}

WORKDIR /app

CMD [ "python", "./iris-iptv-proxy.py" ]