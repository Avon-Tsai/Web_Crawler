# -*- coding: utf-8 -*-

## databse : gsearch.kr_product_detail
## author : Ya Fang Tsai
## date : 2017 / 11 / 28

import requests
import json
import datetime
import traceback

import mysql.connector

def save_product(data):
    cnx = mysql.connector.connect(user='jared', password='iscae100',host='140.96.83.145',port=3306,database='gsearch')
    cursor = cnx.cursor()
    sql = "insert into kr_product_detail(category_code,category_name,prodid,p_created,p_updated,p_name,price,capacity,brandid,b_created,b_updated,b_name,review,score,specNames,tag,rating) values(%(category_code)s,%(category_name)s,%(prodid)s,%(p_created)s,%(p_updated)s,%(p_name)s,%(price)s,%(capacity)s,%(brandid)s,%(b_created)s,%(b_updated)s,%(b_name)s,%(review)s,%(score)s,%(specNames)s,%(tag)s,%(rating)s)"
    
    try:
        cursor.execute(sql,data)
        cnx.commit()
    except: 
        print('exception')
        traceback.print_exc()
        
def myparser(category_code, category_name, category_count):

    if category_count%50 !=0 :
        num = category_count//50 + 1
    else :
        num = category_count//50
    
    for row in range(num) :
        currentCount = row*50
        response = requests.get("http://www.powderroom.co.kr/api/search/products?category="+category_code+"&currentCount="+str(currentCount)).json()
    
        for pro in range(len(response)): # len(response)
            res = response[pro]  
            data = {}

            data['category_code'] = category_code
            data['category_name'] = category_name
            data['prodid'] = res['$id']
            print(data['prodid'])
        
            data['p_created'] = datetime.datetime.fromtimestamp(res['$created'] / 1e3)
            data['p_updated'] = datetime.datetime.fromtimestamp(res['$updated'] / 1e3)
            data['p_name'] = res['name']

            try :
                data['price'] = res['sizes'][0]['price']
            except:
                data['price'] = 0
            
            try :
                data['capacity'] = res['sizes'][0]['capacity']
            except:
                data['capacity'] = ''

            data['brandid'] = res['brand']['$id']
            data['b_created'] = datetime.datetime.fromtimestamp(res['brand']['$created'] / 1e3)
            data['b_updated'] = datetime.datetime.fromtimestamp(res['brand']['$updated'] / 1e3)
            data['b_name'] = res['brand']['name']
            data['review'] = res['count']['review']
            data['score'] = res['score']
            
            prod = requests.get("https://www.powderroom.co.kr/api/products/"+ str(data['prodid'])).json()
            try :
                data['specNames'] = str(prod['specNames'])
            except :
                data['specNames'] = ''
            data['tag'] = str(prod['summary']['hashtags'])
            data['rating'] = str(prod['summary']['count']['ratings'])
            
            save_product(data)   
            
## category
cate = {}
response = requests.get("https://www.powderroom.co.kr/api/products/categories?$search=1").json()
for row in range(len(response)) :
    sub_cate = response[row]['subCategories']
    for sub in range(len(sub_cate)) :
        try: 
            sub_cate_2 = sub_cate[sub]['subCategories']
            for sub_2 in range(len(sub_cate_2)) :
                category_code = sub_cate_2[sub_2]['code']
                category_name = sub_cate_2[sub_2]['name']
                category_count = sub_cate_2[sub_2]['count']
                
                myparser(category_code, category_name, category_count)
        except:
            category_code = sub_cate[sub]['code']
            category_name = sub_cate[sub]['name']
            category_count = sub_cate[sub]['count']  

            myparser(category_code, category_name, category_count)

