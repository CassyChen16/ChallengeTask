#!/usr/bin/env python
# coding: utf-8

# In[21]:


# Load libraries
import json
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
from datetime import datetime, timezone
import errno


# In[22]:


def parse_json_file(file_path):
    #open json file
    try:
        with open(file_path, 'r') as read_file:
            data = json.load(read_file)
    except (OSError, IOError) as e: 
       if getattr(e, 'errno', 0) == errno.ENOENT:
          print('json file not found!') # file not found
       raise

    # Parse json file into dataframe
    df_original = json_normalize(data, record_path=['user'], meta=['session_id','unix_timestamp', 'cities'])
    df_user = json_normalize(df_original[0])
    df = pd.concat([df_original, df_user], axis = 1)
    df.drop(columns=[0,'_row'], axis=1, inplace=True)
    df['country'].replace('', 'Unknown', inplace=True)

    df["joining_date"] = pd.to_datetime(df["joining_date"])
    df["unix_timestamp"] = pd.to_datetime(df["unix_timestamp"],unit='s')
    df['access_date'] = df['unix_timestamp'].dt.date
    df['country'] = df['country'].astype('category').cat.as_ordered()
    return df


# In[23]:


# For test
file_path = 'city_search.json'
df = parse_json_file(file_path)
df.columns
df.info()
df.head(8)

