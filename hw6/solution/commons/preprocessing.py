from recordlinkage.preprocessing import clean
import numpy as np
import pandas as pd
import re

columns_to_keep = ['name', 'category', 'market_cap', 'country', 'city', 'founding_year', 'number_of_employees', 'website', 'ceo' ]
columns_to_clean = ['name', 'category', 'country', 'city', 'ceo']

def std_market_cap(value):
    if pd.isnull(value):
        return value
    return re.sub(r'[^0-9.,]', '', str(value))
    
def std_founding_year(value):
    if pd.isnull(value):
        return value
    return str(value).replace(".0","")[-4:]

def restore_null_values(value):
    if value == 'nan' or str(value).lower() == 'not found':
        return np.NaN 
    return value

def keep_only_specified_columns(df, columns_to_keep):
  current_columns = df.columns.tolist()
  columns_to_drop = [col for col in current_columns if col not in columns_to_keep]
  df.drop(columns_to_drop, axis=1, inplace=True)
  columns_to_add = [col for col in columns_to_keep if col not in current_columns]
  for col in columns_to_add:
      df[col] = np.NaN
  return df[columns_to_keep] #it reorders the columns

def pre_process_dataframe(df):
    df = keep_only_specified_columns(df, columns_to_keep)
    for col in columns_to_clean:
        df[col] = clean(df[col].astype(str))
    for col in columns_to_keep:
        df[col] = df[col].apply(lambda x: (restore_null_values(x)))
    df['market_cap'] = df['market_cap'].apply(lambda x: (std_market_cap(x)))
    df['founding_year'] = df['founding_year'].apply(lambda x: (std_founding_year(x)))

    return df