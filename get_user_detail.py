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
    sql = "insert into urcosme_reviews(userid,username,prodid,prodname,score,type,season,skin,age,content,effects,reviewid,pageview,likes,pdate) values(%(userid)s,%(username)s,%(prodid)s,%(prodname)s,%(score)s,%(type)s,%(season)s,%(skin)s,%(age)s,%(content)s,%(effects)s,%(reviewid)s,%(pageview)s,%(likes)s,%(pdate)s)"
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

def save_user(data):
    global cnx2
    cursor2 = cnx2.cursor()
    sql = "insert into urcosme_users(userid,nickname,gender,skin,age,horoscope,aboutme,characteristics,places,blogs,magazines) values(%(userid)s,%(nickname)s,%(gender)s,%(skin)s,%(age)s,%(horoscope)s,%(aboutme)s,%(characteristics)s,%(places)s,%(blogs)s,%(magazines)s)"

    try:
        cursor2.execute(sql,data)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def save_user_topics(userid,topics):
    global cnx2
    cursor2 = cnx2.cursor()
    sql = "insert into urcosme_user_topics(userid,topics) values(%(userid)s,%(topics)s)"
    data={'userid':userid,'topics':topics}
    try:
        cursor2.execute(sql,data)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def save_user_brands(userid,brands):
    global cnx2
    cursor2 = cnx2.cursor()
    sql = "insert into urcosme_user_brands(userid,brands) values(%(userid)s,%(brands)s)"
    data={'userid':userid,'brands':brands}
    try:
        cursor2.execute(sql,data)
        cnx2.commit()
    except: 
        print('exception')
        traceback.print_exc()

def myparser(content):
    global logtype
    global userid
    data={}
    soup = BeautifulSoup(content, "html.parser")    

    nickname=soup.find("div",{"class":"nickname"})
    if nickname is None:
        return
    data['userid']=userid
    data['nickname']=nickname.text
    usertable=soup.find("div",{"class":"mbd-about-user-table"})
    rot=list(usertable.children)[1]
    data['gender']=list(list(rot.children)[0].children)[1].text
    data['skin']=list(list(rot.children)[1].children)[1].text
    data['age']=list(list(rot.children)[2].children)[1].text

    m=re.search(r'([\d\.]+)',data['age'])
    if m:
        data['age']=m.group(1)
    else:
        data['age']=-1     
    
    data['horoscope']=list(list(rot.children)[3].children)[1].text

    usertable=soup.find("div",{"class":"mbd-self-intro-show"})
    rot=list(usertable.children)[1]
    print(list(list(rot.children)[0].children)[1].text)
    print(list(list(rot.children)[1].children)[1].text)
    print(list(list(rot.children)[2].children)[1].text)
    print(list(list(rot.children)[3].children)[1].text)
    print(list(list(rot.children)[4].children)[1].text)

    data['aboutme']=list(list(rot.children)[0].children)[1].text
    data['characteristics']=list(list(rot.children)[1].children)[1].text
    data['places']=list(list(rot.children)[2].children)[1].text
    data['blogs']=list(list(rot.children)[3].children)[1].text
    data['magazines']=list(list(rot.children)[4].children)[1].text

    print(data)
    save_user(data)

    usertable=soup.find("div",{"class":"beauty-diary-focus-topic"})
    spans=usertable.find_all("span",{"class":"inline-block"})
    for s in spans:
        save_user_topics(userid,s.text.strip())

    usertable=soup.find("div",{"class":"beauty-diary-focus-brand"})
    if usertable is None:
        return
    spans=usertable.find_all("div",{"class":"mbd-bdfb-item"})
    for s in spans:
        print(s.a.div.text.strip())
        bid=s.a['href'].split("/")[2]
        save_user_brands(userid,bid)
    
    return
    nexturl=soup.find("div",{"class":"user-info"})
    if nexturl is not None:
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
        print(uname.text)

        print(uname.a['href'])
        ids=uname.a['href'].split("/")
        print(ids[2])
        r_prodid=ids[2]

        pname=prodinfo.find("div",{"class":"name"})
        print(pname.text)
        r_prodname=pname.text
    else:
        update_status(reviewid)
        return None

    pageview=soup.find("div",{"class":"ur-pageview"})
    if pageview is not None:
        print(pageview.text)
        m=re.search(r'([\d\.]+)',pageview.text)
        if m:
            r_pageview=m.group(1)
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

logtype='urcosme_user_profile'

cnx = mysql.connector.connect(user=jconfig2.user, password=jconfig2.password,host=jconfig2.host,port=jconfig2.port,database=jconfig2.database) 
cursor = cnx.cursor()
sql = "select userid from urcosme_reviews where userid not in (select userid    from urcosme_users) order by rand()"

cursor.execute(sql)
for (u) in cursor:
    print(u[0])
    userid=str(u[0])

    crawlerutil.log_next("urcosme_user_detail",userid)

    url='https://www.urcosme.com/beauty_diary/'+str(u[0])+'/profile'
    crawlerutil.crawl_and_savenext(logtype,url,myparser)
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


