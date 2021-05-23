import robin_stocks.robinhood as rh


def fetch_build_holdings(username, password):
    rh.login(username, password)
    my_stocks = rh.build_holdings()
    return my_stocks
