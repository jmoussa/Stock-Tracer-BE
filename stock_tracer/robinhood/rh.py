import pyotp
import robin_stocks.robinhood as rh
from stock_tracer.config import config
from logging import getLogger


class RobinhoodConnector:
    def __init__(self, username, password):
        totp = pyotp.TOTP(config.robinhood["mfa_application_identifier"]).now()
        rh.authentication.login(username, password, mfa_code=totp)
        self.rh_conn = rh

    def fetch_build_holdings(self):
        # totp = pyotp.TOTP(config.robinhood["mfa_application_identifier"]).now()
        # rh.authentication.login(username, password, mfa_code=totp)
        my_stocks = self.rh_conn.build_holdings()
        return my_stocks
