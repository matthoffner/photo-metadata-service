import requests
import json
from multiprocessing import Pool

def extract(image_url):
	source = requests.post("http://localhost:5000/images/",data=json.dumps({'url': image_url}),headers={'Content-Type': 'application/json'})
	print source.content

if __name__ == '__main__':
	p = Pool(1)
	#flat_file = "image_links.csv"
	#image_url = [line for line in flat_file]
	image_url = ["http://www.findexif.com/client/samples/iguana.jpg","http://www.findexif.com/client/samples/swiss_view.jpg"]
	p.map(extract,image_url)

