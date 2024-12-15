# JobHub\jobscraper\models.py
from django.db import models

class ScrapedData(models.Model):
    jobid = models.CharField(max_length=255, unique=True)
    date_scraped = models.DateField(blank=True, null=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=500, null=True, blank=True)
    company_location = models.CharField(max_length=255, null=True, blank=True)
    min_salary = models.FloatField(null=True, default=None, blank=True)
    max_salary = models.FloatField(null=True, default=None, blank=True)
    salary_unit = models.TextField(null=True, default=None, blank=True)
    job_types = models.TextField(null=True, default=None, blank=True)
    job_description = models.TextField()
    # url = models.URLField(null=True, blank=True)
    url = models.CharField(max_length=500, default='', null=True, blank=True)

    def __str__(self):
        return self.job_title