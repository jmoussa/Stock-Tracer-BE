import pyotp
import robin_stocks.robinhood as rh
from stock_tracer.config import config
from logging import getLogger


def fetch_build_holdings(username, password):
    totp = pyotp.TOTP(config.robinhood["mfa_application_identifier"]).now()
    rh.authentication.login(username, password, mfa_code=totp)
    my_stocks = rh.build_holdings()
    return my_stocks
