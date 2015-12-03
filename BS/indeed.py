import urllib2
from bs4 import BeautifulSoup
import json
import re
import lxml

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
	start = '&start='+ str((page_number-1)*10)

	# sort tells how the results should be sorted in the result
	# if the value of order_by is 'date' then the job results are sorted by date
	# otherwise it is sorted by 'relevance', which I don't know how they rank them
	# sort = ''
	# if order_by == 'date':
	# 	sort = '&sort=date'

	# this is the url to be put in the browser
	url = 'http://www.indeed.com/jobs?' + q + l + start

	return url


def _last_page_reached(soup):
	# if we reached the last page
	# the 'Next' anchor tag should not appear
	# therefore this can be used as an indicator of whether the last page has been reached
	pagination = soup.find('div', class_ = 'pagination')
	anchors = pagination.find_all('a')
	if anchors[-1].find('span', recursive = False).find('span',class_ = 'np'):
		# the 'Next' clickable was found
		return False
	else:
		return True


def _get_jobs_on_page(soup):
	jobs_on_page = []
	job_divs = soup.find_all('div', class_ = 'row')
	for job_div in job_divs:
		# job is a dictionary
		job_on_page = {}
		
		# get the job title
		# structure like <h2><a>Java <b>web</b> developer</a></h2>

		job_title = job_div.find('a', target = '_blank').text.strip()
		job_on_page['job_title'] = job_title

		# get the employer
		# the employer could either be an anchor tag with the following structure
		# <span class = 'company'><a>name</a></span>
		# or a plain text with the following structure
		# <span class = 'company'><span itemprop = 'name'>name</span></span>
		# or just one layer of span tag..
		# <span class = 'company'> name </span>

		employer = job_div.find('span', class_ = 'company').text.strip()
		# employer_span = job_div.find('span', class_ = 'company')
		# if employer_span.find('a'):
		# 	employer = employer_span.find('a').string
		# elif employer_span.find('span'):
		# 	employer = employer_span.find('span').string
		# else:
		# 	employer = employer_span.find('span').strin			
		job_on_page['employer'] = employer

		# get the location
		location = job_div.find('span', class_ = 'location').text.strip()
		job_on_page['location'] = location

		if not location:
			print employer

		# get the summary
		summary= job_div.find('span', class_ = 'summary').text.strip()
		job_on_page['summary'] = summary

		# get the job url, for indeed.com I cannot figure it out yet
		url = 'http://www.indeed.com' + job_div.find('a')['href']
		job_on_page['url'] = url

		# get the posted time
		date = job_div.find('span', class_ = 'date').text.strip()
		# if re.search('hour', date):
		# 	date = '0'
		# elif re.search('[0-9]+',date):
		# 	date = re.search('[0-9]+',date).group()
		# else:
		# 	print date
		# 	date = '0'
		job_on_page['date'] = date

		job_on_page['source'] = 'indeed.com'

 
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

	while page_number<10:
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
#     data = get_job_data(['web','developer'], 'Vienna', 'date')

#     with open('indeed.JSON', 'w') as outfile:
#         json.dump(data, outfile, indent=4)
