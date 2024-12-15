# JobHub\listings\serializers.py
from rest_framework import serializers
from jobscraper.models import ScrapedData

class CustomURLField(serializers.URLField):
    def to_internal_value(self, data):
        if data == "":
            return None
        return super().to_internal_value(data)

class ScrapedDataSerializer(serializers.ModelSerializer):
    date_scraped = serializers.DateField(format='%Y-%m-%d')
    url = CustomURLField(allow_null=True)

    class Meta:
        model = ScrapedData
        fields = '__all__'
