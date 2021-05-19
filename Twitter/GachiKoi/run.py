import datetime as dt
import os

from src.gachikoi_manager import GachikoiManager

if __name__ == "__main__":
    CK = os.environ["CONSUMER_KEY"]
    CS = os.environ["CONSUMER_SECRET"]
    ATK = os.environ["ACCESS_TOKEN"]
    ATS = os.environ["ACCESS_SECRET"]

    GachikoiManager(
        consumer_key=CK,
        consumer_secret=CS,
        access_token_key=ATK,
        access_token_secret=ATS,
    ).execute_all()
