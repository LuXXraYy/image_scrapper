from flask import Flask,render_template,request,jsonify
from flask_cors import CORS, cross_origin
import os
import time
import csv
from bs4 import BeautifulSoup as bs
import requests
from urllib.request import urlopen as uReq
from selenium import webdriver
from selenium.webdriver.common.by import By
import pymongo

app = Flask(__name__)

@app.route("/", methods=['GET'])
# @cross_origin()
def homepage():
    return render_template("index.html") 

@app.route("/results", methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # search String
            searchString = request.form['content'].replace(" ", "")

            # Saving Directory
            save_dir = f"images/{searchString}"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Create fake user agent so that google doesn't block us.
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            
            # fetch the url body
            url_body = requests.get(f"https://www.google.com/search?q={searchString}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")

            # url/img html
            img_html = bs(url_body.content, "html.parser")

            # Extract img tag
            img_tags = img_html.find_all("img")

            # delete the first image as it is logo 
            del img_tags[0]

            # Storing Images 
            img_data_store = []
            for images in img_tags:
                img_url = images['src']
                img_data = requests.get(img_url).content
                mydict = {"index": img_tags.index(images), "url": img_url, "image_data": img_data}
                img_data_store.append(mydict)
                with open(os.path.join(save_dir, f"{searchString}_{img_tags.index(images)}.jpg"), "wb") as f:
                    f.write(img_data)

            
            client = pymongo.MongoClient("mongodb+srv://hrithik2406:Awi2406@cluster0.kwjgqgn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            db = client['image_scrapper']
            review_col = db['image_scrapper_data']
            review_col.insert_many(img_data_store)


            return render_template('results.html', reviews=img_data_store[0:len(img_data_store)])

        except Exception as e:
            print(e)
            return "Something is Wrong"
    else:
        return render_template("index.html")
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)