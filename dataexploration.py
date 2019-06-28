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
from pandas.io.json import json_normalize
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
pd.set_option('display.max_colwidth', -1)


# In[2]:


# Load dataset
file_path = 'city_search.json'
df = parse_json_file(file_path)
df.columns
df.info()
df.head(8)


# In[3]:


# check missing data
missing_data = pd.DataFrame({'total_missing': df.isnull().sum(), 'perc_missing': (df.isnull().sum()/20022)*100})
missing_data


# In[4]:


# Get the first day and the last day of the data
df_by_accessdate = df.groupby(by=["access_date"], axis = 0).count()
print('first_date: ', df_by_accessdate.index[0])
print('last_date: ', df_by_accessdate.index[-1])

# Plot the number of sessions by day 
daily_session_df = df.groupby(by=["access_date"], axis = 0).count()
fig, axes = plt.subplots(1,1,figsize=(20,10))
axes.set_ylabel("# of sessions")
axes.set_xlabel("access_date")
axes.set_title("# of Sessions per Day")
axes.plot(daily_session_df["session_id"])


# In[28]:


'''
Get the set of all searched cities and t
he corresponding searched times of each city
'''
searched_cities= df['cities'].unique()

cities_set = set() # the set of all searched cities
searched_city_dict = {} # the dictionary of "city:searched times" pair
for item in searched_cities: 
     for c in item.split(','):
        cities_set.add(c.strip())
        searched_city_dict[c.strip()] =  searched_city_dict.get(c.strip(),0) + 1
        

sorted_city = sorted(searched_city_dict.items(), key=operator.itemgetter(1))
sorted_city.reverse()
searched_city_dict = collections.OrderedDict(sorted_city)

print('The number of searched cities: ', len(cities_set))
print(searched_city_dict)

most_polular_cities = [item for item in searched_city_dict.keys() if searched_city_dict.get(item) > 50]
print('most_popular_cities: ','\n', most_polular_cities)

# These are all US and Canada cities

#Plot the # searched times by city name
plt.figure(figsize=(10,6))
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)

plt.plot(searched_city_dict.keys(), searched_city_dict.values())
plt.xlabel("Searched cities", labelpad=14)
plt.ylabel("# of Searched Times", labelpad=14)
plt.title("Count of Searched times per City", y=1.02)


# In[6]:


# Get group by country information
group_by_country = df.groupby('country')

# Create city×country data frame
rows = [] # For a city, the number of searched times by each country
index_to_country_dict = {} # Dictionary of "index:country" pair
country_to_usercount_dict = {}
index=0
for name,group in group_by_country:
   d = dict.fromkeys(cities_set, 0)
   country_to_usercount_dict[name] = group['user_id'].nunique()
   for items in group['cities'].iteritems(): 
      for c in items[1].split(','):
        d[c.strip()] = d.get(c.strip()) + 1
   rows.append(d)
   index_to_country_dict[index]=name
   index = index+1

# city×country data frame
df_city_by_country = pd.DataFrame.from_dict(rows, orient='columns')
df_city_by_country.rename(index = index_to_country_dict, inplace=True)
df_city_by_country.head()


# In[7]:


# Plot user counts by country
user_count_by_country = pd.Series(country_to_usercount_dict).sort_index()
sns.set(font_scale=1.4)
plt.subplot(1, 2, 1)
user_count_by_country.plot(kind="bar",title="Count users by country",figsize=(12,5),rot=0)
plt.xlabel("country")
plt.ylabel("Count of users")
plt.title("Count of Users by Country", y=1.02)

# Plot session counts by country
sns.set(font_scale=1.4)
plt.subplot(1, 2, 2)
country_series = df['country'].value_counts().sort_index()
country_series.plot(kind="bar",title="country distribution",figsize=(12,5),rot=0)
plt.xlabel("country", labelpad=14)
plt.ylabel("Count of search sessions", labelpad=14)
plt.title("Count of Search Sessions by Country", y=1.02)

plt.tight_layout()

avg_session_per_user = df.shape[0]/df['user_id'].nunique()
print('Average number of sessions per user: ', avg_session_per_user)


# In[8]:


# country×city data frame
df_country_by_city = df_city_by_country.T
df_country_by_city.head()
df_country_by_city.describe()


# 1) US people searched the maximum number of cities, UK and DE ranked the second and third, 
#    maybe it is because of US's large population
# 2) Based on the standard deviation, the number of cities searched by people in US, UK, DE, Unknown countrry
#    spead over more cities as compared to ES, FR, and IT
# 3) For all countries, there is a large gap between 75% to max. It means that at most 25% cities 
#   (89 multiply by 0.25 =  23 approximately) are very popular and has been searched a lot by people coming from every 
#   country.
#   

# In[9]:


# For each country, calculate the percentage of searched times for each city as compared to 
# the total number of searches for that country
session_per_country_list = df['country'].value_counts()
df_country_by_city['US_sr'] = df_country_by_city['US']/session_per_country_list[0]
df_country_by_city['DE_sr'] = df_country_by_city['DE']/session_per_country_list[1]
df_country_by_city['UK_sr'] = df_country_by_city['UK']/session_per_country_list[2]
df_country_by_city['Unknown_sr'] = df_country_by_city['Unknown']/session_per_country_list[3]
df_country_by_city['FR_sr'] = df_country_by_city['FR']/session_per_country_list[4]
df_country_by_city['ES_sr'] = df_country_by_city['ES']/session_per_country_list[5]
df_country_by_city['IT_sr'] = df_country_by_city['IT']/session_per_country_list[6]

# Get the top 25 cities searched most by Unknown country
df_country_by_city.nlargest(30, 'Unknown').head(23)


# From DE_sr, UK_sr, and Unknown_sr, we can see people in these countries are espcially like to search New York. 
# However, US_sr is not very high which means US people not very interested in New York as compared to people in 
# DE, UK and Unknown.

# In[10]:


# Get the top 15 cities searched least by Unknown country
df_country_by_city.nsmallest(15, 'Unknown').head(15)


# From the cities that have been searched least, Halifax in Canada is not known at all for people in IT, 
# DE and UK, but have been searched by US, Unknown, and other countries.

# In[11]:


# Plot the number of searched session vs cities for each country
plt.figure(figsize=(10,6))
plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)
plt.plot(df_country_by_city.index, df_country_by_city["DE"], label='DE')
plt.plot(df_country_by_city.index, df_country_by_city["ES"], label='ES')
plt.plot(df_country_by_city.index, df_country_by_city["FR"], label='FR')
plt.plot(df_country_by_city.index, df_country_by_city["IT"], label='IT')
plt.plot(df_country_by_city.index, df_country_by_city["UK"], label='UK')
plt.plot(df_country_by_city.index, df_country_by_city["US"], label='US')
plt.plot(df_country_by_city.index, df_country_by_city["Unknown"], label='Unkown')
plt.xlabel("Searched cities", labelpad=14)
plt.ylabel("Count of searched sessions", labelpad=14)
plt.title("Count of Searched Sessions Per City for Each Country", y=1.02);
plt.legend()


# In[12]:


plt.subplots(figsize=(6,6))
sns.heatmap(df_country_by_city[df_country_by_city.columns[0:7]].corr(), annot=True)
# It shows that People of all countries have similar interests regarding cities based on the number of search


# # #Conclusion: 
# The Unknown country is Canada. Since Canada in north America and have large population as compared to those of European country. Canada is close to US, beside canadian cities, canadian people likes to visit US cities. Canadian people will show more passion to New York as compared to US people.

# In[ ]:




