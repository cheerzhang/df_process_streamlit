import pandas as pd


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