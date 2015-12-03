import urllib2
from bs4 import BeautifulSoup
import json
import re
import lxml
import re

def _get_soup(url):
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	response = opener.open(url)
	soup = BeautifulSoup(response.read(),'lxml')
	return soup


def _get_indeed_query_url(keywords,location,page_number):
	# keywords is a list of words you input in a search bar for 
	# a search in indeed.com

	# q represents the q part (keywords) in the search url
	q = 'q='
	for index in range (0,len(keywords)):
		if index==0:
			q += keywords[index]
		else:
			q += ('+' + keywords[index])

	# l represents the location part in the search url
	l = '&l=' + location

	# start somewhat represents the current number of page in the result
	# eg. start = 0 for page 1, start = 10 for page 2 etc.
	# typically, indeed only gives 100 pages of results
	# therefore the maximum value for start is 990
	# there could aslo be an exception (which I haven't found yet)
	# but we can use some other mechanism to see if we have reached the last page
	pn = '&start='+ str(page_number)

	# this is the url to be put in the browser
	url = 'http://www.simplyhired.com/search?' + q + l + pn

	return url


def _last_page_reached(soup):
	if soup.find('a', class_ = 'evtc next-pagination'):
		return False
	else:
		return True


def _get_jobs_on_page(soup):
	jobs_on_page = []
	job_divs = soup.find_all('div', class_ = 'card js-job')
	for job_div in job_divs:
		job_on_page = {}

		job_title = job_div.find('h2', class_ = 'serp-title').text.strip()
		job_on_page['job_title'] = job_title

		employer = job_div.find_all('span', class_ = 'serp-company')[0].text.strip()		
		job_on_page['employer'] = employer


		location = job_div.find('span', class_ = 'serp-location').text.strip()
		words = re.findall('[a-zA-Z,]+',location)
		location =''
		for word in words:
			location+=word
			location+=' '
		job_on_page['location'] = location.strip()

		summary= job_div.find('p', class_ = 'serp-snippet').text.strip()
		job_on_page['summary'] = summary

		# get the job url, for indeed.com I cannot figure it out yet
		url = 'http://www.simplyhired.com'
		url += job_div.find('a', class_ = 'card-link js-job-link')['href']
		job_on_page['url'] = url

		# get the posted time
		date = job_div.find('span', class_ = 'serp-timestamp').text.strip()
		job_on_page['date'] = date
		job_on_page['source'] = 'simplyhired.com'
 
		jobs_on_page.append(job_on_page)

	return jobs_on_page


def get_job_data(keywords,location):
	# this function is intended to return the job listing basing on 
	# location and keywords as a python list
	# the index of a job in this list is essentially its order in the 
	# search results
	jobs = []

	# we start off at page one
	page_number = 1

	while True and page_number<10:
		url = _get_indeed_query_url(keywords,location,page_number)
		soup = _get_soup(url)
		if _last_page_reached(soup):
			print 'last page of results reached at ' + url
			print 'last page number is ' + str(page_number)
			break
		else:
			jobs_on_page = _get_jobs_on_page(soup)
			for job_on_page in jobs_on_page:
				jobs.append(job_on_page)
			page_number += 1

	return jobs


# if __name__ == '__main__':
#     data = get_job_data(['web','developer'], '22202')

#     with open('simplyhired.JSON', 'w') as outfile:
#         json.dump(data, outfile, indent=4)
