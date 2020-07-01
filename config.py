"""App configuration."""
from dotenv import load_dotenv

load_dotenv()

from os import environ


class Config:
    """Set configuration vars from .env file. (or from environment variables otherwise) """

    # Deco HOST or IP
    IRIS_DEVICE_HOST = environ.get('IRIS_DEVICE_HOST')

    IRIS_PROXY_HOST = environ.get('IRIS_PROXY_HOST')
    IRIS_PROXY_PORT = environ.get('IRIS_PROXY_PORT')
