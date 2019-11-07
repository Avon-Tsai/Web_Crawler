#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

## databse : gsearch.urcosme_pageview
## author : Ya Fang Tsai
## date : 2017 / 11 / 28

import requests as r
from bs4 import BeautifulSoup
import requests
import re
import codecs
import json
import sys
from pprint import pprint
import jconfig2
import mysql.connector
import crawlerutil
import traceback
import time
from dateutil.parser import parse
import datetime

cnx2 = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'}
logtype='urcosme_review_detail'  

def save_review_detail(data):
    global cnx2
    cursor2 = cnx2.cursor()
    
    date = ''
    week = datetime.datetime.now().isocalendar()
    date = str(week[0]) + '-' + str(week[1])
    date_updatedAt = date+'_updatedAt'
    date_pageview = date+'_pageview'
    date_like = date+'_like'
    
    date_now = datetime.datetime.now()
    
    sql_tmp = []
    cstatus_tmp = []
    for row in range(len(data)) :
        reviewid = data[row][0]
        pageview = data[row][1]
        like = data[row][2]
           
        sql = "update gsearch.urcosme_pageview set `%s` = %s,`%s` = '%s',`%s` = %s  where reviewid = %s" %(date_pageview,pageview,date_updatedAt,date_now,date_like,like,reviewid) 
        sql_tmp.append(sql)
        
        cstatus = "update urcosme_pageview set cstatus = 1 where reviewid='"+str(reviewid)+"'"
        cstatus_tmp.append(cstatus)
        
    sql_all = ';'.join(sql_tmp)+';'
    cstatus_all = ';'.join(cstatus_tmp)+';'
    print(sql_all)
    
    try:
        for result in cursor2.execute(sql_all, multi=True):
            pass    
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()
                    
    try:
        for result in cursor2.execute(cstatus_all, multi=True):
            pass 
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def myparser(content):
    global logtype
    global reviewid
    global result

    soup = BeautifulSoup(content, "html.parser")     
    
    ''' get review-date and pageview '''
    pageview=soup.find("div",{"class":"review-date-and-pageview"})
    if pageview is not None:
        if pageview.text.find('人氣') != -1 :
            r_pageview = pageview.text.split('人氣 ')[1]
        else :
            r_pageview = -1
    else :
        r_pageview = -1
        
    ''' get ur-like count '''
    urlike=soup.find("div",{"class":"ur-like-desc"})
    if urlike is not None:
        m=re.search(r'([\d\.]+)',urlike.text)
        if m:
            r_like=m.group(1)
        else:
            r_like=-1
    else:
        r_like=-1
        
    #data={'pageview':r_pageview,'like':r_like}
    #save_review_detail(data)
    data = [reviewid,r_pageview,r_like]
    result.append(data)
    
result = []
reviewid=0
cnx = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 
cursor = cnx.cursor()
sql = "select reviewid from urcosme_pageview where cstatus = 0 order by rand() limit 50"
cursor.execute(sql)

for (u) in cursor:
    reviewid=str(u[0])
    print("review id :"+ reviewid)
    try :
        crawlerutil.crawl_and_savenext(logtype,'https://www.urcosme.com/reviews/'+reviewid,myparser)
    except :
        print("Took Too Long To Respond !!!\n")
        pass
        
cursor.close() 
print(len(result))  
save_review_detail(result)
