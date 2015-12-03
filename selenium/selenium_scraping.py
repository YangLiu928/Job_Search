from selenium import webdriver
import os
import time
from bs4 import BeautifulSoup
import lxml
import json
import re



# open up the browser and navigate to the hompage of careerbuilder.com
career_builder_base_url = 'http://www.careerbuilder.com/?cbRecursionCnt=1'
phantomjs_path = '../phantomjs-2.0.0-windows/bin/phantomjs.exe'
# browser = webdriver.Firefox()
# browser = webdriver.Chrome('../chromedriver_win32/chromedriver.exe')

browser = webdriver.PhantomJS(executable_path=phantomjs_path, service_log_path=os.path.devnull)
browser.implicitly_wait(10)
browser.get(career_builder_base_url)

# locate the input fields and search buttons
keywords_input = browser.find_element_by_id('search-key')
location_input = browser.find_element_by_id('search-loc')
search_button = browser.find_element_by_id('search-button')

keywords = 'java'
location = '22304'

# start the search
keywords_input.send_keys(keywords)
location_input.send_keys(location)
search_button.click()
print 'search button clicked'
# since we do not know which element loads the last
# we explicitly wait 5 seconds after the search button was hit

# click the appropriate 'sort by' button
sort_by_job_title_button = browser.find_element_by_id('SortBox1_JobTitleSort')
sort_by_location_button = browser.find_element_by_id('SortBox1_cbhlDist')
sort_by_relevance_button = browser.find_element_by_id('SortBox1_cbhlKey')
sort_by_date_button = browser.find_element_by_id('SortBox1_cbhlDate')
sort_by_date_button.click()
# print 'sort button clicked'

# we should have now reached the first page in the results
# we should now grab the html in all result pages
# first we take the page source and append it to the htmls list
# then try to find the next button (anchor tag actually)
# if next button found, we click on it and repeat the process above
# if next button not found, we have reached the last page of possible results
# we therefore break out of the while loop
htmls = []
while True:
	for i in range (0,100):
		browser.execute_script("window.scrollBy(0,100);")
		time.sleep(0.03)
	# # time.sleep(3)
	# # give the page 3 seconds to fully load
	htmls.append(browser.page_source)
	try:
		print 'trying to click a next button'
		next_button = browser.find_element_by_class_name('JL_MXDLPagination2_next')
		next_button.click()
		print 'next button clicked'
	except:
		print 'failed to click next button'
		break

# we are now done with the selenium and the webdrivers
# do not forget to close the webdriver
browser.close()

jobs=[]

for html in htmls:
	print 'new html source parsed'
	soup = BeautifulSoup(html, 'lxml')
	table = soup.find('table', id = 'NJL_ND')
	# recursive = False because there are nested tables
	# if recursive = True, it will drill down to more than one level
	# which is not what we want
	rows = table.find_all('table')
	jobs_on_page = []
	for row in rows:
		print 'new job added'
		job_on_page={}
		
		try:
			title = row.find('h2', itemprop='title').text.strip()
		except:
			title = 'failed'
		job_on_page['title'] = title
		
		try:
			summary = row.find('span',id=re.compile('NJL_ND__ctl[0-9]+_[a-z]+Teaser')).text.strip()
		except:
			summary = 'failed'
		job_on_page['summary'] = summary

		try:
			if row.find(id=re.compile('NJL_ND__ctl[0-9]+_[a-z]+Company')):
				employer = row.find(id=re.compile('NJL_ND__ctl[0-9]+_[a-z]+Company')).text.strip()
			else:
				employer = None
		except:
			employer = 'failed'
		job_on_page['employer'] = employer

		try:
			location = row.find(id=re.compile('NJL_ND__ctl[0-9]+_[a-z]+Location')).text.strip()
		except:
			location = 'failed'
		job_on_page['location'] = location

		try:
			date = row.find(id=re.compile('NJL_ND__ctl[0-9]+_[a-z]+Posted')).text.strip()
		except:
			date = 'failed'
		
		job_on_page['date'] = date

		jobs_on_page.append(job_on_page)

	jobs += jobs_on_page


with open('careerbuilder.JSON', 'w') as outfile:
    json.dump(jobs, outfile, indent=4)
