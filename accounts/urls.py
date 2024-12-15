# JobHub\accounts\urls.py
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from accounts.views import *

urlpatterns = [
    path('register/', views.register, name='register'),
    path('set_profile/', views.set_profile, name='set_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recruiter_dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('delete_user_job/', views.delete_user_job, name='delete_user_job'),
    path('update_user_job/', views.update_user_job, name='update_user_job'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('password_reset/', CustomPasswordResetView.as_view(template_name = 'registration/password_reset_custom.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name = 'registration/password_reset_done_custom.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = 'registration/password_reset_confirm_custom.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name = 'registration/password_reset_complete_custom.html'), name='password_reset_complete'),


    path('delete_account/', views.delete_account, name='delete_account'),
    path('verify_password/', views.verify_password, name='verify_password'),
    path('user_profile_edit/', views.user_profile_edit, name='user_profile_edit'),
    path('verify_phone/', views.verify_phone, name='verify_phone'),
    path('verify_phone_otp/', views.verify_phone_otp, name='verify_phone_otp'),


    path('get_countries_data/', views.get_countries_data, name='get_countries_data'),
    path('jobs/', views.jobs, name='jobs'),
    path('bookmark/', views.bookmark, name='bookmark'),
    path('remove_bookmark/', views.remove_bookmark, name='remove_bookmark'),

    path('', views.home, name='home'),
    path('gateway/', views.gateway, name='gateway'),
    path('generate_resume/', views.generate_resume,name="generate_resume"),
]

