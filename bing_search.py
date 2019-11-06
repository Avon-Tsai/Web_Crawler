#!/usr/bin/python3
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time
import urllib
import sys
import re
from selenium import webdriver
import urllib.parse
from selenium.webdriver.chrome.options import Options
import os

import mysql.connector
import re
import socket
import traceback
import datetime
from datetime import timedelta
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
cnx = mysql.connector.connect(user, password ,host, port, database, charset='utf8') 

Begindate=17531 #2017/12/31  count back
weekOfYear=52
CountYear=3
enddate=Begindate-CountYear*weekOfYear*7

def save_data(data):
    global cnx
    cursor = cnx.cursor()
    sql = "insert into Serena.Bing_result_test(begindate,enddate,product,brand,numresult,EnddateCount,brandIndex) values(%(begindate)s,%(enddate)s,%(product)s,%(brand)s,%(numresult)s,%(EnddateCount)s,%(brandIndex)s)  ON DUPLICATE KEY UPDATE numresult=%(numresult)s  "
    try:
        print(data) 
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('exception')
        traceback.print_exc()

def get_progress(query): #目前爬到哪一個日期
    global cnx
    cursor = cnx.cursor()
    product,brand=query.split('$@$')
    sql = "select min(EnddateCount) from Serena.Bing_result_test where product='"+product+"' and  brandIndex= '"+BrandClean(brand)+"' "

    resultdt=Begindate
    try:
        cursor.execute(sql)
        for u in cursor:
            resultdt=int(u[0])-7
    except: 
        print('exception')
        traceback.print_exc()
    return resultdt

def BrandClean(a):
    rule = re.compile("[^A-Za-z]")
    tmpString=rule.sub("",a)
    return tmpString

def process_page(driver):
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    elmt=soup.find('span',{'class':'sb_count'})
    date=soup.find('span',{'class':'fs_label'})
    sresult=re.search(u'(.+) results',elmt.text)
    return sresult.group(1).replace(",",""),date.text

def CheckSearchResult(driver):
    state=False
    html = driver.page_source
    soup = BeautifulSoup(html,"html.parser")
    elmt=soup.find('ol',{'id':'b_results'})
    elmt2=elmt.find('h1')
    if "There are no results" in str(elmt2):
        state=True

    return state

def dateTransform(date):
    date=re.sub(" ","",date)
    return datetime.datetime.strptime(date,"%m/%d/%Y").strftime("%Y-%m-%d")

def get_prevweek(dt):
    ed=dt.strftime("%m/%d/%Y").replace("/","%2F")
    dt=dt+timedelta(days=-6)
    bg=dt.strftime("%m/%d/%Y").replace("/","%2F")
    return (bg,ed)

def mysearch(ed,query):
    global enddate
    global driver
    state=False
    flag=False
    product,brand=query.split('$@$')
    bg=ed-6
    fullurl='https://www.bing.com/search?q='+brand+"+"+product+'&filters=ex1%3a%22ez5_'+str(bg)+'_'+str(ed)+'%22&qs=n&sp=-1&pq='+brand+"+"+product+'&sc=8-6&qpvt='+brand+"+"+product
    driver.get(fullurl)
    try:
        #搜尋結果為0的時候ww這一行會timeout error,所以做except例外處理,給值:0
        ww = WebDriverWait(driver,12).until(EC.presence_of_element_located((By.XPATH, "//div[@id='b_tween']")))
        numresult,date=process_page(driver)
        StartDate,EndDate=date.split('-')
    except:
        flag=True
        numresult=0
        
    if flag:
        try:
            ww = WebDriverWait(driver,12).until(EC.presence_of_element_located((By.XPATH, "//div[@id='b_content']")))
            state=CheckSearchResult(driver)
        except:
            pass

    if state!=True and flag == False:
        save_data({'begindate':dateTransform(StartDate),'enddate':dateTransform(EndDate),'product':product,'brand':brand,'numresult':int(numresult),'EnddateCount':int(ed),'brandIndex':BrandClean(brand)})
        time.sleep(2)
    elif state!=True and flag == True:
        StartDate=datetime.datetime.strptime("2017-12-31","%Y-%m-%d").date()+timedelta(days=(bg-Begindate))
        EndDate=datetime.datetime.strptime("2017-12-31","%Y-%m-%d").date()+timedelta(days=(ed-Begindate))
        save_data({'begindate':StartDate,'enddate':EndDate,'product':product,'brand':brand,'numresult':int(numresult),'EnddateCount':int(ed),'brandIndex':BrandClean(brand)})
        time.sleep(2)

    return state

options = webdriver.ChromeOptions() 
options.add_argument("user-data-dir=User Data") #Path to your chrome profile
driver= webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)

cursor = cnx.cursor()
sql="SELECT o.name, o.asCat FROM gsearch.search_list s, oneil.urcosme_prod_brand_google_segment o where s.id % 7 = 1 and o.brandid=s.pixid ;"
cursor.execute(sql)
result=[]

for u in cursor:   # 把要跑的keyword存到result list
    tmp=[]
    try:
        tmp=u[1].split('+or+')
    except:
        pass

    if len(tmp)>1:
        brand=tmp[1]
    else:
        brand=u[1]
    result.append(u[0] + "$@$" + brand)

for query in result:  
    n=get_progress(query)
    if n is None:
        n=Begindate

    while n >= enddate:
        state=mysearch(n,query)
        n=n-7
        if state:
            break

driver.close()
exit(1)
