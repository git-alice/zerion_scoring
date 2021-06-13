import pandas as pd
import numpy as np
import datetime


def prepare_data(df):
    df = df.drop(columns=['address_type'])
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x)) 
    df[['income', 'outcome', 'fee', 'balance']] = df[['income', 'outcome', 'fee', 'balance']].fillna(0)   
    df['PNL_timestamp'] = df['income'] - df['outcome'] - df['fee']
    df['PNL'] = df['PNL_timestamp'].cumsum()    
    df['diff'] = df['balance'] - df.groupby('address')['balance'].shift()
    return df

def window_diff_mean_stats(chunk, tao):
    end = chunk['timestamp'].max()
    start = end - tao
    window = chunk.loc[chunk['timestamp'] >= start]
    days = tao.days
    
    df_mean = window['diff'].mean()
    
    df_mean = pd.DataFrame(data=[[df_mean / days]],
                        columns=['diff_ratio_' + f'{days}' + 'days'],)

    return df_mean

def window_pnl_mean_stats(chunk, tao):
    end = chunk['timestamp'].max()
    start = end - tao
    window = chunk.loc[chunk['timestamp'] >= start]
    days = tao.days
    
    df_mean = window['PNL'].mean()
    
    df_mean = pd.DataFrame(data=[[df_mean / days]],
                        columns=['PNL_ratio_' + f'{days}' + 'days'],)

    return df_mean

def window_mean_stats(chunk, tao):
    end = chunk['timestamp'].max()
    start = end - tao
    window = chunk.loc[chunk['timestamp'] >= start]
    days = tao.days
    keys = ['income', 'outcome', 'fee', 'balance']
    
    df_mean = window[keys].mean()
    df_mean = df_mean.to_frame().T
    df_mean = df_mean.rename(columns={key: key + '_mean_window={}'.format(days) for key in keys})

    return df_mean

def window_std_stats(chunk, tao):
    end = chunk['timestamp'].max()
    start = end - tao
    window = chunk.loc[chunk['timestamp'] >= start]
    days = tao.days
    keys = ['income', 'outcome', 'fee', 'balance']
    
    df_mean = window[keys].std()
    df_mean = df_mean.to_frame().T
    df_mean = df_mean.rename(columns={key: key + '_std_window={}'.format(days) for key in keys})

    return df_mean

def number_of_transaction_ration(chunk, tao):
    end = chunk['timestamp'].max()
    start = end - tao
    window = chunk.loc[chunk['timestamp'] >= start]
    days = tao.days
    df = pd.DataFrame(data=[[window.shape[0] / days]],
                        columns=['ratio_transactions_' + f'{days}' + 'days'],
                     ) 
    return df

def number_of_transaction(chunk):
    df = pd.DataFrame(data=[[chunk.shape[0]]],
                        columns=['total_num_transactions'],
                     ) 
    return df

def get_time_stats(chunk):
    start = chunk['timestamp'].min() 
    end = chunk['timestamp'].max()
    days = (end - start).days
    monthes =  days / 30
    years = days / 365
    df = pd.DataFrame(data=[[days, monthes, years]],
                        columns=['days_from_start', 'monthes_from_start', 'years_from_start'],
                     ) 
    return df

def apply_to_wallet(chunk):
    windows = [pd.Timedelta(value=7, unit='days'), 
               pd.Timedelta(value=14, unit='days'), 
               pd.Timedelta(value=30, unit='days'),
               pd.Timedelta(value=90, unit='days'),
               pd.Timedelta(value=180, unit='days'),
               pd.Timedelta(value=360, unit='days')]
    dfs = []
    df1 = get_time_stats(chunk)
    dfs.append(df1)
    df2 = number_of_transaction(chunk)
    dfs.append(df2)
    
    df3 = []
    for w in windows:
        dff = number_of_transaction_ration(chunk, w)
        df3.append(dff)
    dfs.extend(df3)
    
    df4 = []  
    for w in windows:
        dfff = window_mean_stats(chunk, w)
        df4.append(dfff)
    dfs.extend(df4)
    
    df5 = []  
    for w in windows:
        dffff = window_std_stats(chunk, w)
        df5.append(dffff)
    dfs.extend(df5)
    
    df6 = []  
    for w in windows:
        dfffff = window_pnl_mean_stats(chunk, w)
        df6.append(dfffff)
    dfs.extend(df6)
    
    df7 = []  
    for w in windows:
        dffffff = window_diff_mean_stats(chunk, w)
        df7.append(dffffff)
    dfs.extend(df7)
    
    vector = pd.concat(dfs, axis=1)
    vector.index = chunk.index.get_level_values('address').unique()
    return vector

def gen_features(df):
    df_prep = prepare_data(df)
    features = df_prep.groupby('address').apply(apply_to_wallet).droplevel(0)
    features.fillna(0, inplace=True)
    features.to_csv('features_1.csv')
    return features
