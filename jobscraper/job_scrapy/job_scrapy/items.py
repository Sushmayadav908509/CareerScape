import scrapy

class JobScrapyItem(scrapy.Item):
    jobid = scrapy.Field()
    datePosted = scrapy.Field()
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    company_location = scrapy.Field()
    min_salary = scrapy.Field()
    max_salary = scrapy.Field()
    salary_unit = scrapy.Field()
    job_description = scrapy.Field()
    url = scrapy.Field()
    job_types = scrapy.Field()