# KuPyBot
# Trading bot for Kucoin API.
# Requirements: Kucoin Python library. 'pip install kucoin-python'
# FlyingPig_69

import time
import functions
from datetime import datetime
from kucoin.client import Trade
from kucoin.client import User


#API Keys. These can be generated on your Kucoin API Management page
api_key = 'key'
api_secret = 'secret'
api_passphrase = 'passphrase'

#configuration
pair1 = "ERG"               # Set pair 1
pair2 = "USDT"              # Set pair 2
first_order = "sell"        # Defines what the first order should be. In this case the first order will SELL pair1. Values: 'buy' or 'sell'
diff_up = 0.03              # After a buy how much, in %s, should the price go up before selling.
diff_down = 0.03            # After a sell how much, in %s, should the price go down before re-buying.
initial_price = 0.95        # Set initial buy/sell price for first order.
shift_price = 0.05          # %s tolerance in price increase before resetting target buy price (NOT sell target!). This is useful in case of large buys where price increases significantly(think infinity bot!)
shift_percentage = 0.025    # %s to shift target price up if shift price is met.
ceiling = 1.50              # Ceiling price. If price goes above this, no more trades will be executed.
floor = 0.91                # Floor price. If price goes below this, no more trades will be executed.
amount = 'MAX'              # How many of pair1 to buy/sell per trade. Add number in ''. Example '10'. If you want to always sell/buy with the entire outstanding balance of pair1 AND pair2 enter 'MAX'. CAUTION: THIS WILL BUY/SELL ENTIRE BALANCE!!!
slippage = 0.99             # If amount is 'MAX' a buy will execute with x% of total pair2 holdings since executing market orders won't always be at current price, it will slip. E.g. if you have 100USDT a 0.98 slippage will buy 98 USDT worth of pair1.
interval = 60               # Time, in seconds, between each price update.
arbitrage = True            # Set to true if you want to sell/buy based on price on another exchange (gate_IO for now). Values : True or False
gate_arb_up = 0.02          # If gateio price is x% higher than kucoin it will purchase immediately, not waiting for target price
gate_arb_down = 0.02        # If gateio price is x% lower than kucoin it will sell immediately, not waiting for target price
log_trades = True           # If True, will log all trades to trade_log.csv. Values: True or False
log_price = True            # If True, will log all prices to price_log.csv . (If interval is 5 seconds, prices will be logged every 5 seconds.. Values: True or False


#-------[No need to change anything below this line]------------------------------------------
# colors
RESET = "\033[0m"  # Reset
RED = "\033[31m"   # Red
GREEN = "\033[32m" # Green
BOLD = "\033[1m"   # Bold
UL = "\033[4m"     # Underline

#initializing values
next_order = first_order
pair = (pair1+"-"+pair2)
no_buys = 0
no_sells = 0
max_price = 0
min_price = 0
url = 'https://api.kucoin.com'

client = Trade(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=False, url=url)
user = User(key=api_key, secret=api_secret, passphrase=api_passphrase, is_sandbox=False, url=url)
balance_1, balance_2 = functions.get_balance(pair1,pair2,user)
startp_1 = balance_1
startp_2 = balance_2
session_start = datetime.now()
price, bid, ask, max_price, min_price = functions.get_price(max_price,min_price,pair,url)
start_price = price # sets the base price for the bot.
startp = start_price
target_price = initial_price
max_price = price
min_price = price

counter= datetime.now()

#start main process
while True:
    try:
        sleeptime = interval
        #fetch latest price and balances
        price, bid, ask, max_price, min_price = functions.get_price(max_price,min_price,pair,url)
        gate_price = float(functions.gate_price()[-1]['last'])
        balance_1, balance_2 = functions.get_balance(pair1,pair2,user)
        balance_1 = float(balance_1)
        balance_2 = round(float(balance_2),2)
        arb_up = (price*(1+gate_arb_up))
        arb_down = (price*(1-gate_arb_down))
        buy_count, sell_count = functions.read_log('trade_log.csv')

        #check if price is below floor or above ceiling. It if set trade status to False. No trades will be done.
        arb = False
        trade = True
        if price >= ceiling:
            trade = False
        if price <= floor:
            trade = False
        #print session info
        print(BOLD +functions.timestamp()," Session duration:", functions.datetime.now()-session_start)
        print("")
        if trade == False:
            print(RED,"TRADING IS PAUSED AS PRICE IS ABOVE OR BELOW CEILING PRICE",RESET)
        print(BOLD,"                        ", pair1,"                        ",pair2,"          Total USDT")
        print(BOLD,"Starting balance:      ", RESET,startp_1,"(",float(startp_1)*float(startp),"USD)                ",startp_2,"       ",(float(startp_1)*float(startp))+float(startp_2))
        print(BOLD,"Current balance:       ", RESET, balance_1,"(",balance_1*price,"USD)             ", RESET, balance_2,"            ",(balance_1*price)+balance_2)
        print("", no_buys, "buys and", no_sells, "sells in current session.", buy_count, "buys and", sell_count, "sells all time")
        print("")
        print(BOLD, "Last Trade / Ask / Bid :                    ", RESET, GREEN, price, RESET, "Ask:", GREEN, ask, RESET, "Bid:", RED, bid, RESET)
        if next_order == 'buy':
            order = ask
            color = GREEN
        if next_order == 'sell':
            order = bid
            color = RED
        print(BOLD, "Current / Target", next_order, "price:                 ",color, bid,"/", round(target_price, 4),RESET)
        if arbitrage == True:
            print(BOLD, "Gate.io (Current/ArbUp/ArbDown/Difference:  ", RESET,gate_price,"/",round(arb_up,4),"/",round(arb_down,4),"/",round(100-(price/gate_price)*100,2),"%")
        print(BOLD, "High/Low current session:                   ",RESET, max_price, "/", min_price)
        print(BOLD, "Profit target per trade cycle:              ", RESET,((diff_up+diff_down)*100),"%   Trade cycle = 1 buy and 1 sell")

        print(BOLD, "Ceiling/Floor price:                        ", RESET, ceiling, "/", RESET, floor)
        print(BOLD, "Bot base price:                             ", RESET,start_price)

        trade_type = 'Standard'

        if trade == True: # only trade if trading is true.
            #if next order is sell
            if next_order == "sell":
                if gate_price <= arb_down:
                    arb = True
                    trade_type = 'Arbitrage'
                if bid >= target_price or arb:
                    arb = False
                    if amount == 'MAX':
                        order_id = client.create_market_order(symbol=pair, side='sell',clientOid='KuBot',size=str(balance_1)) # place market order for entire pair 1 balance
                        size = float(balance_1)
                    elif amount!='MAX':
                        order_id = client.create_market_order(symbol=pair, side='sell', clientOid='KuBot', size=amount)  # place market order for amount in config
                        size = float(amount)
                    if log_trades:  # log trade
                        trade_log = [
                            {"Date": functions.timestamp(), "Type": trade_type, "Pair": pair, "Sell/Buy": "sell", "Quantity": size, "Price": price, "Total": price * size,pair1+"_balance": balance_1, pair2+"_balance": balance_2}
                        ]
                        functions.write_log('trade', trade_log, 'trade_log.csv', pair1, pair2)

                    print("Sell order Placed. ID:", order_id)
                    print("Target price met, executing sale of", size, pair1, "at", price, "Waiting 5 minutes before setting new target buy price")
                    sleeptime=3 # waits 5 minutes for price to settle in case of large trades
                    next_order = "buy"
                    target_price = bid * (1- diff_down) #setting target price for buy order
                    start_price = price
                    no_sells +=1

            #if next order is buy
            if next_order == "buy" or arb:
                print(BOLD,"Shift price:                                ",RESET, round(target_price*(1+shift_price),4),"If price reaches shift price target buy price will increase by", shift_percentage*100,"percent to", round(target_price * (1+shift_percentage),3))
                if ask >= (target_price*(1+shift_price)): # check if price has shifted too much, if so change the target to be
                    target_price = target_price * (1+shift_percentage)
                    print("Price shifted to new target", target_price,"Base price is now",price)
                    start_price = price
                    print(log_trades)
                if next_order == "buy":
                    if gate_price >= arb_up:
                        arb = True
                        trade_type = 'Arbitrage'
                if price <= target_price or arb:
                    arb = False
                    if amount == 'MAX':
                        balance_2 = round((balance_2 * slippage),4)
                        order_id = client.create_market_order(symbol=pair, side='buy',clientOid='KuBot', funds=balance_2)  # place market order for entire pair 2 balance
                        size=float(balance_2)
                        if log_trades:  # log trade
                            trade_log = [
                                {"Date": functions.timestamp(), "Type": trade_type, "Pair": pair, "Sell/Buy": "buy", "Quantity": size, "Price": price, "Total": price * size,pair1 + "_balance": balance_1, pair2 + "_balance": balance_2}
                            ]
                            functions.write_log('trade', trade_log, 'trade_log.csv', pair1, pair2)
                    elif amount != 'MAX':
                        order_id = client.create_market_order(symbol=pair, side='buy', clientOid='KuBot', size=amount)  # place market order for amount in config
                        size = float(amount)
                        if log_trades: # log trade
                            trade_log = [
                                {"Date": functions.timestamp(),"Type": trade_type, "Pair": pair, "Sell/Buy": "buy", "Quantity": size, "Price": price, "Total": price * size, pair1 + "_balance": balance_1, pair2 + "_balance": balance_2}
                            ]
                            functions.write_log('trade', trade_log, 'trade_log.csv',pair1,pair2)
                    print("Buy order Placed. ID:", order_id)
                    start_price = price
                    target_price = bid * (1+diff_up)  # setting new target price
                    next_order = "sell"
                    no_buys +=1

        # Write price_log
        if log_price == True:
            price_log = [
                {"Date": functions.timestamp(), "Coin": pair1, "Ku_Price": price, "Gate_price": gate_price}
            ]
            functions.write_log('price', price_log, 'price_log.csv', pair1, pair2)

    except Exception as e:
        print(f"Error: {e}")
    print("--------------------------------------------------------------------------------")
    time.sleep(sleeptime)


