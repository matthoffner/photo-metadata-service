import sys
import re, requests, json, codecs
from urlparse import urlparse
from bs4 import BeautifulSoup as bs
from flask import Flask, Response, json, make_response, render_template, request, jsonify
from PIL import Image
from PIL.ExifTags import TAGS
import urllib

app = Flask(__name__)

@app.route('/meta/',methods = ['GET','POST'])
def get_meta():
	content = request.json
	f = open('00000001.jpg','wb')
	f.write(urllib.urlopen(content['url']).read())
	f.close()
	filename = '00000001.jpg'
	result = get_exif(filename)
	return jsonify(result)

def get_exif(fn):
	ret = {}
	i = Image.open(fn)
	info = i._getexif()
	for tag, value in info.items():
		decoded = TAGS.get(tag, tag)
		ret[decoded] = value
	return ret

@app.route('/tags/', methods = ['POST'])
def get_tags():
	imagga_url = "http://api.imagga.com/v1/tagging"
	content = request.json
	print content
	url = content['url']
	querystring = {"url":url,"version":"2"}
	headers = { 'accept': "application/json",'authorization': "Basic YWNjXzM4ZDRkNzgxOGRlYmMwNDoxZWVlZjY0ZThiMWQzMGYxZmRkODgxOTkxOGViOGI1Yg=="}
	response = requests.request("GET", imagga_url, headers=headers, params=querystring)
	return response.text
	
if __name__ == '__main__':
	app.debug = True
	app.run()
