FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7 

COPY . /app

RUN cd /app && \
  python setup.py develop

WORKDIR /app/stock_tracer
RUN cd /app/stock_tracer

EXPOSE 80
EXPOSE 8000

ENTRYPOINT ["./run"]
