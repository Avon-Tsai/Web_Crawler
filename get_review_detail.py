#!/usr/bin/python3.4
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
from dateutil.parser import parse

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

def update_status(reviewid):
    global cnx2
    cursor2 = cnx2.cursor()

    sql = "update urcosme_review_list set cstatus=1 where reviewid='"+str(reviewid)+"'"
    try:
        cursor2.execute(sql)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def save_review_detail(data):
    global cnx2
    cursor2 = cnx2.cursor()
    sql = "insert into urcosme_reviews(userid,username,prodid,prodname,score,type,season,skin,age,content,effects,reviewid,pageview,likes,pdate) values(%(userid)s,%(username)s,%(prodid)s,%(prodname)s,%(score)s,%(type)s,%(season)s,%(skin)s,%(age)s,%(content)s,%(effects)s,%(reviewid)s,%(pageview)s,%(likes)s,%(pdate)s) ON DUPLICATE KEY UPDATE userid=%(userid)s,username=%(username)s,prodid=%(prodid)s,prodname=%(prodname)s,score=%(score)s,type=%(type)s,season=%(season)s,skin=%(skin)s,age=%(age)s,content=%(content)s,effects=%(effects)s,pageview=%(pageview)s,likes=%(likes)s,pdate=%(pdate)s "
    try:
        cursor2.execute(sql,data)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

    sql = "update urcosme_review_list set cstatus=1 where reviewid=%(reviewid)s"
    try:
        cursor2.execute(sql,data)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def save_next(url):
    global cnx
    cursor = cnx.cursor()
    sql = "insert into urcosme_prods(prodid,pdate,name,ucpoint,reviews,price,pageview,likes,pdate) values(%(prodid)s,%(pdate)s,%(name)s,%(ucpoint)s,%(reviews)s,%(price)s,%(pageview)s,%(likes)s,%(pdate)s)"

    data={'prodid':str(prodid),'pdate':pdate,'name':name,'ucpoint':ucpoint,'reviews':reviews,'price':price}
    try:
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('exception')
        traceback.print_exc()

def myparser(content):
    global logtype
    global reviewid
    soup = BeautifulSoup(content, "html.parser")    
    nexturl=soup.find("div",{"class":"user-info"})
    if nexturl is not None:
        uname=nexturl.find("div",{"class":"user-name"})
        if uname is None:
            return
        print(uname.text)
        print(uname.a['href'])
        ids=uname.a['href'].split("/")
        print(ids[2])
        r_username=uname.text
        r_userid=ids[2]
        if len(r_username.split()) <=0:
            update_status(reviewid)
            return None
    else:
        update_status(reviewid)
        return None
    prodinfo=soup.find("div",{"class":"product-info"})
    if prodinfo is not None:
        uname=prodinfo.find("div",{"class":"img-brand"})
        if uname is None:
            update_status(reviewid)
            return None
            
        print(uname.text)

        print(uname.a['href'])
        ids=uname.a['href'].split("/")
        print(ids[2])
        r_prodid=ids[2]

        pname=prodinfo.find("div",{"class":"name"})
        print(pname.text)
        r_prodname=pname.text
    else:
        print(reviewid)
        update_status(reviewid)
        return None

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
    
    urlike=soup.find("div",{"class":"ur-like"})
    if urlike is not None:
        print(urlike.text)
        m=re.search(r'([\d\.]+)',urlike.text)
        if m:
            r_like=m.group(1)
            print(r_like)
        else:
            r_like=-1

    urdate=soup.find("div",{"class":"review-date"})
    if urdate is not None:
        print(urdate.text)
        dstr=urdate.text.split("發表")[0]
        print(dstr)
        r_date=parse(dstr)

    descinfo=soup.find("div",{"class":"desc-block"})
    if descinfo is not None:
        score=descinfo.find("div",{"class":"score"})
        print(score.text)
        m=re.search(r'([\d\.]+)',score.text)
        if m:
            r_score=m.group(1)
            print(r_score)
        else:
            r_score=-1
        type=descinfo.find("div",{"class":"type"})
        print(type.text)
        r_type=type.text
        season=descinfo.find("div",{"class":"season"})
        print(season.text)
        r_season=season.text
        skin=descinfo.find("div",{"class":"skin"})
        print(skin.text)
        r_skin=skin.text
        age=descinfo.find("div",{"class":"age"})
        print(age.text)
        m=re.search(r'([\d\.]+)',age.text)
        r_age=m.group(1)
        print(r_age)
    rcontent=soup.find("div",{"class":"review-content"})
    if rcontent is not None:
        print(rcontent.text)
        r_content=rcontent.text

    reffects=soup.find("div",{"class":"review-effects"})
    if reffects is not None:
        print(reffects.text)
        r_effects=reffects.text
    
    data={'username':r_username,'userid':r_userid,'userid':r_userid,'prodid':r_prodid,'prodname':r_prodname,'score':r_score,'type':r_type,'season':r_season,'skin':r_skin,'age':r_age,'content':r_content,'effects':r_effects,'reviewid':reviewid,'pageview':r_pageview,'likes':r_like,'pdate':r_date}
    save_review_detail(data)

logtype='urcosme_review_detail'

reviewid=0
cnx = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 

cursor = cnx.cursor()
sql = "select reviewid from urcosme_review_list where cstatus=0 order by rand()"

cursor.execute(sql)
for (u) in cursor:
    print(u[0])
    reviewid=str(u[0])
    print("review id")
    print(reviewid)
    crawlerutil.crawl_and_savenext(logtype,'https://www.urcosme.com/reviews/'+str(u[0]),myparser)
    time.sleep(1)

previ=0
cnt=0
while True:
    job=crawlerutil.get_job(logtype)
    url='https://www.urcosme.com'+job
    m=re.search("page=(\d+)",url)
    print(job)
    if m:
        val=m.group(1)
        if previ==val:
            cnt+=1
        else:
            cnt=0
            previ=m.group(1)
    if cnt>=3:
        break
    print(url)
    crawlerutil.crawl_and_savenext(logtype,url,myparser)


