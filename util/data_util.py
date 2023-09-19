import pandas as pd
from datetime import datetime

DAYS_DEFINE = 30

class COMBINE_DF:
    def __init__(self, name='combind dataframe'):
        self.name = name
    def remove_duplicate(self, df, unique_id = 'id'):
        df.drop_duplicates(subset=unique_id, keep='first', inplace=True)
        return df
    def combine_df_up_down(self, df1, df2, unique_id = 'id'):
        df_new = pd.concat([df1, df2], axis=0)
        df_new = self.remove_duplicate(df_new, unique_id)
        return df_new

class FE_Base:
    def __init__(self):
        self.bad_days = DAYS_DEFINE
    
    def calculate_age(self, df, birth_date_column, date_format=None):
        df[birth_date_column] = pd.to_datetime(df[birth_date_column], format=date_format, errors='coerce')
        current_date = datetime.now()
        df['age'] = current_date.year - df[birth_date_column].dt.year
        df.loc[df[birth_date_column].dt.month > current_date.month, 'age'] -= 1
        return df['age'].values