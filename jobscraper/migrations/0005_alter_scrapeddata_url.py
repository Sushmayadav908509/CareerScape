# Generated by Django 5.0.1 on 2024-05-04 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobscraper', '0004_alter_scrapeddata_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapeddata',
            name='url',
            field=models.CharField(blank=True, default='', max_length=500, null=True),
        ),
    ]
