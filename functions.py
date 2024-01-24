import os
import requests
import csv
from datetime import datetime

#kucoin
def get_balance(pair1,pair2,user):

    pair1 = user.get_account_list(currency=pair1, account_type='trade')
    pair2 = user.get_account_list(currency=pair2, account_type='trade')

    balance_1=pair1[0]['balance']
    balance_2=pair2[0]['balance']

    return balance_1, balance_2

def get_price(max_price,min_price,pair,url):
    rex = requests.get(url + '/api/v1/market/orderbook/level1?symbol='+pair, data = { 'data': 'price'} ).json()
    price = float((rex['data']['price']))
    bid = float((rex['data']['bestBid']))
    ask = float((rex['data']['bestAsk']))
    if price >= max_price:
        max_price = price
    if price <= min_price:
        min_price = price
    return price, bid, ask, max_price, min_price

def gate_price():
    # headers = 'Accept': 'application/json', 'Content-Type': 'application/json'
    try:

        query_params = {
            "currency_pair": "ERG_USDT"
        }
        gate_price = requests.get('https://api.gateio.ws/api/v4/spot/tickers/', params=query_params, data = { 'data'} ).json()
        return gate_price

    except Exception as e:
        print("Error connecting to API:", e)



def timestamp():
    timestamp = datetime.utcnow().isoformat(' ', 'seconds')
    return timestamp

# Open the CSV file in append mode

def write_log(type, data, file, pair1, pair2):

    try:
        if type == 'price':
            fieldnames= ["Date", "Coin", "Ku_Price", "Gate_price"]
        if type == 'trade':
            fieldnames = ["Date", "Type", "Pair", "Sell/Buy", "Quantity", "Price", "Total",pair1+"_balance", pair2+"_balance"]

        file_exists = os.path.isfile(file)

        with open(file, mode="a", newline="") as file:
            # Create a CSV writer
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # If the file doesn't exist, write the header row
            if not file_exists:
                writer.writeheader()

            # If the file is empty, write the header row
            if file.tell() == 0:
                writer.writeheader()

            # Append the data to the CSV file
            for row in data:
                writer.writerow(row)

    except FileNotFoundError:
        print(f"The file '{csv_file}' does not exist.")

def read_log(csv_file):


    try:
        # Specify the CSV file name
        csv_file = "trade_log.csv"

        # Initialize a counter for fields with "sale" as a value
        sell_count = 0
        buy_count = 0
        # Open the CSV file and read its content
        with open(csv_file, mode="r") as file:
            reader = csv.reader(file)
            next(reader) # skip header row

            # Iterate through each row in the CSV
            for row in reader:
                # Iterate through each field in the row
                for field in row:
                    # Check if the field contains "sale"
                    if "sell" in field.lower():
                        sell_count += 1
                    if "buy" in field.lower():
                        buy_count += 1
        return buy_count, sell_count

    except FileNotFoundError:
        print(f"The file '{csv_file}' does not exist. Will be created on first trade.")
        return buy_count, sell_count
















