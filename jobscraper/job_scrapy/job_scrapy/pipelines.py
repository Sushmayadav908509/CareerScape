from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy import Spider
from scrapy.exceptions import DropItem
from jobscraper.models import ScrapedData
from asgiref.sync import sync_to_async

class JobScrapyPipeline:
    def process_item(self, item, spider):
        return item

class DatabaseSavePipeline:

    @sync_to_async
    def process_item(self, item, spider):
        try:
            jobid = item.get('jobid', '')
            date = item.get('datePosted', '')
            job_title = item.get('job_title', '')
            company_name = item.get('company_name', '')
            company_location = item.get('company_location', '')
            min_salary = item.get('min_salary', '')
            max_salary = item.get('max_salary', '')
            salary_unit = item.get('salary_unit', '')
            job_description = item.get('job_description', '')
            url = item.get('url', '')
            job_types = item.get('job_types', [])

            if not min_salary:
                min_salary = None
            if not max_salary:
                max_salary = None


            existing_job = ScrapedData.objects.filter(jobid=jobid).first()
            if existing_job:
                raise DropItem(f"Duplicate jobid found: {jobid}")

            data = ScrapedData(
                jobid=jobid,
                date_scraped=date,
                job_title=job_title,
                company_name=company_name,
                company_location=company_location,
                min_salary = min_salary,
                max_salary = max_salary,
                salary_unit = salary_unit,
                job_description=job_description,
                url=url,
                job_types = job_types,
            )
            data.save()
        except Exception as e:
            spider.logger.error(f"Error saving data to the database for item: {item}")
            for key, value in item.items():
                if isinstance(value, str):
                    spider.logger.info(f"Length of {key}: {len(value)}")
            spider.logger.error(f'Error details: {e}')


        return item
