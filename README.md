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
it checks the cache (for now, in the database) for any request of that stock within the cache time limit
(default set in `config.json`, and editable by the user in the UI).

After the historical data is retrieved the API will format the data as efficiently as possible
so that it can be sent to the front-end in the proper format and graphed.

## Set Up and Run the Server

I've set it up so that you only need to use the `run` script to start.
Be sure to set the S3 environement variables for access

```bash
conda env create -f environment.yml
conda activate stock-tracer 
cp config/config.json.template config/config.json # edit config.json and fill with your values/credentials

./run
```

_For quick API documentation, navigate to `localhost:8000/docs` after starting the server_
