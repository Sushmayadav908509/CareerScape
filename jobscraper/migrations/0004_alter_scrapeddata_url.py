# Generated by Django 5.0.1 on 2024-04-01 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobscraper', '0003_alter_scrapeddata_company_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapeddata',
            name='url',
            field=models.CharField(default='', max_length=500),
        ),
    ]
