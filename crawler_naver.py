# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 11:06:19 2018

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
import pickle

service_path = "phantomjs"
service_log_path = r"E:/watchlog.log"
driver = webdriver.PhantomJS(service_path , service_log_path = service_log_path)
driver.set_page_load_timeout(30)

def crawler(blog_url, url, blogId, logNo, title, date) :
    try : 
        driver.get(url)
        soup = BeautifulSoup(driver.page_source,"lxml")
        
        ''' get image '''
        #print("Get Image ")
        #crawler_imag(soup, blogId, logNo)
        
        try:
            ''' get content '''
            all_content = []
            content = soup.find_all("p",{"class":"se_textarea"})
            if len(content) > 0 :
                for c in content:
                    all_content.append(c.text)
    
            content = soup.find_all("div",{"class":"view"})
            if len(content) > 0 :
                for c in content:
                    all_content.append(c.text.replace('\n','').replace('\t',''))
                
            content = soup.find_all("div",{"id":"postViewArea"})
            if len(content) > 0 :
                for c in content:
                    all_content.append(c.text)
    
            ''' get tag '''
            all_tag = []
            tag = soup.find_all("a",{"class":"tag pcol1 itemTagfont _setTop"})
            for t in tag:
                all_tag.append(t.text)
    
            data = {'title':title, 'pdate':date, 'blogId':blogId,'logNo':logNo,'content':str(all_content),'tag':str(all_tag)}
            print(data)    
            #save(data)
            #update_status(blog_url)
            #driver.close()
            #driver.quit()
            print("===============================================================\n")
            
        except: 
            print('************************** Exception **************************')
            traceback.print_exc()
            
    except :
        driver.delete_all_cookies()
        print("************************ Timeout Exception ************************")
        pass

def crawler_imag(soup, blogId, logNo) :
    img_path = r'E:/naver_img/' + blogId + '_' + logNo
        
    if not os.path.exists(img_path):
        os.makedirs(img_path)
  
    image = soup.find_all("img",{"class":"se_mediaImage __se_img_el"})
    if len(image) < 1 :
        image = soup.find_all("img",{"class":"_photoImage"})
        
    num = 1  
    for img in image:
        try :
            full_image_path = img_path +'/'+ str(num) + '.jpg'
            image_path = img.get('src')
        
            urllib.request.urlretrieve(image_path, full_image_path)
            num += 1
        except: 
            print('************************** Exception **************************')
            traceback.print_exc()

def save(data) :
    host = '140.96.178.1'
    port = 3306
    database = 'naver'
    user = 'root'
    password = 'itriw100'
    
    cnx = mysql.connector.connect(user=user, password=password,host=host,port=port,database= database, charset='utf8')     
    cursor = cnx.cursor()  
    
    sql = "insert into blog(logNo,blogId,title,content,tag,pdate) values(%(logNo)s,%(blogId)s,%(title)s,%(content)s,%(tag)s,%(pdate)s)"
    try:
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('************************** Exception **************************')
        traceback.print_exc()
        
def update_status(blog_url):    
    cnx = mysql.connector.connect(user=user, password=password,host=host,port=port,database= database, charset='utf8')     
    cursor = cnx.cursor()  
    
    sql = "update blog_list set blog_status = 1 where blog_url='"+str(blog_url)+"'"
    print(sql)
    try:
        cursor.execute(sql,blog_url)
        cnx.commit()
    except: 
        print('************************** Exception **************************')
        traceback.print_exc()
        
def update_status_v2(blog_url):    
    cnx = mysql.connector.connect(user=user, password=password,host=host,port=port,database= database, charset='utf8')     
    cursor = cnx.cursor()  
    
    sql = "update blog_list set blog_status = 2 where blog_url='"+str(blog_url)+"'"
    print(sql)
    print("===============================================================\n")
    try:
        cursor.execute(sql,blog_url)
        cnx.commit()
    except: 
        print('************************** Exception **************************\n')
        traceback.print_exc()     

cnx = mysql.connector.connect(user=user, password=password,host=host,port=port,database=database) 
cursor = cnx.cursor()

sql = "select blog_url,blog_title,blog_date from blog_list where blog_status = 0 order by rand()"
cursor.execute(sql)

for url in cursor:
    if 'blog.naver.com' in url[0] :  
        blogId = url[0].split('/')[3]
        logNo = url[0].split('/')[4]   
        nexturl = 'https://blog.naver.com//PostView.nhn?blogId=' + blogId + '&logNo=' + logNo + '&redirect=Dlog&widgetTypeCall=true&directAccess=false'
        print(nexturl)
        crawler(url[0], nexturl, blogId, logNo, url[1], url[2])
    
    elif 'blog.me' in url[0] : 
        blogId = url[0].split('/')[2].split('.')[0]
        logNo = url[0].split('/')[3] 
        nexturl = 'https://blog.naver.com//PostView.nhn?blogId=' + blogId + '&logNo=' + logNo + '&redirect=Dlog&widgetTypeCall=true&directAccess=false'
        print(nexturl)
        crawler(url[0], nexturl, blogId, logNo, url[1], url[2])
            
    # http://buyhan.co.kr/221176889287    
    elif 'co.kr' in url[0] : 
        blogId = url[0].split('/')[2].split('.')[0]
        logNo = url[0].split('/')[3] 
        nexturl = 'https://blog.naver.com//PostView.nhn?blogId=' + blogId + '&logNo=' + logNo + '&redirect=Dlog&widgetTypeCall=true&directAccess=false'
        print(nexturl)
        crawler(url[0], nexturl, blogId, logNo, url[1], url[2])
        
    else :
        update_status_v2(url[0])
 
