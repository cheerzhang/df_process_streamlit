import pandas as pd
import requests

class GetModelPredict:
    def __init__(self, url = None):
        self.url = url
    def set_url(self, url):
        self.url = url
    def call_gender_model(self, df, first_name=None):
        if first_name is not None:
            df['first_name'] = df[first_name]
        df['first_name'] = df['first_name'].fillna("")
        data = df[['first_name']].to_dict(orient='records')
        api_url = self.url
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            response_data = response.json()
            df['pred'] = response_data['gender']
            return df