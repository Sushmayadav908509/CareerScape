# JobHub\listings\views.py
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from jobscraper.models import ScrapedData
from accounts.models import LookUpJob
from .serializers import ScrapedDataSerializer
from .data_processing import format_salary, format_job_type, format_salary_unit
from django.http import Http404
from itertools import chain
from django.db.models import Q
from datetime import date
import json




class FormatDataMixin:
    def format_job_data(self, data):
        results = data.get('results', [])

        for item in results:
            min_salary = format_salary(item['min_salary'])
            max_salary = format_salary(item['max_salary'])
            item['salary_range'] = f"{min_salary} - {max_salary}"

            item['salary_unit'] = format_salary_unit(item['salary_unit'])
            item['job_types'] = format_job_type(item['job_types'])  

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = response.data
        self.format_job_data(data)
        return response


class CustomLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 12
    max_limit = 100



class ScrapedDataList(FormatDataMixin, generics.ListAPIView):
    serializer_class = ScrapedDataSerializer
    pagination_class = CustomLimitOffsetPagination
    queryset = ScrapedData.objects.all()



class ScrapedDataByDate(FormatDataMixin, generics.ListAPIView):
    serializer_class = ScrapedDataSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        date = self.kwargs['date']
        queryset = ScrapedData.objects.all().filter(date_scraped=date)
    
        # if not queryset.exists():
        #         raise Http404("No data found")
        return queryset
    

class ScrapedDataSortByDate(FormatDataMixin, generics.ListAPIView):
    serializer_class = ScrapedDataSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        queryset = ScrapedData.objects.all()
        sort_option = self.request.query_params.get('sort')
        if sort_option == 'newest':
            queryset = queryset.order_by('-date_scraped')
        elif sort_option == 'oldest':
            queryset = queryset.order_by('date_scraped')
        elif sort_option == 'today':
            today = date.today()
            queryset = queryset.filter(date_scraped=today)
            
        print(sort_option) 
        return queryset
    
    

class SearchScrapedData(FormatDataMixin, generics.ListAPIView):
    serializer_class = ScrapedDataSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '')
        sort_option = self.request.query_params.get('sort')

        search_vector = SearchVector('job_title', 'company_name', 'company_location', 'job_types')
        search_term = SearchQuery(search_query)
        rank = SearchRank(search_vector, search_term)
        queryset = ScrapedData.objects.annotate(search = search_vector, rank=rank).filter(search=search_term).order_by('-rank')


        if sort_option == 'newest':
            queryset = queryset.order_by('-date_scraped')
        elif sort_option == 'oldest':
            queryset = queryset.order_by('date_scraped')
        elif sort_option == 'today':
            today = date.today()
            queryset = queryset.filter(date_scraped=today)
        else:
            queryset=queryset

        return queryset
    

class SearchByKeyWord(generics.ListAPIView):
    serializer_class = ScrapedDataSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '')

        keywords = search_query.split()
        queryset = ScrapedData.objects.all()

        if len(keywords) == 1:
            conditions = Q()
            conditions &= Q(job_title__iregex=r'\y{}\y'.format(search_query))
            queryset = queryset.filter(conditions)
        else:
            for keyword in keywords:
                queryset = queryset.filter(job_title__icontains=keyword)

        # for keyword in keywords:
        #     queryset = queryset.filter(job_title__icontains=keyword)

        queryset = queryset.distinct()
        print(queryset)
        return queryset




class UserScrapedData(generics.ListAPIView):
    serializer_class = ScrapedDataSerializer

    def get_queryset(self):
        user_unique_key = self.request.query_params.get('user_unique_key')

        try:
            lookup_job = LookUpJob.objects.get(user_unique_key=user_unique_key)
            jobids = lookup_job.jobid
            queryset = ScrapedData.objects.filter(jobid__in=jobids)
        except LookUpJob.DoesNotExist:
            queryset = ScrapedData.objects.none()

        return queryset


class UserSaveData(generics.CreateAPIView):
    queryset = ScrapedData.objects.all()
    serializer_class = ScrapedDataSerializer

    def create(self, request, *args, **kwargs):
        jobid = request.data.get('jobid')

        if jobid:
            try:
                print(request.data)
                if ScrapedData.objects.filter(jobid=jobid).exists():
                    return Response("jobid already present", status=400)
                else:
                    serializer = self.get_serializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        print('job created')
                        return Response(serializer.data, status=201)
                    else:
                        print('invalid serializer', serializer.errors)
                        return Response(serializer.errors, status=400)
            except ScrapedData.DoesNotExist():
                pass


class UserDeleteJob(generics.DestroyAPIView):
    queryset = ScrapedData.objects.all()

    def destroy(self, request, *args, **kwargs):
        jobid = request.data.get('jobid')
        if jobid:
            try:
                print(request.data)
                scraped_data = ScrapedData.objects.get(jobid=jobid)
                scraped_data.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ScrapedData.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            

class UserUpdateJob(generics.UpdateAPIView):
    queryset = ScrapedData.objects.all()
    serializer_class = ScrapedDataSerializer
    lookup_field = 'jobid'

    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return super().update(request, *args, **kwargs)
        else:
            print("Invalid Serializer", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


class UserBookmarkData(FormatDataMixin, APIView):
    def post(self, request, format=None):

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"message": "Invalid JSON data in body"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = ScrapedData.objects.filter(jobid__in = data)
        serializer = ScrapedDataSerializer(queryset, many=True)
        
        response_data = serializer.data
        self.format_job_data({'results': response_data})

        return Response(response_data, status=status.HTTP_200_OK)
