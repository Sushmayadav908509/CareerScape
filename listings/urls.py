# JobHub\listings\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('scraped_data/all', views.ScrapedDataList.as_view(), name='scraped-data-list'),
    path('scraped_data/sort/', views.ScrapedDataSortByDate.as_view(), name='scraped-data-sort-by-date'),
    path('scraped_data/search/', views.SearchScrapedData.as_view(), name='search-scraped-data'),
    path('scraped_data/date_scraped/<str:date>/', views.ScrapedDataByDate.as_view(), name='scraped-data-by-date'),
    path('scraped_data/user_job/', views.UserScrapedData.as_view(), name='user-scraped-data'),
    path('scraped_data/user_job_save/', views.UserSaveData.as_view(), name='user-job-save'),
    path('scraped_data/delete_user_job/', views.UserDeleteJob.as_view(), name='delete-user-job'),
    path('scraped_data/update_user_job/<str:jobid>', views.UserUpdateJob.as_view(), name='update-user-job'),
    path('scraped_data/user_bookmark_data/', views.UserBookmarkData.as_view(), name='user-bookmark-data'),

    path('scraped_data/keyword/', views.SearchByKeyWord.as_view(), name='search-by-keyword'),

]

