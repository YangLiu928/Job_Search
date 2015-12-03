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
	q= 'search='
	for index in range (0,len(keywords)):
		if index==0:
			q += keywords[index]
		else:
			q += ('+' + keywords[index])

	l = '&location=' + location

	p = '&page='+ str(page_number)

	url = 'https://www.ziprecruiter.com/candidate/search?' + q + l + p

	return url


def _last_page_reached(soup):
	if soup.find('a', class_ = 'next_prev next'):
		return False
	else:
		return True


def _get_jobs_on_page(soup):
	jobs_on_page = []
	job_divs = soup.find('div',id='job_list').find_all('article')
	for job_div in job_divs:
		job_on_page = {}

		job_title = job_div.find('span', class_ = 'just_job_title').text.strip()
		job_on_page['job_title'] = job_title

		employer = job_div.find('span',itemprop = 'hiringOrganization').find('span',class_ = 'name').text.strip()		
		job_on_page['employer'] = employer


		raw_location = job_div.find('span', itemprop = 'jobLocation').text.strip()
		list = re.findall('[a-zA-Z,]+',raw_location)
		location = ''
		for word in list:
			location += word
			location += ' '
		job_on_page['location'] = location.strip()

		summary= job_div.find('p', class_ = 'job_snippet').text.strip()
		job_on_page['summary'] = summary

		url = job_div.find('a', itemprop = 'url')['href']
		job_on_page['url'] = url

		date = 'zip recriuter does not provide job posted date'
		job_on_page['date'] = date
		job_on_page['source'] = 'ziprecriuter.com'
 
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
#     data = get_job_data(['web','developer'], '22202')

#     with open('ziprecriuter.JSON', 'w') as outfile:
#         json.dump(data, outfile, indent=4)
