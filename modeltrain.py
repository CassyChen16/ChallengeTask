#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import libraries
import json
import numpy as np
import pandas as pd
import pickle
import operator
import collections
from dataparser import parse_json_file
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse


# In[3]:


# Load dataset
file_path = 'city_search.json'
df = parse_json_file(file_path)
#df.columns
#df.info()
df.head(3)


# In[4]:


def create_user_by_city_matrix(df):
    # Get all user_id and city set
    user_array = df['user_id'].unique()
    user_count = df['user_id'].nunique()
    cities_str = ','.join(df['cities'].values)
    cities_set = set(city.strip() for city in cities_str.split(','))

    # Generate user by cities matrix with all value as 0
    data = np.zeros((user_count, len(cities_set))
    df_user_by_city = pd.DataFrame(data, index = list(user_array), columns = list(cities_set))
    df_user_by_city.index.rename('user_id', inplace=True) 
    df_user_by_city.head(3)

    # Populate the matrix with 1 if user_id searched the city
    for user_id,group in df.groupby('user_id'):
        for item in group['cities'].iteritems(): 
          for c in item[1].split(','):
            df_user_by_city.loc[user_id, c.strip()] = 1
    return df_user_by_city

df_city_item = create_user_by_city_matrix(df)
#df_city_item.head(3)


# In[5]:


# Normalized user by city matrix
def normalize_user_user_matrx(df_city_item):
    magnitude = np.sqrt(np.square(df_city_item).sum(axis=1))
    df_city_item = df_city_item.divide(magnitude, axis='index')
    return df_city_item

'''
Calculate the column-wise cosine similarity between cities.
Retrun a similary matrix(dataframe)
'''
def cal_similarity_cosine(df_city_item):
    sparse_data = sparse.csr_matrix(df_city_item)
    similaries = cosine_similarity(sparse_data.transpose())
    similarity_matrix = pd.DataFrame(data=similaries, index = df_city_item.columns, columns = df_city_item.columns)
    return similarity_matrix

def city_similarity_matrix(df):
    #df = parse_json_file(file_path)
    df_city_item = create_user_by_city_matrix(df)
    df_city_item = normalize_user_user_matrx(df_city_item)
    #build the similarity matrix
    similarity_matrix = cal_similarity_cosine(df_city_item)
    #similarity_matrix.to_pickle('similaritymatrix.pkl')    
    return similarity_matrix



#similarity_matrix = city_similarity_matrix(file_path)
#similarity_matrix.head(3)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




