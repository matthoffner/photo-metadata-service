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
	global result
	content = request.json
	f = open('00000001.jpg','wb')
	f.write(urllib.urlopen(content['url']).read())
	f.close()
	filename = '00000001.jpg'
	result = get_lat_long(filename)
	return jsonify(result)

def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None
	
def _convert_to_degress(value):
    """Helper function to convert the GPS coordinates stored in the EXIF to degress in float format"""
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)


def get_lat_lon(fn):

	exif_data = {}
	i = Image.open(fn)
	info = i._getexif()
	for tag, value in info.items():
		decoded = TAGS.get(tag, tag)
		exif_data[decoded] = value

	lat = None
	lon = None
	if "GPSInfo" in exif_data:		
		gps_info = exif_data["GPSInfo"]

	gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
	gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
	gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
	gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

	if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
		lat = _convert_to_degress(gps_latitude)
		if gps_latitude_ref != "N":                     
			lat = 0 - lat

		lon = _convert_to_degress(gps_longitude)
		if gps_longitude_ref != "E":
			lon = 0 - lon

	payload = {}
	payload[lat] = lat
	payload[lon] = lon
	return payload


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
