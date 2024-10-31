import pandas as pd
import requests


def calcTax(x):
    if x < 50:
        return 0
    else:
        return x * 0.02
    
def fetchCurrentPrices():

    latest = 'https://prices.runescape.wiki/api/v1/osrs/latest'
    mapping = 'https://prices.runescape.wiki/api/v1/osrs/mapping'
    five_minute = 'https://prices.runescape.wiki/api/v1/osrs/5m'
    one_hour = 'https://prices.runescape.wiki/api/v1/osrs/1h'

    # get latest high and low prices and unix timestamp from when the last transaction was placed.
    # if there has not been an instant buy/sell high/highTime, low/lowTime will be nan
    latest_data = requests.get(latest).json()    
    latest_df = pd.DataFrame(latest_data['data']).T
    latest_df = latest_df.reset_index()
    latest_df['index'] = latest_df['index'].astype(int)

    # # gives a list of objects containing name, id, examine text, buy limit, member status, low/high alch.

    mapping_data = requests.get(mapping).json()
    mapping_df = pd.DataFrame(mapping_data)
    mapping_df = mapping_df.rename(columns={'id':'index'})

    #Gives 5-minute average of item high and low prices as well as the number traded for the items that we have 
    # data on. Comes with a Unix timestamp indicating the 5 minute block the data is from.
    five_minute_data = requests.get(five_minute).json()
    five_minute_df = pd.DataFrame(five_minute_data['data']).T
    five_minute_df = five_minute_df.reset_index()
    five_minute_df['index'] = five_minute_df['index'].astype(int)    
    five_minute_df = five_minute_df.rename(columns={'avgHighPrice': '5m_avgHighPrice',
                                                    'highPriceVolume':'5m_highPriceVolume',
                                                    'avgLowPrice':'5m_avgLowPrice',
                                                    'lowPriceVolume':'5m_lowPriceVolume'})

    # Gives hourly average of item high and low prices, and the number traded.
    one_hour_data = requests.get(one_hour).json()
    one_hour_df = pd.DataFrame(one_hour_data['data']).T
    one_hour_df = one_hour_df.reset_index()
    one_hour_df['index'] = one_hour_df['index'].astype(int)
    one_hour_df = one_hour_df.rename(columns={'avgHighPrice': '1h_avgHighPrice',
                                            'highPriceVolume':'1h_highPriceVolume',
                                            'avgLowPrice':'1h_avgLowPrice',
                                            'lowPriceVolume':'1h_lowPriceVolume'})

    all_df = pd.merge(latest_df, mapping_df, on='index', how='inner')
    all_df = pd.merge(all_df, five_minute_df, on='index', how='inner')  
    all_df = pd.merge(all_df, one_hour_df, on='index', how='inner')
    all_df['name'] = all_df['name'].astype(str)
    all_df = all_df.drop(columns=['examine', 'members','lowalch','highalch','icon'])
        
    return all_df


def calculateFeatures(data_frame):
    data_frame['margin'] = data_frame['high'] - data_frame['low']
    data_frame['tax'] = data_frame.apply(lambda x: calcTax(x['high']), axis=1)
    data_frame['profit'] = data_frame['margin'] - data_frame['tax'] 
    data_frame['ROI'] = data_frame['profit'] / data_frame['low']

