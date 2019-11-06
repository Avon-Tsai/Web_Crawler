#!/usr/bin/python3
# -*- coding: utf-8 -*-
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

cnx = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 
cnx2 = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36'}

def SaveContentToFile(content):
    fw=codecs.open("content.html","w","utf-8")
    print ( type(content) )
    fw.write(content)
    fw.close()

def getcontent(myurl):
    res = r.get(myurl,headers=headers)
    res.encoding='utf-8'
    SaveContentToFile(res.text)    
    content=res.text.encode('utf-8')
    return content

def save_brand(pixid,brand):
    global cnx
    cursor = cnx.cursor()
    sql = "insert into urcosme_brands(pixid,brand) values(%(pixid)s,%(brand)s)"
    data={'pixid':pixid,'brand':brand}
    try:
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('exception')
        traceback.print_exc()

def save_prod(prodid,pdate,name,ucpoint,reviews,price,likes,buy,cate,brandid,channel,pageview):
    global cnx2
    print(prodid)
    cursor2 = cnx2.cursor()
    sql = "insert into urcosme_prods(prodid,pdate,name,ucpoint,reviews,price,likes,buy,category,brandid,channel,pageview) values(%(prodid)s,%(pdate)s,%(name)s,%(ucpoint)s,%(reviews)s,%(price)s,%(likes)s,%(buy)s,%(cate)s,%(brandid)s,%(channel)s,%(pageview)s) ON DUPLICATE KEY UPDATE pageview=%(pageview)s,likes=%(likes)s,buy=%(buy)s"

    data={'prodid':str(prodid),'pdate':pdate,'name':name,'ucpoint':ucpoint,'reviews':reviews,'price':price,'likes':likes,'buy':buy,'cate':cate,'brandid':brandid,'channel':channel,'pageview':pageview}
    if len(pdate.strip())<=3:
        data['pdate']='1900-01-01'
    try:
        print(data)
        cursor2.execute(sql,data)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def save_next(url):
    global cnx
    cursor = cnx.cursor()
    sql = "insert into urcosme_prods(prodid,pdate,name,ucpoint,reviews,price,likes,buy) values(%(prodid)s,%(pdate)s,%(name)s,%(reviews)s,%(price)s,%(likes)s,%(buy)s)"

    data={'prodid':str(prodid),'pdate':pdate,'name':name,'ucpoint':ucpoint,'reviews':reviews,'price':price}
    try:
        print(data)
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('exception')
        traceback.print_exc()

def update_cate():
    global cnx
    global cate
    cursor = cnx.cursor()
    sql = "update urcosme_prods set category=%(cate)s where category is NULL"

    data={'cate':cate}
    try:
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('exception')
        traceback.print_exc()

def myparser(content):
    global prodid
    global logtype
    brandid=''

    m=re.search("content_category\: '(.+?)',",content.decode('utf-8'))
    if m:
        print(m.group(1))
        cate=m.group(1)

    m=re.search("level_channel\: '(.+?)'",content.decode('utf-8'))
    if m:
        print(m.group(1))
        channel=m.group(1)
    soup = BeautifulSoup(content, "html.parser")

    nexturl=soup.find("a",{"class":"brand-focus-small-button"})
    if nexturl is not None:
        m=re.search('brand_id\=(\d+)',nexturl['data-redirect'])
        if m:
            brandid=m.group(1).strip()

    pageview=soup.find("div",{"class":"ur-pageview"})
    if pageview is not None:
        print(pageview.text)
        m=re.search(r'([\d\.]+)',pageview.text)
        if m:
            r_pageview=m.group(1)
            if ('k' in pageview.text):
                r_pageview=float(r_pageview.strip())*1000
            print(r_pageview)
        else:
            r_pageview=-1

    nexturl=soup.find("div",{"class":"info-tbl"})
    if nexturl:
        pdate=list(nexturl.children)[5].find("span").text.strip()
        print( pdate)
        iname=list(list(nexturl.children)[0].children)[1].text.strip()
        print( iname)
        price=list(nexturl.children)[4].find("span").text.strip()
        print( price)

    nexturl=soup.find("div",{"class":"deg"})
    ucpoint=list(nexturl.children)[1].text.strip()
    if "-" in ucpoint:
        ucpoint=-1

    nexturl=soup.find("div",{"class":"stat-text"})
    elmts=nexturl.text.split("/")
    m=re.search(r'(\d+)',elmts[0])
    if m:
        likes=m.group(1).strip()
    m=re.search(r'(\d+)',elmts[1])
    if m:
        buy=m.group(1).strip()
    print(likes)
    print(buy)

    nexturl=soup.find("div",{"class":"content-menu user-opinion-search-final"})
    nexturl=nexturl.find("div",{"class":"outer"})
    reviews=list(nexturl.children)[1]
    m=re.search(r'(\d+)',reviews.text)
    if m:
        reviews=m.group(1).strip()

    print(reviews)
    print(brandid)
    try:
        cate
    except NameError:
        cate=''
    save_prod(prodid,pdate,iname,ucpoint,reviews,price,likes,buy,cate,brandid,channel,r_pageview)
    return
 
logtype='urcosme_review_prods'
prodid=0

cnx = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 
cursor = cnx.cursor()
sql = "SELECT distinct prodid FROM urcosme_prods where pageview is NULL order by rand()"

cursor.execute(sql)
for (u) in cursor:
    prodid=str(u[0])
    crawlerutil.crawl_and_savenext(logtype,'https://www.urcosme.com/products/'+str(u[0]),myparser)

