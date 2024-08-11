# This is an API which scape the currency data from tjgu.org and return the data in csv format

# Import the necessary libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import io


# Define the get_currency function to recived the currency data from website
def get_currency_data(currency_code: str) -> pd.DataFrame:
    url = f'https://www.tgju.org/profile/{currency_code}/history'
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('table', {'class': 'table widgets-dataTable table-hover text-center history-table'})

    # Extract the headers (columns names)
    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())

    # Extract the data rows
    data = []
    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        if len(cols) > 0:
            cols = [ele.text.strip() for ele in cols]
            data.append(cols)

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(data, columns=headers)
    
    # Rename and keep only the necessary columns

    cols_to_keep = ['تاریخ / میلادی', 'پایانی؟']
    curr_df = df[cols_to_keep]

    curr_df = curr_df.rename(columns={'تاریخ / میلادی': 'Date', 'پایانی؟': 'Price'})
    
    return curr_df
    

# Create the API using FastAPI
app = FastAPI()

class CurrencyRequest(BaseModel):
    currency_code: str
    
@app.post("/get_currency_data")
def get_currency_data_api(request: CurrencyRequest):
    df = get_currency_data(request.currency_code)
    
    # Convert DataFrame to CSV format for the response
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    return {"data": csv_data}