'''
Created on 23-Jun-2015

@author: niloygupta
'''

import sys
from bs4 import BeautifulSoup
import urllib2 

# Gets the specific filters available on the Pinterest page
def get_subtopics(soup):
    guideText = soup.findAll('span', {"class":"guideText"})
    
    sub_topics = []
    for guide in guideText:
        sub_topics.append(str(guide.contents[0]))
    
    print sub_topics

#Gets the pin attributes for a given query    
def get_pins(soup,query_term):
	pins = soup.findAll('div', {"class":"pinWrapper"})
	image_urls = []
	for pin in pins:
		try:
        		if (pin.find('p',{'class':'pinDescription'})!=None):
            			#pin_description = unicode(str(pin.find('p',{'class':'pinDescription'}).contents[0].encode('utf-8').strip()))
        			pin_img = str(pin.find('div', {"class":"heightContainer"}).img['src'])
				image_urls.append(pin_img)
        	except:
			pass
	print image_urls
        return image_urls

def query_pinterest(query_term='forever21'):
	url = 'https://www.pinterest.com/search/pins/?q='
	query_term = query_term.replace(' ','+')
	url = url + query_term
	#print url
	response = urllib2.urlopen(url)

	html_page = response.read()
	soup = BeautifulSoup(html_page)
	image_links = get_pins(soup,query_term)
	#get_subtopics(soup)
	return image_links

if __name__ == '__main__':
    query_pinterest(sys.argv[1])
