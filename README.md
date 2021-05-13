# Stock Tracer Backend

This is the backend API for the [Stock Tracer Web App](www.github.com/jmoussa/stock-tracer-fe).
This API handles 
- Fetching/Caching historical stock data from `yfinance`
- Authentication
- User Account 
- User's Explicit Financial Profiling (stored safely)

## Requirements

- Anaconda (for Python environemnt management)
- Python FastAPI (included in the Anaconda environment) [docs](https://fastapi.tiangolo.com/)
- PostgreSQL database [docs](https://www.postgresql.org/docs/13/index.html)

## Architecture

The API caches each call it does, and before the next call is made,
it checks the database for any request of that stock within the caching time limit
(default set in `config.json`, and editable by the user in the UI).

After the historical data is retrieved (whether from the database or yfinance) the API will format the data
so that it can be sent to the front-end in the proper format and graphed.

## Set Up and Run the Server

I've set it up so that you only need to use the `run` script to start.
Be sure to set the S3 environement variables for access.

In the root directory of the repository:

```bash
conda env create -f environment.yml
conda activate stock-tracer 
cd stock_tracer
cp config/config.json.template config/config.json # edit config.json and fill with your values/credentials for the postgresql database

./run
```

_For quick API documentation, navigate to `localhost:8000/docs` after starting the server_
