import pyotp
import logging
import robin_stocks.robinhood as rh
from stock_tracer.config import config
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(10)


class RobinhoodConnector:
    def __init__(self, username, password, mfa_code=""):
        self.username = username
        self.build_holdings = None
        self.rh_conn = None
        try:
            if mfa_code == "" or mfa_code is None:
                mfa_code = pyotp.TOTP(config.robinhood["mfa_application_identifier"]).now()

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

    def fetch_historicals(
        self, symbols: str or list = None, time_period: str = "ytd", aggregation="Close",
    ):
        """
        Returns a dictionary mapping each ticker (in the user's holdings) to a
        pandas dataframe-interpreted dictionary of the stock's historical data
        """
        logger.info("Logged Into Robinhood")

        # Fetch build holding symbols/tickers
        if symbols is None:
            if self.build_holdings is None:
                self.build_holdings = self.fetch_build_holdings()

            symbols = [x.replace(".", "-") for x in list(self.build_holdings.keys())]

        # Fetch historical data from yfinance
        #   could also get from robinhood, but yfinance is faster and more accurate
        response = yf.Tickers(" ".join(symbols))

        # fetch_instrument_to_stock_map()
        rh_instruments = self.rh_conn.stocks.get_instruments_by_symbols(symbols)
        instrument_id_to_symbol = {}
        for instrument_data in rh_instruments:
            instrument_id_to_symbol[instrument_data["id"]] = instrument_data["symbol"]

        tickers = response.tickers
        historical_data = {}
        macd_data = {}
        for ticker, ticker_obj in tickers.items():
            df = None
            try:
                df = ticker_obj.history(period=time_period)
            except Exception:
                try:
                    df = ticker_obj.history(period="ytd")
                except Exception as e:
                    logger.error(f"{e.__class__.__name__}: {e}")
                    logger.error(f"No historical data found for {ticker}")

            if df is not None and not df.empty:
                logger.info(f"Historical DF ================== \n{df}")
                macd_d3_data = self.generate_macd(df, aggregation)
                df.index = df.index.map(str)
                ticker_historicals = df.to_dict("index")
                historical_data[ticker.replace("-", ".")] = ticker_historicals
                macd_data[ticker.replace("-", ".")] = macd_d3_data
            else:
                logger.info(f"Skipping {ticker} historical data")

        return historical_data, macd_data, instrument_id_to_symbol

    def fetch_earnings(self):
        if self.build_holdings is None:
            symbols = list(self.rh_conn.build_holdings().keys())
        else:
            symbols = list(self.build_holdings.keys())

        earnings_dict = {}
        for s in symbols:
            _earnings = self.rh_conn.stocks.get_earnings(s)
            earnings_dict[s] = _earnings
        return earnings_dict

    def fetch_dividends(self):
        dividends = self.rh_conn.get_dividends()
        return dividends

    def fetch_transactions(self):
        stock_orders = self.rh_conn.get_all_stock_orders()
        return stock_orders

    @staticmethod
    def generate_macd(df, aggregation):
        """
        Returns MACD, Signal line dataframes
        :param df: time indexed ticker df with ohlc columns
        :param aggregataion: ohlc to use

        Returns:
            Pandas DF->dictionary object formatted for D3 data
        """
        df = df[[aggregation]]
        df.reset_index(inplace=True)
        df.columns = ["ds", "y"]
        logger.info(f"MACD PRIME DF\n{df}")
        # MACD Calculation
        exp1 = df.y.ewm(span=12, adjust=False).mean()
        exp2 = df.y.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()

        d = {"date": df.ds, "macd": macd, "signal": signal}
        _df = pd.DataFrame(data=d)
        logger.info(f"FINAL MACD DF\n{_df}")
        # _df.reset_index(inplace=True)
        final_dictionary = _df.to_dict("records")
        return final_dictionary


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)

    """
    mfa = input("Enter MFA Code: ")
    rh = RobinhoodConnector(
        config.robinhood["username"], config.robinhood["password"], mfa_code=mfa
    )
    if rh.rh_conn:
        logger.warning(rh.fetch_build_holdings())
    else:
        logger.warning("Login failed")
    """
