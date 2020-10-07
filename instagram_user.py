import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from pymongo import MongoClient
#from webdriver_manager.chrome import ChromeDriverManager

import time
MONGO_URL=""

client= MongoClient(MONGO_URL)
db = client.instagram_user




PATH='C:\Program Files\ChromeDriver\chromedriver.exe'
driver=webdriver.Chrome(PATH)

entities=['ronaldo', 'microsoft', 'messi', 'dell', 'lampard', 'pfizer', 'chelsea', 'sanofi', 'buhari', 'twitter']

#search=driver.find_element_by_name("q")
def get_all(entities):
    ##edit here later
    handle_every=[]
    name_every=[]
    #entities=['ronaldo', 'microsoft', 'messi', 'dell', 'lampard', 'pfizer', 'chelsea', 'sanofi', 'buhari', 'twitter']
    for ent in entities:
        driver.get('https://searchusers.com/') ##open the site


        search=driver.find_element_by_name("q") ##use the search button

        search.send_keys(ent) ## search for the entity
        search.send_keys(Keys.RETURN) ##press enter to begin search
        print('getting for', ent)

        main=driver.find_element_by_class_name('tagbox') ##this gets all the users found
        all_users=[]
        all_users.append(main.text) ##apend it to a list


        handle_list=[]
        name_list=[]
        special='@'

        all_users_split=[x for x in all_users[0].split('\n')] ## split the above result by '\n'

        ## after spliting, strip @ character, then add handle and full names to the respective lists
        for item in all_users_split:
            if special in item:
                remove_special=item.strip('@')
                handle_list.append(remove_special)
            else:
                name_list.append(item)


        handle_every.append(handle_list)
        name_every.append(name_list)
        
    return handle_every, name_every
    
    
def get_number_of_likes(handle_every): 
    ##get the number of likes for each handle   
        try:    
            handle_every=[b for a in handle_every for b in  a[:1]]
            num_of_likes=[]
            for j in handle_every:
                try:
                    driver.get('https://searchusers.com/'+ '/user/' +j) ##get the account of the handle

                    soup = BeautifulSoup(driver.page_source,"lxml") ##scrape the entire page

                    nposts2 = soup.findAll('div',  {'class': 'tallyb'}) ##get where the number of likes is called 
                    
                    nposts2=str(nposts2[1]) ##convert it to a string
                    
                    nposts2= re.findall(r'\d+', nposts2) ##get only the number
                    nposts2=int(''.join(nposts2)) ##convert it to an integer
                    print('....getting subsets for....', j)
                    print()

                    num_of_likes.append(nposts2) ##append it to our empty list
                except:
                    num_of_likes.append(int(0)) ##append zero for users who locked their accounts
        except:
            pass
        
        return num_of_likes
        


        

        
def save_as_df(handle_every, name_every, num_of_likes):  
    
    handle_every=[b for a in handle_every for b in  a[:1]]
    name_every=[b for a in name_every for b in  a[:1]]
    
    ##save all to a dataframe       
    df=pd.DataFrame()
    df['handle']=handle_every
    df['full name']=name_every
    df['likes_per_post']=num_of_likes

    ##filter by a digit
    df=df[df['likes_per_post']>500]

    #print(df)
    return df


def save_to_mongodb(df):
    
    
    # Load in the instagram_user collection from MongoDB
    instagram_user_collection = db.instagram_user_collection # similarly if 'testCollection' did not already exist, Mongo would create it
    
    cur = instagram_user_collection.find() ##check the number before adding
    print('We had %s instagram_user entries at the start' % cur.count())
    
     ##search for the entities in the processed colection and store it as a list
    instagram_users=list(instagram_user_collection.find({},{ "_id": 0, "handle": 1})) 
    instagram_users=list((val for dic in instagram_users for val in dic.values()))


    #loop throup the handles, and add only new enteries
    for handle in df['handle']:
        if handle  not in instagram_users:
            instagram_user_collection.insert_many(df.to_dict('records')) ####save the df to the collection
    
    
    
   
   
  
    cur = instagram_user_collection.find() ##check the number after adding
    print('We have %s spacy entity entries at the end' % cur.count())
    
    
   
def call_all_func():
    entities=['ronaldo', 'microsoft', 'messi', 'dell', 'lampard', 'pfizer', 'chelsea', 'sanofi', 'buhari', 'twitter']

    handle_every, name_every= get_all(entities)
    num_of_likes=get_number_of_likes(handle_every)
    df=save_as_df(handle_every, name_every, num_of_likes)
    save_to_mongodb(df)
    df = df.to_json()
    
    print('we are done ')
    
    driver.close()
    
    return df
    
#call_all_func()

#close the browser 


