import sys
import re, requests, json, codecs
from urlparse import urlparse
from bs4 import BeautifulSoup as bs
from flask import Flask, Response, json, make_response, render_template, request, jsonify
import urllib
import sys
import pytz, datetime
from pygeocoder import Geocoder
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

app = Flask(__name__)


@app.route('/images/',methods = ['GET','POST'])
def extract_photo():
	payload = {}
	content = request.json
	f = open('00000001.jpg','wb')
	f.write(urllib.urlopen(content['url']).read())
	f.close()
	filename = '00000001.jpg'
	image = Image.open(filename)
	exif_data = get_exif_data(image)
	coordinates = get_lat_lon(exif_data)
	payload['coordinates'] = str(coordinates)
	timestamp = get_timestamp(exif_data)
	payload['timestamp'] = str(timestamp)
	address = reverse_geocode(coordinates)
	payload['address'] = str(address)
	print payload
	return jsonify(payload)


def get_exif_data(image):
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[sub_decoded] = value[gps_tag]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value
    return exif_data


def _convert_to_degress(value):
    deg_num, deg_denom = value[0]
    d = float(deg_num) / float(deg_denom)

    min_num, min_denom = value[1]
    m = float(min_num) / float(min_denom)

    sec_num, sec_denom = value[2]
    s = float(sec_num) / float(sec_denom)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data):
    lat = None
    lon = None
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        gps_latitude = gps_info.get("GPSLatitude")
        gps_latitude_ref = gps_info.get('GPSLatitudeRef')
        gps_longitude = gps_info.get('GPSLongitude')
        gps_longitude_ref = gps_info.get('GPSLongitudeRef')
        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":
                lat *= -1
            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon *= -1
    payload = {}
    payload['lat'] = lat
    payload['lon'] = lon
    return payload


def get_altitude(exif_data):
    alt = None
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        gps_altitude = gps_info.get('GPSAltitude')
        gps_altitude_ref = gps_info.get('GPSAltitudeRef')
        if gps_altitude:
            alt = float(gps_altitude[0]) / float(gps_altitude[1])
            if gps_altitude_ref == 1:
                alt *=-1
    return alt

def reverse_geocode(coordinates):
	results = Geocoder.reverse_geocode(coordinates['lat'],coordinates['lon'])
	return results

def get_timestamp(exif_data):
    dt = None
    utc = pytz.utc
    if "GPSInfo" in exif_data:
        gps_info = exif_data["GPSInfo"]
        gps_time_stamp = gps_info.get('GPSTimeStamp')
        if 'GPSDateStamp' in gps_info:
            gps_date = [int(i) for i in gps_info['GPSDateStamp'].split(':')]
        elif 29 in gps_info:
            gps_date = [int(i) for i in gps_info[29].split(':')]
        else:
            gps_date = None
        if gps_time_stamp and gps_date:
            yy = gps_date[0]
            mm = gps_date[1]
            dd = gps_date[2]
            h = int(float(gps_time_stamp[0][0]) / float(gps_time_stamp[0][1]))
            m = int(float(gps_time_stamp[1][0]) / float(gps_time_stamp[1][1]))
            s = int(float(gps_time_stamp[2][0]) / float(gps_time_stamp[2][1]))
            dt = utc.localize(datetime.datetime(yy,mm,dd,h,m,s))
    return dt

	
if __name__ == '__main__':
	if len(sys.argv) < 2:
		print "Launching service..."
		app.debug = True
		app.run()
	image = Image.open(sys.argv[1])
	exif_data = get_exif_data(image)
	coordinates = get_lat_lon(exif_data)
	print coordinates
	timestamp = get_timestamp(exif_data)
	print timestamp
	address = reverse_geocode(coordinates)
	print address
