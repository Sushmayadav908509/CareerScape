import os
import sys
DJANGO_PROJECT_PATH = r"C:\Users\Sushma Yadav\OneDrive\Desktop\CareerScape\CareerScape"
sys.path.append(DJANGO_PROJECT_PATH)
os.environ['DJANGO_SETTINGS_MODULE']='CareerScape.settings'
import django
django.setup()

import scrapy
from urllib.parse import urlencode, urljoin, unquote
from job_scrapy.items import JobScrapyItem
from job_scrapy.settings import SCRAPEOPS_API_KEY
from datetime import datetime
from time import sleep
from job_scrapy.scrapy_utils import extract_job_info
import json
import re



KEY = SCRAPEOPS_API_KEY
JOBS = ['fresher']
LOCATIONS = ['Panvel']

def get_scrapeops_url(url):
    payload = {'api_key': KEY, 'url': url}
    proxy_url = 'https://proxy.scrapeops.io/v1/?' + urlencode(payload)
    return proxy_url


class JobspiderSpider(scrapy.Spider):
    name = "jobspider"

    def start_requests(self):
        for job in JOBS:
            for location in LOCATIONS:
                search_url = f"https://in.indeed.com/jobs?q={job}&l={location}&fromage=1"
                yield scrapy.Request(search_url, callback=self.parse)

    def parse_final_link(self, response):
        item = JobScrapyItem()
        json_data = response.css('script[type="application/ld+json"]::text').get()
        if not json_data:
            self.logger.info(f"\n \n No JSON data found in {response.url}. Skipping this page.\n \n")
            return

        try:
            data = json.loads(json_data)
            job_info = extract_job_info(data)
            item.update(job_info)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON data for {response.url}")

        raw_url = response.url
        pattern = 'jk=([a-zA-Z0-9]{16})'
        jobid_match = re.search(pattern, raw_url)
        jobid=''
        # pattern = 'fccid=(.*?)&vjs=3'
        # pattern = 'fccid=(.*?)&cmp='
        if jobid_match:
            jobid = jobid_match.group(1)
            print(jobid)

        item['url'] = response.url
        item['jobid'] = jobid
        title = response.css('h1.jobsearch-JobInfoHeader-title span::text').get()
        company_name = response.css('div[data-testid="inlineHeader-companyName"] a::text').get()
        company_location = response.css('div[data-testid="jobsearch-JobInfoHeader-companyLocation"] span::text').get()
        item['job_title'] = title
        item['company_name'] = company_name
        item['company_location'] = company_location
        yield item


    def parse(self, response):
        widget_links = response.css('div.job_seen_beacon a.jcs-JobTitle::attr(href)').extract()
        print('widget_links :-',widget_links)

        for widget_link in widget_links:
            widget_url = response.urljoin(widget_link)
            proxy_widget_url = get_scrapeops_url(widget_url)
            original_widget_url = unquote(proxy_widget_url)

            print(f'\nFinal Widget Url : {original_widget_url}\n')

            x = '&url='
            if x in original_widget_url:
                final_link = original_widget_url.split(x)[1]
                print(f'\nFinal Widget Url : {final_link}\n')

                yield scrapy.Request(final_link, callback=self.parse_final_link, meta={'delay': 10})
                

        pagination_links = response.css('nav[aria-label=pagination] a::attr(href)').extract()
        for next_page in pagination_links:
            if next_page:
                yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)
            else:
                self.logger.info("Reached last page. No pagination links further")

