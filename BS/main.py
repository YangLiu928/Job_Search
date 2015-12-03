import indeed
import simplyHired
import ziprecriuter
import json
import pandas


def get_jobs(keywords,zip_code):
	indeed_jobs = indeed.get_job_data(keywords,zip_code)
	simplyHired_jobs = simplyHired.get_job_data(keywords,zip_code)
	ziprecriuter_jobs = ziprecriuter.get_job_data(keywords,zip_code)
	jobs = []
	ids =set()
	max_len = max([len(indeed_jobs),len(simplyHired_jobs),len(ziprecriuter_jobs)])
	for index in range(0,max_len):
		if index<len(indeed_jobs):
			if not indeed_jobs[index]['employer']+indeed_jobs[index]['job_title'] in ids:
				ids.add(indeed_jobs[index]['employer']+indeed_jobs[index]['job_title'])
				jobs.append(indeed_jobs[index])
		if index<len(simplyHired_jobs):
			if not simplyHired_jobs[index]['employer']+simplyHired_jobs[index]['job_title'] in ids:
				ids.add(simplyHired_jobs[index]['employer']+simplyHired_jobs[index]['job_title'])
				jobs.append(simplyHired_jobs[index])
		if index<len(ziprecriuter_jobs):
			if not ziprecriuter_jobs[index]['employer']+ziprecriuter_jobs[index]['job_title'] in ids:
				ids.add(ziprecriuter_jobs[index]['employer']+ziprecriuter_jobs[index]['job_title'])
				jobs.append(ziprecriuter_jobs[index])
	return jobs


if __name__ == '__main__':
	keywords = ['java']
	zip_code = '22304'
	jobs = get_jobs(keywords,zip_code)
	# with open('jobs_duplicate_removed.JSON', 'w') as outfile:
	#     json.dump(jobs, outfile, indent=4)

	df = pandas.DataFrame(jobs)
	print df[['employer','location']]