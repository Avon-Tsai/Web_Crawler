# -*- coding: utf-8 -*-
"""
Created on Wed May 23 15:51:04 2018

@author
"""
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from selenium import webdriver
import urllib.request
import os
import time
from datetime import datetime
import mysql.connector
import traceback
   
def save_list(data) :
    cnx = mysql.connector.connect(user=user, password=password,host=host,port=port,database= database, charset='utf8') 
    cursor = cnx.cursor()
    sql = "insert into blog_list(blog_url,blog_title,blog_date) values(%(blog_url)s,%(blog_title)s,%(blog_date)s)"
    try:
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('************************** exception **************************')
        traceback.print_exc()

# Search list main 
for pdate in range(1,30):    
    service_path = "phantomjs"
    service_log_path = r"E:/watchlog.log"
    driver = webdriver.PhantomJS(service_path , service_log_path = service_log_path )

    url= "https://section.blog.naver.com/Search/Post.nhn?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate=2017-01-"+str(pdate)+"&endDate=2017-01-"+str(pdate)+"&keyword=%EB%8C%80%EB%A7%8C " ## %EB%8C%80%EB%A7%8C ## %EB%8C%80%EB%A7%8C%EC%97%AC%ED%96%89
    print(url)
    driver.get(url)
    soup_list = BeautifulSoup(driver.page_source,"lxml")
    search_number = soup_list.find("em",{"class":"search_number"}).text.replace('건','')
    search_number = search_number.split(',')

    if len(search_number) == 1 :
        page_num = int (int(search_number[0])/7)
    else :
        page_num = int((int(search_number[0])*1000 + int(search_number[1]))/7)
        
    print("page_num : " + str(page_num))
    driver.close()
    driver.quit()
      
    for num in range(1,page_num):
        service_path = "phantomjs"
        service_log_path = r"E:/watchlog.log"
        driver = webdriver.PhantomJS(service_path , service_log_path = service_log_path )
        print("num : " + str(num))
    
        site= "https://section.blog.naver.com/Search/Post.nhn?pageNo=" + str(num) + "&rangeType=PERIOD&orderBy=sim&startDate=2017-01-"+str(pdate)+"&endDate=2017-01-"+str(pdate)+"&keyword=%EB%8C%80%EB%A7%8C " ## %EB%8C%80%EB%A7%8C ## %EB%8C%80%EB%A7%8C%EC%97%AC%ED%96%89
        print(site)  
        
        driver.get(site)
        soup_search = BeautifulSoup(driver.page_source,"lxml")    
        # get user url
        url_tmp = soup_search.find_all("a",{"class":"desc_inner"})
        
        for u in url_tmp:
            print("Page :" + str(num))
            
            title = u.find("span",{"class":"title"}).text
        
            date = u.find("span",{"class":"date"}).text     
            date_tmp = date.split('. ')
            date = '-'.join(date_tmp).replace('.','')
            # datetime.datetime.strptime(date, '%Y-%m-%d')
            print(date)
        
            user_url = u.get( 'href' )
            print(user_url)
            
            blog_list = {'blog_url':user_url,'blog_title':title, 'blog_date':date}
            save_list(blog_list)
            print("===============================================================\n")
        driver.close()
        driver.quit()
        
