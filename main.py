from fastapi import FastAPI
import database_transactions
import os

app = FastAPI()
DETA_KEY = os.environ.get("DETA")
DETA_NAME_MINING = os.environ.get("WALLET_DB_NAME")
DETA_NAME_PING = os.environ.get("PING_DB_NAME")
DETA_NAME_ALL = os.environ.get("DETA_name_all")


@app.get("/")
async def root():
    return {"message": "nothing to see here"}


@app.get("/mining")
async def mining():
    return database_transactions.mining_data(DETA_KEY, DETA_NAME_MINING)


@app.get("/ping")
async def ping():
    return database_transactions.ping_data(DETA_KEY, DETA_NAME_PING)
