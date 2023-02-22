
import time
import json
import requests
import random
from datetime import datetime, timedelta
import configparser
import mysql.connector
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient
from telethon import functions
from telegram.ext import Updater, CommandHandler

url = "https://api.defined.fi"
definet_lv = "ev1g4sXv2b4HR6XC9x4bw4IKP5zUj6av3QhrOWJz"
definet_vd = "yNk1v01YDP3Glmq5xGEiY8BBIhEt1y261KTwSwHv"
definet_apis = [definet_lv, definet_vd]

updater = Updater(token='5649973136:AAH2izrLwVsIvyL5fyPrSIUM9lPzNHwm06M', use_context=True)

def getDefinedPairEvent(PAIR_ADDRESS):
    headers_define = {
        "accept": "application/json",
        "x-api-key": f"{random.choice(definet_apis)}"
    }

    getTokenEvents = """query FilterPairsQuery($token_pair: String) 
        { filterPairs(phrase: $token_pair rankings: { attribute: liquidity, direction: DESC } ) 
            {count offset results 
                { buyCount5m buyCount1 buyCount4 buyCount12 buyCount24 sellCount5m sellCount1 sellCount4 sellCount12 sellCount24 txnCount5m txnCount1 txnCount4 txnCount12 txnCount24 highPrice5m highPrice1 highPrice4 highPrice12 highPrice24 lowPrice5m lowPrice1 lowPrice4 lowPrice12 lowPrice24 priceChange5m priceChange1 priceChange4 priceChange12 priceChange24 volumeUSD5m volumeUSD1 volumeUSD4 volumeUSD12 volumeUSD24 price marketCap liquidity liquidityToken exchange 
                    { address iconUrl id name networkId tradeUrl } 
                        pair { address exchangeHash fee id networkId tickSpacing token0 token1 } 
                            token0 { address cmcId decimals id name networkId symbol totalSupply } 
                                token1 { address cmcId decimals id name networkId symbol totalSupply } } } }"""
    
    variables = {"token_pair": str(PAIR_ADDRESS).lower()} 

    response_tokenEvent = requests.post(url, headers=headers_define, json={"query": getTokenEvents, "variables": variables }) 

    try:
        response_result_filterPair =  json.loads(response_tokenEvent.text)['data']['filterPairs']['results'][0]

        LP = int(response_result_filterPair['liquidity'])
        MKT_CAP = round(float(response_result_filterPair['marketCap']), 2)
        VOL_1H = int(response_result_filterPair['volumeUSD1'])
        VOL_4H = int(response_result_filterPair['volumeUSD4'])
        VOL_12H = int(response_result_filterPair['volumeUSD12'])
        VOL_24H = int(response_result_filterPair['volumeUSD24'])
        TXNS_TXNS_1H = int(response_result_filterPair['txnCount1'])
        TXNS_TXNS_4H = int(response_result_filterPair['txnCount4'])
        TXNS_TXNS_12H = int(response_result_filterPair['txnCount12'])
        TXNS_TXNS_24H = int(response_result_filterPair['txnCount24'])
        TXNS_SELLS_1H = int(response_result_filterPair['sellCount1'])
        TXNS_SELLS_4H = int(response_result_filterPair['sellCount4'])
        TXNS_SELLS_12H = int(response_result_filterPair['sellCount12'])
        TXNS_SELLS_24H = int(response_result_filterPair['sellCount24'])
        TXNS_BUYS_1H = int(response_result_filterPair['buyCount1'])
        TXNS_BUYS_4H = int(response_result_filterPair['buyCount4'])
        TXNS_BUYS_12H = int(response_result_filterPair['buyCount4'])
        TXNS_BUYS_24H = int(response_result_filterPair['buyCount24'])
        
        if LP < 50:
            RUG = True
            LP = 0
        else:
            RUG = False
    except:
        LP = ""
        MKT_CAP = ""
        VOL_1H = ""
        VOL_4H = ""
        VOL_12H = ""
        VOL_24H = ""
        TXNS_TXNS_1H = ""
        TXNS_TXNS_4H = ""
        TXNS_TXNS_12H = ""
        TXNS_TXNS_24H = ""
        TXNS_SELLS_1H = ""
        TXNS_SELLS_4H = ""
        TXNS_SELLS_12H = ""
        TXNS_SELLS_24H = ""
        TXNS_BUYS_1H = ""
        TXNS_BUYS_4H = ""
        TXNS_BUYS_12H = ""
        TXNS_BUYS_24H = ""
        RUG = True

    return LP, MKT_CAP, VOL_1H, VOL_4H, VOL_12H, VOL_24H, TXNS_TXNS_1H, TXNS_TXNS_4H, TXNS_TXNS_12H, TXNS_TXNS_24H, TXNS_SELLS_1H, TXNS_SELLS_4H, TXNS_SELLS_12H, TXNS_SELLS_24H, TXNS_BUYS_1H, TXNS_BUYS_4H, TXNS_BUYS_12H, TXNS_BUYS_24H, RUG

def sqlInsertAllTokenData(time, token_address, pair_address, token_name, token_symbol, token_supply, creator_address, creator_eth_balance, token_url, dexcreener, ID, LP, MKT_CAP, VOL_1H, VOL_4H, VOL_12H, VOL_24H, TXNS_TXNS_1H, TXNS_TXNS_4H, TXNS_TXNS_12H, TXNS_TXNS_24H, TXNS_SELLS_1H, TXNS_SELLS_4H, TXNS_SELLS_12H, TXNS_SELLS_24H, TXNS_BUYS_1H, TXNS_BUYS_4H, TXNS_BUYS_12H, TXNS_BUYS_24H, RUG):
    # Connect to the database
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    # Create a cursor object
    cursor = cnx.cursor()
    # Insert data into the "table_name" table
    query = "INSERT INTO all_data_tokens (time, token_address, pair_address, token_name, token_symbol, token_supply, creator_address, creator_eth_balance, token_url, dexcreener, ID, LP, MKT_CAP, hour1, hour4, hour12, day1, TXNS_TXNS_1H, TXNS_TXNS_4H, TXNS_TXNS_12H, TXNS_TXNS_24H, TXNS_SELLS_1H, TXNS_SELLS_4H, TXNS_SELLS_12H, TXNS_SELLS_24H, TXNS_BUYS_1H, TXNS_BUYS_4H, TXNS_BUYS_12H, TXNS_BUYS_24H, RUG) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE ID = %s"
    
    data = (time, token_address, pair_address, token_name, token_symbol, token_supply, creator_address, creator_eth_balance, token_url, dexcreener, ID, LP, MKT_CAP, VOL_1H, VOL_4H, VOL_12H, VOL_24H, TXNS_TXNS_1H, TXNS_TXNS_4H, TXNS_TXNS_12H, TXNS_TXNS_24H, TXNS_SELLS_1H, TXNS_SELLS_4H, TXNS_SELLS_12H, TXNS_SELLS_24H, TXNS_BUYS_1H, TXNS_BUYS_4H, TXNS_BUYS_12H, TXNS_BUYS_24H, RUG, ID)
    cursor.execute(query, data)
    # Commit the transaction
    cnx.commit()
    print(f'{token_name} | {time} -- inserted on DB.all_data_tokens')
    # Close the cursor and connection
    cursor.close()
    cnx.close()

def mysqlConnectorTrendingTokens(token_name, deploy_time, token_symbol, creator_address, creator_eth_address, hour1, change_hour1, previousValue_hour1, hour4, change_hour4, previousValue_hour4, hour12, change_hour12, previousValue_hour12, day1, change_day1, previousValue_day1, buy_tax, sell_tax, token_address, pair_address, lp, txns, txns_less_5_mins, buys, sells, token_url, dexcreener, dextools):
    # Connect to the database
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    # Create a cursor object
    cursor = cnx.cursor()
    # Insert data into the "table_name" table
    query = "INSERT INTO trending_tokens (TOKEN_NAME, DEPLOY_TIME, SYMBOL, CREATOR_ADDRESS, CREATOR_ETH_BALANCE, hour1, change_hour1, previousValue_hour1, hour4, change_hour4, previousValue_hour4, hour12, change_hour12, previousValue_hour12, day1, change_day1, previousValue_day1, buy_tax, sell_tax, token_address, pair_address, lp, txns, txns_less_5_mins, buys, sells, token_url, dexcreener, dextools) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE TOKEN_NAME = %s"
    
    data = (token_name,  deploy_time, token_symbol, creator_address, creator_eth_address, hour1, change_hour1, previousValue_hour1, hour4, change_hour4, previousValue_hour4, hour12, change_hour12, previousValue_hour12, day1, change_day1, previousValue_day1, buy_tax, sell_tax, token_address, pair_address, lp, int(txns), int(txns_less_5_mins), int(buys), int(sells), token_url, dexcreener, dextools, token_name)
    cursor.execute(query, data)
    # Commit the transaction
    cnx.commit()
    print(f'{token_name} | {day1} was inserted into the DB.trending_tokens')
    # Close the cursor and connection
    cursor.close()
    cnx.close()

def sqlConnectorInsertPostTelegramTokenInfo(time, token_address, pair_address, token_name, token_symbol, token_supply, creator_address, creator_eth_balance, token_url, dexcreener, lp, txns, buys, sells, rug):
    # Connect to the database
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    # Create a cursor object
    cursor = cnx.cursor()
    # Insert data into the "table_name" table
    query = "INSERT INTO post_telegram_token_info (time, token_address, pair_address, token_name, token_symbol, token_supply, creator_address, creator_eth_balance, token_url, dexcreener, lp, txns, buys, sells, rug) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE token_address = %s"
    
    data = (time, token_address, pair_address, token_name, token_symbol, token_supply, creator_address, creator_eth_balance, token_url, dexcreener, lp, txns, buys, sells, rug, token_address)
    cursor.execute(query, data)
    # Commit the transaction
    cnx.commit()
    print(f'{token_name} | {pair_address} was inserted into the DB.post_telegram_token_info')
    # Close the cursor and connection
    cursor.close()
    cnx.close()

def sqlConnectorExtractAllDataTokens(filtered_date):
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    cursor = cnx.cursor(dictionary=True)

    query = f"""SELECT token_address FROM all_data_tokens WHERE time like '%{filtered_date}%' and LP = 0"""
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    return result

def sqlConnectorExtractNewPairs(table_name, filtered_date):
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    cursor = cnx.cursor(dictionary=True)

    query = f"SELECT * FROM {table_name} where launch_date like '%{filtered_date}%' ORDER BY launch_date DESC"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()

    return result

def sqlConnectorExtractPostTelegramTokenInfo(table_name):
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    cursor = cnx.cursor(dictionary=True)

    query = f"SELECT * FROM {table_name}"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    cnx.close()

    return result

def sqlUpdatePostTelegramTokenInfo(table_name):
    # Connect to the database
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    # Create a cursor object
    cursor = cnx.cursor()
    # Delete all rows from the table
    query = "DELETE FROM %s" % (table_name,)
    cursor.execute(query)
    # Commit the transaction
    cnx.commit()
    print("All rows from table %s were deleted." % (table_name,))
    print(f"Loop started at: {datetime.now().strftime('%d/%m/%Y %H:%M:00')}")
    # Close the cursor and connection
    cursor.close()
    cnx.close()

def sqlUpdateTrendingTokens(table_name):
    # Connect to the database
    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )
    # Create a cursor object
    cursor = cnx.cursor()
    # Delete all rows from the table
    query = "DELETE FROM %s" % (table_name,)
    cursor.execute(query)
    # Commit the transaction
    cnx.commit()
    print("All rows from table %s were deleted." % (table_name,))
    # Close the cursor and connection
    cursor.close()
    cnx.close()

def sqlInsertTax(buy_tax, sell_tax, txns_less_5_mins, hour1, change_hour1, previousValue_hour1, hour4, change_hour4, previousValue_hour4, hour12, change_hour12, previousValue_hour12, day1, change_day1, previousValue_day1, token_address):

    cnx = mysql.connector.connect(
        host='sql8.freesqldatabase.com',
        user='sql8593502',
        password='tuz9qrT3jT',
        database='sql8593502',
        port=3306
    )

    # Create a cursor object
    cursor = cnx.cursor()
    # Delete all rows from the table
    query = """UPDATE post_telegram_token_info
                SET buy_tax = %s, sell_tax = %s, txn_less_5_mins = %s, hour1 = %s, change_hour1 = %s, previousValue_hour1 = %s, hour4 = %s, change_hour4 = %s, previousValue_hour4 = %s, hour12 = %s, change_hour12 = %s, previousValue_hour12 = %s, day1 = %s, change_day1 = %s, previousValue_day1 = %s
                WHERE token_address = %s;"""

    data = (buy_tax, sell_tax, txns_less_5_mins, hour1, change_hour1, previousValue_hour1, hour4, change_hour4, previousValue_hour4, hour12, change_hour12, previousValue_hour12, day1, change_day1, previousValue_day1, token_address)

    cursor.execute(query, data)
    # Commit the transaction
    cnx.commit()
    print(f"{buy_tax} inserted in {token_address}")
    # Close the cursor and connection
    cursor.close()
    cnx.close()

def readJson():
    data = sqlConnectorExtractNewPairs("pair_created_real_time", datetime.now().strftime("%d/%m/%Y"))

    for token in data:
        LP, MKT_CAP, VOL_1H, VOL_4H, VOL_12H, VOL_24H, TXNS_TXNS_1H, TXNS_TXNS_4H, TXNS_TXNS_12H, TXNS_TXNS_24H, TXNS_SELLS_1H, TXNS_SELLS_4H, TXNS_SELLS_12H, TXNS_SELLS_24H, TXNS_BUYS_1H, TXNS_BUYS_4H, TXNS_BUYS_12H, TXNS_BUYS_24H, RUG = getDefinedPairEvent(token['pair_address'])
        sqlConnectorInsertPostTelegramTokenInfo(
            token['launch_date'], 
            token['token_address'],
            token['pair_address'],
            token['token_name'],
            token['token_symbol'],
            token['token_supply'],
            token['creator_address'],
            token['creator_eth_balance'],
            token['token_url'],
            token['dexcreener'],
            LP,
            TXNS_TXNS_24H,
            TXNS_BUYS_24H,
            TXNS_SELLS_24H,
            RUG
            )
        sqlInsertAllTokenData(
            datetime.now().strftime("%d/%m/%Y %H:%M:00"), 
            token['token_address'],
            token['pair_address'],
            token['token_name'],
            token['token_symbol'],
            token['token_supply'],
            token['creator_address'],
            token['creator_eth_balance'],
            token['token_url'],
            token['dexcreener'],
            str(f"{token['token_name']} {VOL_24H}"),
            LP,
            MKT_CAP,
            VOL_1H,
            VOL_4H,
            VOL_12H,
            VOL_24H,
            TXNS_TXNS_1H,
            TXNS_TXNS_4H,
            TXNS_TXNS_12H,
            TXNS_TXNS_24H,
            TXNS_SELLS_1H,
            TXNS_SELLS_4H,
            TXNS_SELLS_12H,
            TXNS_SELLS_24H,
            TXNS_BUYS_1H,
            TXNS_BUYS_4H,
            TXNS_BUYS_12H,
            TXNS_BUYS_24H,
            RUG
        )
        

def getDefinedTokenEvents(token_pair):
    headers_define = {
        "accept": "application/json",
        "x-api-key": f"{random.choice(definet_apis)}"
    }
    getTokenEvents = """{getTokenEvents(query: {address: "%s", networkId: 1}, limit:500) 
            {
                items {
                address
                baseTokenPrice
                blockHash
                blockNumber
                eventType
                id
                liquidityToken
                logIndex
                maker
                networkId
                timestamp
                token0SwapValueUsd
                token1SwapValueUsd
                token0ValueBase
                token1ValueBase
                transactionHash
                transactionIndex
                eventDisplayType
                }
                cursor
            }
        }""" % (token_pair,)
    
    response_tokenEvent = requests.post(url, headers=headers_define, json={'query':getTokenEvents }) 
    json_response_tokenEvent = json.loads(response_tokenEvent.text)['data']['getTokenEvents']['items']

    return json_response_tokenEvent

def getDefinedDetailedPairStats(token_pair):
    volume_values = {
        "hour1": int,
        "change_hour1": float,
        "previousValue_hour1": int,
        "hour4": int,
        "change_hour4": float,
        "previousValue_hour4": int,
        "hour12": int,
        "change_hour12": float,
        "previousValue_hour12": int,
        "day1": int,
        "change_day1": float,
        "previousValue_day1": int
    }

    for volume_type in ['hour1', 'hour4', 'hour12', 'day1']:
        headers_define = {
            "accept": "application/json",
            "x-api-key": f"{random.choice(definet_apis)}"
        }
        getDetailedPairStats = {"query": 
            """{getDetailedPairStats(pairAddress: "%s", networkId: 1, durations: %s, bucketCount: 1) 
                {
                    networkId
                    pairAddress
                    stats_%s {
                    duration
                    end
                    start
                    statsNonCurrency {
                        buyers {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        buys {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        sellers {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        sells {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        traders {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        transactions {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                    }
                    statsUsd {
                        buyVolume {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        close {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        highest {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        lowest {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        open {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        sellVolume {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                        volume {
                        buckets
                        change
                        currentValue
                        previousValue
                        }
                    }
                    timestamps {
                        end
                        start
                    }
                    
                }
                }
            }""" % (token_pair, volume_type, volume_type)
        }

        response_DetailedPairStats = requests.post(url, headers=headers_define, json=getDetailedPairStats) 

        json_response_volume = json.loads(response_DetailedPairStats.text)['data']['getDetailedPairStats'][f'stats_{volume_type}']['statsUsd']['volume']['currentValue']
        json_response_volume_variation = json.loads(response_DetailedPairStats.text)['data']['getDetailedPairStats'][f'stats_{volume_type}']['statsUsd']['volume']['change']
        json_response_volume_previous = json.loads(response_DetailedPairStats.text)['data']['getDetailedPairStats'][f'stats_{volume_type}']['statsUsd']['volume']['previousValue']
        volume_values[f'{volume_type}'] = int(json_response_volume)
        volume_values[f'change_{volume_type}'] = float(json_response_volume_variation)
        volume_values[f'previousValue_{volume_type}'] = int(json_response_volume_previous)

    return volume_values

def make_request_honeypot(querystring):
    url = "https://honeypotapi.p.rapidapi.com/api/v1/scan/"

    headers = {
        "X-RapidAPI-Key": "1851244663msh3f44cb93899cadep17b4cdjsne05a1f5c7894",
        "X-RapidAPI-Host": "honeypotapi.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response

uniswapV2 = {
    "name":"Uniswap v2",
    "factory_address":"0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
    "router_address":"0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
}

uniswapV3 = {
    "name":"Uniswap v3",
    "factory_address":"0x1F98431c8aD98523631AE4a59f267346ea31F984",
    "router_address":"0xE592427A0AEce92De3Edee1F18E0157C05861564"
}
def send_tg_message(update, context):
    original_message = context.bot.send_message(chat_id=update.message.chat_id, text="Generating List...", parse_mode = "Markdown", disable_web_page_preview=True)
    original_message_id = original_message.message_id

    sqlUpdatePostTelegramTokenInfo("post_telegram_token_info")
    
    while True:
        readJson()
        data = sqlConnectorExtractPostTelegramTokenInfo("post_telegram_token_info")

        dextools_url = "https://www.dextools.io/app/es/ether/pair-explorer/"
        
        list_test = []
        list_volume_day1 = []
        list_volume_hour1 = []
        list_volume_hour4 = []
        list_volume_hour12 = []
        counter_honeypotrequests = 0
        for token in data:
            
            if token['rug'] == 0:
                if datetime.now().strftime("%d/%m/%Y") == datetime.strptime(token['time'], "%d/%m/%Y %H:%M:%S").strftime("%d/%m/%Y"):
                    if token['txns'] != '':                
                        json_response_tokenEvent = getDefinedTokenEvents(token['pair_address'])

                        all_transactions = []
                        open_trading_time = None
                        for json_transaction in json_response_tokenEvent:
                            json_transaction['timestamp'] = datetime.fromtimestamp(json_transaction['timestamp'])
                            
                            if json_transaction['eventDisplayType'] == 'Mint':
                                open_trading_time = json_transaction['timestamp']
                                
                            elif json_transaction['eventDisplayType'] == 'Buy' or json_transaction['eventDisplayType'] == 'Sell':
                                all_transactions.append(json_transaction['timestamp'])
                        try:     
                            open_trading_time = all_transactions[-1]
                            transactions = []

                            for transaction in all_transactions:
                                restant_time = abs(transaction - open_trading_time)
                                if restant_time < timedelta(minutes=5):
                                    transactions.append(restant_time)
                            
                            txns_less_5_mins = len(transactions)
                        except:
                            txns_less_5_mins = None

                        data_from_allTokens = sqlConnectorExtractAllDataTokens(datetime.now().strftime("%d/%m/%Y"))
                        
                        if any(token['token_address'] == item['token_address'] for item in data_from_allTokens):
                            print(f"{token['token_address']} entered")
                            try: 
                                querystring = {"factory_address": uniswapV2["factory_address"], "token_b":"0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2","chain":"eth","exchange":"Uniswap v3","token_a":token['token_address'],"router_address": uniswapV2["router_address"]}

                                response = make_request_honeypot(querystring)
                                buy_tax = str(response.json()['buy_tax'])
                                sell_tax = str(response.json()['sell_tax'])
                                error = response.json()['error']
                                isHoneypot = False
                            except:
                                if response.status_code == 200:
                                    querystring = {"factory_address": uniswapV3["factory_address"], "token_b":"0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2","chain":"eth","exchange":"Uniswap v3","token_a":token['token_address'],"router_address": uniswapV3["router_address"]}
                                    response = make_request_honeypot(querystring)
                                    buy_tax = str(response.json()['buy_tax'])
                                    sell_tax = str(response.json()['sell_tax'])
                                    error = response.json()['error']
                                    isHoneypot = False
                                else:
                                    buy_tax = 'Tax -'
                                    sell_tax = 'Tax -'
                                    error = ''
                                    isHoneypot = True

                            try:
                                if "TRANSFER_FAILED" in error:
                                    buy_tax = "HP❌"
                                    sell_tax = "HP❌"
                                    isHoneypot = True
                                elif "INSUFFICIENT_LIQUIDITY" in error:
                                    buy_tax = "-"
                                    sell_tax = "-"

                                elif "SEVERE_FEE" in error:
                                    buy_tax = "HP❌"
                                    sell_tax = "HP❌"
                                    isHoneypot = True
                            except:
                                buy_tax = '-'
                                sell_tax = '-'
                            
                            counter_honeypotrequests += 1
                        else:
                            print(f"{token['token_address']} NONONONONONOOT entered")
                            buy_tax = "-"
                            sell_tax = "-"
                            isHoneypot = True
                            
                        json_response_DetailedPairStats = getDefinedDetailedPairStats(token['pair_address'])
                        sqlInsertTax(buy_tax, sell_tax, txns_less_5_mins, json_response_DetailedPairStats['hour1'],
                                                json_response_DetailedPairStats['change_hour1'],
                                                json_response_DetailedPairStats['previousValue_hour1'],
                                                json_response_DetailedPairStats['hour4'],
                                                json_response_DetailedPairStats['change_hour4'],
                                                json_response_DetailedPairStats['previousValue_hour4'],
                                                json_response_DetailedPairStats['hour12'],
                                                json_response_DetailedPairStats['change_hour12'],
                                                json_response_DetailedPairStats['previousValue_hour12'],
                                                json_response_DetailedPairStats['day1'],
                                                json_response_DetailedPairStats['change_day1'],
                                                json_response_DetailedPairStats['previousValue_day1'], token['token_address'])
                        if not isHoneypot:
                            if json_response_DetailedPairStats['day1'] != 0:
                                
                                # list_test.append(f"{token['rug']}**[{token['token_name']}]**({dextools_url}{token['pair_address']})" + "|" + f"**[{token['token_symbol']}]**({token['dexcreener']})"
                                #     + '\n' + 
                                #     f"**🔖Buy {buy_tax} & Sell {sell_tax}**" 
                                #     + '\n' + 
                                #     f"💰**LP**: {token['lp']}" + '|' + f"**VOL**: {json_response_DetailedPairStats['day1']}" + '|' + f"**TXNS**: {token['txns']}"
                                #     + '\n' + 
                                #     f"**🔥TXNS <5mins: {txns_less_5_mins}**" + '\n' + '\n')
                                                                
                                # insertTrending(trending_info)
                                mysqlConnectorTrendingTokens(
                                                token['token_name'],
                                                token['time'], 
                                                token['token_symbol'],
                                                token['creator_address'],
                                                token['creator_eth_balance'],
                                                json_response_DetailedPairStats['hour1'],
                                                json_response_DetailedPairStats['change_hour1'],
                                                json_response_DetailedPairStats['previousValue_hour1'],
                                                json_response_DetailedPairStats['hour4'],
                                                json_response_DetailedPairStats['change_hour4'],
                                                json_response_DetailedPairStats['previousValue_hour4'],
                                                json_response_DetailedPairStats['hour12'],
                                                json_response_DetailedPairStats['change_hour12'],
                                                json_response_DetailedPairStats['previousValue_hour12'],
                                                json_response_DetailedPairStats['day1'],
                                                json_response_DetailedPairStats['change_day1'],
                                                json_response_DetailedPairStats['previousValue_day1'],
                                                buy_tax,
                                                sell_tax,
                                                token['token_address'],
                                                token['pair_address'],
                                                token['lp'],
                                                token['txns'],
                                                txns_less_5_mins,
                                                token['buys'],
                                                token['sells'],
                                                token['token_url'],
                                                token['dexcreener'],
                                                f"https://www.dextools.io/app/es/ether/pair-explorer/{token['pair_address']}"
                                            )
                                list_volume_day1.append(json_response_DetailedPairStats['day1'])
                                list_volume_hour1.append(json_response_DetailedPairStats['hour1'])
                                list_volume_hour4.append(json_response_DetailedPairStats['hour4'])
                                list_volume_hour12.append(json_response_DetailedPairStats['hour12'])
                            else:
                                pass

                        else:
                            # list_test.append(f"🟥**[{token['token_name']}]**({dextools_url}{token['pair_address']})" + "|" + f"**[{token['token_symbol']}]**({token['dexcreener']})"
                            #     + '\n' + 
                            #     f"**🔖Buy {buy_tax} & Sell {sell_tax}**" 
                            #     + '\n' + 
                            #     f"💰**LP**: {token['lp']}" + '|' + f"**VOL**: {json_response_DetailedPairStats['day1']}" + '|' + f"**TXNS**: {token['txns']}"
                            #     + '\n' + 
                            #     f"**🔥TXNS <5mins: {txns_less_5_mins}**" + '\n' + '\n')
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass

        total_volume_hour1 = str("\n   ▪️**1h** Volume: " + "$" + str(sum(list_volume_hour1)))
        total_volume_hour4 = str("\n   ▪️**4h** Volume : " + "$" + str(sum(list_volume_hour4)))
        total_volume_hour12 = str("\n   ▪️**12h**: " + "$" + str(sum(list_volume_hour12)))
        total_volume_day1 = str("\n   ▪️**24h** Volume: " + "$" + str(sum(list_volume_day1)) + f"Finish loop at: {datetime.now().strftime('%d/%m/%Y %H:%M:00')}")
        print(f"Honeypot requests {counter_honeypotrequests}")
        print(f"{total_volume_hour1} \n {total_volume_hour4} \n {total_volume_hour12} \n {total_volume_day1}")
        list_test.append(total_volume_hour1)
        list_test.append(total_volume_hour4)
        list_test.append(total_volume_hour12)
        list_test.append(total_volume_day1)
        
        try:
            # Edit message each X seconds
            original_message = context.bot.edit_message_text(chat_id=update.message.chat_id, message_id=original_message_id, text=" ".join(list_test), parse_mode = "Markdown", disable_web_page_preview=True )
            original_message_id = original_message.message_id
        except:
            pass

        print(f"Finish loop at: {datetime.now().strftime('%d/%m/%Y %H:%M:00')}")
        time.sleep(1500)   
        sqlUpdatePostTelegramTokenInfo("post_telegram_token_info")  
        
        sqlUpdateTrendingTokens("trending_tokens")
        print(f"Starting loop: {datetime.now().strftime('%d/%m/%Y %H:%M:00')}")

if __name__ == '__main__':
    updater.dispatcher.add_handler(CommandHandler('new_pairs', send_tg_message))
    updater.start_polling()
