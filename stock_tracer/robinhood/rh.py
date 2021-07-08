import pyotp
import robin_stocks.robinhood as rh
from stock_tracer.config import config
import yfinance as yf
import logging

logger = logging.getLogger(__name__)
logger.setLevel(20)


class RobinhoodConnector:
    def __init__(self, username, password, mfa_code=""):
        self.username = username
        self.build_holdings = None
        self.rh_conn = None
        try:
            if mfa_code == "" or mfa_code is None:
                mfa_code = pyotp.TOTP(
                    config.robinhood["mfa_application_identifier"]
                ).now()

            rh.authentication.login(username, password, mfa_code=mfa_code)
            self.rh_conn = rh
        except Exception:
            logger.info("MFA Prompt Sent")

    def login(self, password, mfa_code=None):
        try:
            rh.authentication.login(self.username, password, mfa_code=mfa_code)
            self.rh_conn = rh
        except Exception:
            logger.info("MFA Prompt Sent")

    def fetch_build_holdings(self):
        my_stocks = self.rh_conn.build_holdings()
        return my_stocks

    def fetch_account_profile(self):
        profile = self.rh_conn.profiles.load_portfolio_profile()
        return profile

    def fetch_historicals(self, symbols: str or list = None, time_period: str = "5y"):
        """
        Returns a dictionary mapping each ticker (in the user's holdings) to a pandas dataframe-interpreted dictionary of the stock's historical data
        """
        logger.warning("Logged Into Robinhood")

        # Fetch build holding symbols/tickers
        if symbols is None:
            if self.build_holdings is None:
                self.build_holdings = self.fetch_build_holdings()

            symbols = [x.replace(".", "-") for x in list(self.build_holdings.keys())]

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
            historical_data[ticker.replace("-", ".")] = ticker_historicals

        return historical_data

    def fetch_earnings(self):
        if self.build_holdings is None:
            symbols = list(self.rh_conn.build_holdings().keys())
        else:
            symbols = list(self.build_holdings.keys())

        earnings_dict = {}
        for s in symbols:
            logger.warning(s)
            _earnings = self.rh_conn.stocks.get_earnings(s)
            earnings_dict[s] = _earnings
        return earnings_dict

    def fetch_transactions(self):
        stock_orders = self.rh_conn.get_all_stock_orders()
        return stock_orders


if __name__ == "__main__":
    import logging
    import json

    logger = logging.getLogger(__name__)
    mfa = input("Enter MFA Code: ")
    rh = RobinhoodConnector(
        config.robinhood["username"], config.robinhood["password"], mfa_code=mfa
    )
    if rh.rh_conn:
        logger.warning(rh.fetch_build_holdings())
    else:
        logger.warning("Login failed")
