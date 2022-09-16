from time import sleep
from binance.client import Client
import keys
import pandas as pd
import telebot
bot = telebot.TeleBot(token='5522804791:AAGody6ry_cWIx0uc9p9wHVnIs0j7XkwbqY')
client = Client(keys.api_key, keys.api_secret)

lastcoin = ""
lastcoff = 0
while(True):
    max_coff = 0
    max_coff_coin = ""
    btclist = ""
    usdtlist = ""
    btclist1 = ""
    usdtlist1 = ""
    validcoins = []
    all_tickers = pd.DataFrame(client.get_ticker())

    usdt = all_tickers[all_tickers.symbol.str.contains('USDT')]
    usdt = usdt[~((usdt.symbol.str.contains('UP')) |
                (usdt.symbol.str.contains('DOWN')))]
    btc = all_tickers[all_tickers.symbol.str.contains('BTC')]
    btc = btc[~((btc.symbol.str.contains('UP')) |
                (btc.symbol.str.contains('DOWN')))]

    for index, row in usdt.iterrows():
        usdtlist += str(row['symbol'])
        usdtlist += " "
    for index, row in btc.iterrows():
        btclist += str(row['symbol'])
        btclist += " "

    usdtlist1 = usdtlist.split()
    btclist1 = btclist.split()

    for coinusdt in usdtlist1:
        coinbtc = coinusdt.replace("USDT", "BTC")
        coin = coinusdt.replace("USDT", "")
        if coinbtc in btclist1:
            validcoins.append(coin)

    for coin in validcoins:
        bitcoin = all_tickers[all_tickers.symbol.str.contains('BTCUSDT')]
        searchusdt = coin+"USDT"
        coin_in_usdt = all_tickers[all_tickers.symbol.str.contains(searchusdt)]
        searchbtc = coin+"BTC"
        coin_in_btc = all_tickers[all_tickers.symbol.str.contains(searchbtc)]
        price_in_btc = ""
        price_in_usdt = ""
        bitcoin_price = ""
        for index, row in bitcoin.iterrows():
            bitcoin_price += str(row['lastPrice'])
        for index, row in coin_in_usdt.iterrows():
            price_in_usdt += str(row['lastPrice'])
        for index, row in coin_in_btc.iterrows():
            price_in_btc += str(row['lastPrice'])
        try:
            if(float(price_in_usdt) != 0):
                coff = 1/float(price_in_usdt)*float(price_in_btc) * \
                    float(bitcoin_price)
                if(coff > max_coff):
                    max_coff = coff
                    max_coff_coin = coin
                    max_coff_coin_price_in_usdt = price_in_usdt
                    max_coff_coin_price_in_btc = price_in_btc

        except:
            pass

    print(max_coff_coin)
    print(max_coff)
    print(max_coff_coin_price_in_usdt)
    print(max_coff_coin_price_in_btc)
    print(bitcoin_price)
    if(max_coff > 1.02):
        if(lastcoin != max_coff_coin):
            bot.send_message(
                -1001558563045, f"COIN:{max_coff_coin}\nCOFF:{round((max_coff-1)*100,2)}%\nPRICE IN USDT:{max_coff_coin_price_in_usdt}\nPRICE IN BTC:{max_coff_coin_price_in_btc}")
        elif(lastcoff < round(max_coff, 2)):
            bot.send_message(
                -1001558563045, f"COIN:{max_coff_coin}\nCOFF:{round((max_coff-1)*100,2)}%\nPRICE IN USDT:{max_coff_coin_price_in_usdt}\nPRICE IN BTC:{max_coff_coin_price_in_btc}\nBITCOIN PRICE:{bitcoin_price}")
    lastcoin = max_coff_coin
    lastcoff = round(max_coff, 2)
    print(lastcoff)
    sleep(10)

    if(round((max_coff-1)*100, 2) > 4):
        qty = round(12/float(max_coff_coin_price_in_usdt), 2)
        if(qty > 10):
            qty = int(qty)
        print(f"qty {qty}")
        order = client.create_order(symbol=f"{max_coff_coin}USDT",
                                    side='BUY', type='MARKET', quantity=qty)
        print(order['fills'][0]['commission'])

        qty1 = qty-1-float(order['fills'][0]
                           ['commission'])
        qty3 = round(qty1*max_coff_coin_price_in_btc, 6)
        if(qty1 > 10):
            qty1 = int(qty1)
        print(f"qty1 {qty1}")
        print(f"qty3 {qty3}")

        order = client.create_order(symbol=f"{max_coff_coin}BTC",
                                    side='SELL', type='MARKET', quantity=qty1)

        order = client.create_order(symbol=f"BTCUSDT",
                                    side='SELL', type='MARKET', quantity=qty3)
