import pyotp
import robin_stocks.robinhood as rh
from stock_tracer.config import config
import yfinance as yf
from logging import getLogger


class RobinhoodConnector:
    def __init__(self, username, password):
        totp = pyotp.TOTP(config.robinhood["mfa_application_identifier"]).now()
        rh.authentication.login(username, password, mfa_code=totp)
        self.rh_conn = rh
        self.build_holdings = None

    def fetch_build_holdings(self):
        # totp = pyotp.TOTP(config.robinhood["mfa_application_identifier"]).now()
        # rh.authentication.login(username, password, mfa_code=totp)
        my_stocks = self.rh_conn.build_holdings()
        return my_stocks

    def fetch_historicals(self, symbols: str or list = None, time_period: str = "5y"):
        """
        Returns a dictionary mapping ticker to a pandas dataframe interpreted dictionary of the stock's historical data
        """
        # Fetch build holding symbols/tickers
        if symbols is None:
            if self.build_holdings is None:
                self.build_holdings = self.fetch_build_holdings()

            symbols = list(self.build_holdings.keys())

        # Fetch historical data from yfinance
        #   could also get from robinhood, but yfinance is faster and more accurate
        response = yf.Tickers(" ".join(symbols))
        tickers = response.tickers
        historical_data = {}
        for ticker, ticker_obj in tickers.items():
            try:
                df = ticker_obj.history(period=time_period)
            except Exception:
                df = ticker_obj.history(period="ytd")

            df.index = df.index.map(str)
            ticker_historicals = df.to_dict("index")
            historical_data[ticker] = ticker_historicals
        return historical_data

    def fetch_transactions(self):
        stock_orders = self.rh_conn.get_all_stock_orders()
        return stock_orders


if __name__ == "__main__":
    import logging
    import json

    logger = logging.getLogger(__name__)
    rh = RobinhoodConnector(config.robinhood["username"], config.robinhood["password"])
    transations = rh.fetch_transactions()
    historicals = rh.fetch_historicals()
    logger.warning(historicals.keys())
