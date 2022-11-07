#!/usr/bin/env python
# coding: utf-8

# In[2]:


from bs4 import BeautifulSoup
import requests
import csv
import re
from os import path
import pandas as pd
url = 'https://www.indiatoday.in/visualstories/'
import sqlite3
header = ['date','information_link','category','headlines','story_card_image','description','image_video_links']
with open(r"Data.csv", 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
#creating table and db
con = sqlite3.connect('indiatoday.db')
cur = con.cursor()
# cur.execute("DROP TABLE indiatoday") 
cur.execute('''CREATE TABLE IF NOT EXISTS indiatoday (date,information_link,category,headlines,story_card_image,description,image_video_links)''')

#function for extracting data from link using beautifulsoup and requests library
def beautifulsoup(hyper_link):
    responce=requests.get(hyper_link,verify=False)
    soup=BeautifulSoup(responce.text,'html.parser')
    return soup

def scrape_each_info(url,page_num):
    df_list=[]
    for page_no in range(1,page_num+1):
        url = 'https://www.indiatoday.in/visualstories/?page='+str(page_no)
        raw_html = beautifulsoup(url)
        all_cards =raw_html.findAll(attrs={'class':'visualStoryCard'})
        for each_card in all_cards:
            link =each_card.find('a')['href']
            category = each_card.find('h2').text
            heading = each_card.find('h3').text
            date = each_card.find(attrs={'class':'bottom__date__batch'}).text
            card_image = each_card.find('img')['src']
#             print(link)
            soup1=beautifulsoup(link)
            all_card_details = soup1.findAll('amp-story-page')
            for each_card in all_card_details[:-1]:
                dic={}
                try:
                    img = each_card.find('amp-img').get('src')
                    desc = [i.text for i in each_card.find(attrs={'class':'letterbox'}).find_all('p')]
                    desc1 = [i.text for i in each_card.find(attrs={'class':'letterbox'}).find_all('h1')]
                    description =" - ".join(desc+desc1).replace('\xa0','')
                except:
                    try:
                        img = each_card.find('amp-video').find('source').get('src')
                        desc = [i.text for i in each_card.find(attrs={'class':'letterbox'}).find_all('p')]
                        description =" - ".join(desc).replace('\xa0','')
                    except:
                        img = ''
                        desc = [i.text for i in each_card.find(attrs={'class':'letterbox'}).find_all('p')]
                        description =" - ".join(desc).replace('\xa0','')
                df_list.append((date,link,category,heading,card_image,description,img))
    return df_list

df = scrape_each_info(url,2)
cur.executemany("INSERT INTO indiatoday VALUES (?,?,?,?,?,?,?)",df)
con.commit()
dataframe = pd.DataFrame(df)
dataframe.to_csv('Data.csv', mode='a', index = False, header=None)

# script for saving html pages 
# import os
# pagefolder = r''
# if not os.path.exists(pagefolder): # create only once
#     os.mkdir(pagefolder)
# os.chdir(r'')
# for page_no in range(1,3):
#     url = 'https://www.indiatoday.in/visualstories/?page='+str(page_no)
#     url_exist = url.replace('/','').replace(':','').replace('.','').replace('?','').replace('=','')+".html"
#     if url_exist in os.listdir('mainpages'):
#         with open('mainpages/{}'.format(url_exist), 'r') as file1:
#             soup = BeautifulSoup(file1.read(),'html.parser')
#     else:
#         response = requests.get(url,verify=False)
#         with open('mainpages/{}'.format(url_exist), 'w') as file:
#             file.write(responce.text)
#         print("file created")


# In[ ]:




