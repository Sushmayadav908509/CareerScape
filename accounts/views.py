# JobHub\accounts\views.py
from django.views.decorators.csrf import csrf_exempt
from typing import Any 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, UserProfileEditForm, UserLoginForm, CreateJobForm, ResumeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.views import PasswordResetConfirmView
from django.core.cache import cache
from django.contrib.auth.views import PasswordResetView
from jobscraper.models import ScrapedData
from .models import LookUpJob, CustomUser, PaymentGateway
from accounts.utils import send_otp, generate_jobid, extract_form_data,generate_receipt, extract_resume_data, replace_placeholders
import phonenumbers
from .forms import PasswordVerificationForm
from phonenumbers.phonenumberutil import NumberParseException
from datetime import date
from CareerScape.settings import razr_key, razr_secret
from io import BytesIO
from docx import Document
from docx.shared import Pt
import pyotp
import uuid
import base64
import json
import requests
import razorpay


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])

            user = form.save()
            login(request, user)

            if request.user.profile_type == 'recruiter':
                return redirect('recruiter_dashboard')
            else:
                return redirect('dashboard')
        else:
            print('Form is invalid. Errors:')
            for field, errors in form.errors.items():
                print(f"Field: {field}, Errors: {', '.join(errors)}")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def set_profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = UserProfileEditForm(instance=request.user)

    return render(request, 'set_profile.html', {'form': form})

# -------------------------------------------------------------------------------------------------------------------

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                print("User successfully authenticated")
                if user.profile_type == 'job_seeker':
                    return redirect('dashboard')
                else:
                    return redirect('recruiter_dashboard')
            else:
                print("authentication failed")
                form.add_error('email', 'Invalid email or password. Please try again')
        else:
            print("form is invalid")
            messages.error(request, 'Incorrect credentials')

    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

# -------------------------------------------------------------------------------------------------------------------

@login_required
def verify_password(request):
    if request.method == 'POST':
        form = PasswordVerificationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']

            user = authenticate(request, email = request.user.email, password=password)
            
            if user is not None:
                request.session['password_verified'] = True
                return JsonResponse({'success': True, 'message': 'Password is Verified'})
            else:
                return JsonResponse({'success': False, 'message': 'Password Verification Failed'})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def delete_account(request):
    if request.session.get('password_verified', False):
        user = request.user
        user.delete()
        return JsonResponse({'success': True, 'message': 'Your Account is deleted'})
    return JsonResponse({'success': False, 'message': 'Password verificaion required'})

# -------------------------------------------------------------------------------------------------------------------

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        email = form.cleaned_data['email']
        user = CustomUser.objects.filter(email=email)

        if user.exists():
            return super().form_valid(form)
        else:
            form.add_error('email', 'No user with this email address exists')
            return self.form_invalid(form)


# -------------------------------------------------------------------------------------------------------------------


def home(request):
    return render(request, 'home.html')

# -------------------------------------------------------------------------------------------------------------------

@login_required
def dashboard(request):
    password_form = PasswordVerificationForm()
    profile_type = request.user.profile_type
    bookmarks = request.user.bookmarks
    data = json.dumps(bookmarks)
    resume_form = ResumeForm()
    premium = request.user.is_paid_premium
    print(premium)

    response = requests.post('http://127.0.0.1:8000/scraped_data/user_bookmark_data/', data=data)

    if response.status_code == 200:
        bookmark_data = response.json()
        user_bookmark_data = json.dumps(bookmark_data)


    with open('static/accounts/countries.json', 'r') as json_file:
        countries_data = json.load(json_file)
        countries_data = json.dumps(countries_data)
    
    return render(request, 'dashboard.html', {'profile_type': profile_type, 'password_form': password_form, 'countries_data': countries_data, 'bookmark_data': user_bookmark_data, 'resume_form':resume_form, 'premium': premium})


# -------------------------------------------------------------------------------------------------------------------

@login_required
def recruiter_dashboard(request):

    password_form = PasswordVerificationForm()

    with open('static/accounts/countries.json', 'r') as json_file:
        countries_data = json.load(json_file)
        countries_data = json.dumps(countries_data)

    user_unique_key = request.user.unique_key

    url = f'http://127.0.0.1:8000/scraped_data/user_job?user_unique_key={user_unique_key}'
    response = requests.get(url)

    if response.status_code == 200:
        user_job_data = response.json()
        user_job_data = json.dumps(user_job_data)

    if request.method == 'POST':
        form = CreateJobForm(request.POST)
        user_unique_key = request.user.unique_key
        company_name = request.user.company_name

        if form.is_valid():
            jobid = generate_jobid()
            date_created = date.today()
            job_title, location, job_types, min_salary, max_salary, salary_unit, job_description = extract_form_data(form)

            data = {
                "jobid": jobid,
                "date_scraped": date_created,
                "job_title": job_title,
                "company_name": company_name,
                "company_location": location,
                "job_description": job_description,
                "url": "",
                "job_types": job_types,
                "max_salary": max_salary,
                "min_salary": min_salary,
                "salary_unit": salary_unit
            }
            
            try:
                response = requests.post('http://127.0.0.1:8000/scraped_data/user_job_save/', data=data)
                response.raise_for_status()

                if response.status_code == 201:
                    lookup_job, created = LookUpJob.objects.get_or_create(
                    user_unique_key=user_unique_key,
                    defaults={'jobid': [jobid]}
                    )

                    if not created:
                        lookup_job.jobid.append(jobid)
                        lookup_job.save()
                    print("Job Created")
                    return redirect('recruiter_dashboard')
                else:
                    return HttpResponse('Error creating job', status=500)
            except requests.exceptions.RequestException as e:
                return HttpResponse(f'Error: {str(e)}', status=500)
        return HttpResponse('Form is invalid', status=400)
        
    else:
        initial_data = {'salary_type': 'range'}
        form = CreateJobForm(initial=initial_data)

    return render(request, 'recruiter_dashboard.html', {'form': form, 'password_form': password_form, 'countries_data': countries_data, "user_job_data": user_job_data})


# -------------------------------------------------------------------------------------------------------------------

@login_required
def delete_user_job(request):
    user_unique_key = request.user.unique_key
    jobid = request.GET.get('dataJobId')
    print(jobid)
    data = {'jobid': jobid}
    response = requests.delete(f'http://127.0.0.1:8000/scraped_data/delete_user_job/', data=data)

    if response.status_code == 204:
        try:
            lookup_job = LookUpJob.objects.get(user_unique_key=user_unique_key)
            job_ids = lookup_job.jobid
            if jobid in job_ids:
                job_ids.remove(jobid)
                lookup_job.jobid = job_ids
                lookup_job.save()
            return JsonResponse({"success": True, "message": "Job Posting deleted successfully"})
        except LookUpJob.DoesNotExist:
            return JsonResponse({"success": False, "message": "Error while deleting Job Posting"})
    else:
        return JsonResponse({"success": False, "Message": "Error while deleting Job Posting"})

# -------------------------------------------------------------------------------------------------------------------

login_required
def update_user_job(request):
    if request.method == "POST":

        jobid = request.POST.get('jobid')
        job_title = request.POST.get('job_title')
        location = request.POST.get('location')
        job_type = request.POST.get('job_type')
        min_salary = request.POST.get('min_salary')
        max_salary = request.POST.get('max_salary')
        salary_unit = request.POST.get('salary_unit')
        job_description = request.POST.get('job_description')

        data = {
            'jobid': jobid,
            'job_title': job_title,
            'company_location': location,
            'job_type': job_type,
            'min_salary': min_salary,
            'max_salary': max_salary,
            'salary_unit': salary_unit,
            'job_description': job_description,
            'url': "",
        }

        url = f'http://127.0.0.1:8000/scraped_data/update_user_job/{jobid}'
        response = requests.patch(url, data=data)

        if response.status_code == 200:
            return JsonResponse({"success": True, "message": "Job updated successfully"})
        else:
            return JsonResponse({"success": False, "message": "Error while updating Job"})
    else:
        return HttpResponse(status=405)



# -------------------------------------------------------------------------------------------------------------------

@login_required
def user_profile_edit(request):
    user = request.user

    if request.method == 'POST':
        data = request.POST.copy()
        print(data)
        user_profile_form_data = {key: value for key, value in data.items() if value not in ('null', 'undefined')}
        form = UserProfileEditForm(user_profile_form_data, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            print(form.errors)
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = UserProfileEditForm(instance=request.user)

    return JsonResponse({'success': False})

# -------------------------------------------------------------------------------------------------------------------

def get_countries_data(request):
    with open('static/accounts/countries.json', 'r') as json_file:
        countries_data = json.load(json_file)
    return JsonResponse(countries_data, safe=False)

# -------------------------------------------------------------------------------------------------------------------

@login_required
def verify_phone(request):
    if request.method == 'POST':
        new_phone = request.POST.get('new_phone')
        dial_code = request.POST.get('dial_code')
        new_phone_number = dial_code + new_phone
        region_code = request.POST.get('region_code')
        request.session['new_phone'] = new_phone

        user = request.user
        unique_key = user.unique_key
        email = user.email

        secret_key = base64.b32encode(uuid.UUID(str(unique_key)).bytes).decode()

        interval = 60
        totp = pyotp.TOTP(secret_key, interval=interval, digits=6)
        otp = totp.now()

        try:
            parse_number = phonenumbers.parse(new_phone, region_code)
            if phonenumbers.is_valid_number(parse_number):
                print("Valid Phone Number")
                print(new_phone_number)
                if send_otp(email, otp):
                    print("OTP sent successfully")
                    return JsonResponse({'success': True, 'message': 'OTP sent successfully to your Email Id'})
                else:
                    print("Failed to send OTP")
                    return JsonResponse({'success': False, 'message': 'Failed to send OTP'})
        except NumberParseException as e:
            print(f"Invalid phone number: {e}") 
            return JsonResponse({'success': False, 'message': 'Invalid phone number'})
    
    return JsonResponse({'success': False, 'message': 'Invalid phone number'})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def verify_phone_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        user = request.user
        unique_key = user.unique_key
        secret_key = base64.b32encode(uuid.UUID(str(unique_key)).bytes).decode()
        interval = 60
        totp = pyotp.TOTP(secret_key, interval=interval, digits=6)
        try:
            validate_otp = totp.verify(user_otp, valid_window=1)
            new_phone = request.session.get('new_phone')
            if validate_otp:
                user.phone_number = new_phone
                user.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid OTP'})
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': f"OTP validation error: {str(e)}"})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def verify_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('new_email')
        request.session['new_email'] = new_email

        user = request.user
        unique_key = user.unique_key
    

        secret_key = base64.b32encode(uuid.UUID(str(unique_key)).bytes).decode()

        interval = 60
        totp = pyotp.TOTP(secret_key, interval=interval, digits=6)
        otp = totp.now()
        email_validator = EmailValidator()
        try:
            email_validator(new_email)
            print(True)
            send_otp(new_email, otp)
            return JsonResponse({'success': True, 'message': "OTP sent Successfully"})

        except ValidationError as e:
            print(False)
            return JsonResponse({'success': False, 'message': "Email not valid"})

# -------------------------------------------------------------------------------------------------------------------

@login_required
def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        user = request.user
        unique_key = user.unique_key

        secret_key = base64.b32encode(uuid.UUID(str(unique_key)).bytes).decode()
        
        interval = 60
        totp = pyotp.TOTP(secret_key, interval=interval, digits=6)

        try:
            validate_otp = totp.verify(user_otp, valid_window=1)
            new_email = request.session.get('new_email')

            if validate_otp:
                user.email = new_email
                user.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid OTP'})
            
        except ValidationError as e:
            return JsonResponse({'success': False, 'message': f"OTP validation error: {str(e)}"})

# -------------------------------------------------------------------------------------------------------------------

def jobs(request):
    sort_param = request.GET.get('sort')
    search_param = request.GET.get('search')
    offset_param = request.GET.get('offset')

    default_drf_url = f'http://127.0.0.1:8000/scraped_data/all?offset={offset_param}'

    drf_url = default_drf_url
    base_url = 'http://127.0.0.1:8000/scraped_data/'

    sort_url = f'sort/?offset={offset_param}&sort={sort_param}'
    search_url = f'search/?offset={offset_param}&search={search_param}'

    if sort_param:
        drf_url = base_url + sort_url

    if search_param:
        drf_url = base_url + search_url
        
        if sort_param:
            drf_url += f'&sort={sort_param}'

    response = requests.get(drf_url)

    if response.status_code == 200:
        data = response.json()
        data = json.dumps(data)  

        bookmarked_jobs_json = []

        if request.user.is_authenticated:
            user = request.user
            bookmarked_jobs = user.bookmarks
            bookmarked_jobs_json = json.dumps(bookmarked_jobs)

        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            data_dict = json.loads(data)
            return JsonResponse(data_dict)
        else:
            return render(request, 'jobs.html', {'data': data, 'bookmarked_jobs': bookmarked_jobs_json})
        
# -------------------------------------------------------------------------------------------------------------------

@require_POST
def bookmark(request):
    if request.method == 'POST':
        bookmark_jobid = request.POST.get('job_id')

        if request.user.profile_type == 'recruiter':
            return JsonResponse({"Message": "Bookmark Feature is exclusively available for job seekers"})

        if request.user.is_authenticated:
            user = request.user
            bookmarks = user.bookmarks

            if bookmark_jobid not in bookmarks:
                bookmarks.append(bookmark_jobid)
                user.save()
                return JsonResponse({"Message": "Bookmark added successfully"})
            else:
                return JsonResponse({"Message": "Bookmark already exists"})
        else:
            return JsonResponse({"Message": "Please Sign-in to bookmark"})
    else:
        return JsonResponse({"Message": "Error while bookmarking"})
    
# -------------------------------------------------------------------------------------------------------------------

@require_POST
def remove_bookmark(request):
    if request.method == 'POST':
        bookmark_jobid = request.POST.get('job_id')

        if request.user.is_authenticated:
            user = request.user
            bookmarks = user.bookmarks

            if bookmark_jobid in bookmarks:
                bookmarks.remove(bookmark_jobid)
                user.save()
                return JsonResponse({"Message": "Bookmark removed successfully"})
            else:
                return JsonResponse({"Message": "Bookmark not found"})
        else:
            return JsonResponse({"Message": "Please Sign-in to remove bookmark"})
    else:
        return JsonResponse({"Message": "Error while removing bookmark"})


def custom_error(request, exception=None):
    status_code = 404

    if exception is not None:
        status_code = getattr(exception, 'status_code', status_code)
        
    error_message = {
        404: "Page not found. Please check the URL and try again.",
        500: "Internal Server Error. Something went wrong.",
    }.get(status_code, "Oops! An error occurred.")

    return render(request, 'custom_error.html', { 'status_code': status_code, 'error_message': error_message})


def gateway(request):
    if request.method == 'GET':
        receipt = generate_receipt()
        amount = 10000
        client = razorpay.Client(auth=(razr_key, razr_secret))
        data = {"amount":amount, "currency":"INR", "receipt":receipt}
        pay = client.order.create(data=data)
        print(pay)
        order_id = pay['id']
        order_status = pay['status']
        order_amount = pay['amount']
        order_currency = pay['currency']
        if order_status == 'created':
            payment_gateway = PaymentGateway.objects.create(
                user_id = request.user.id,
                order_id = order_id,
                status = order_status,
                amount = order_amount,
                currency = order_currency,
                receipt = receipt
            )
        return render(request, 'gateway.html', {"data":pay})
    
    elif request.method == 'POST':
        payment_response = json.loads(request.POST.get('payment_response'))
        user_id = request.user.id
        # print(payment_response)
        if 'razorpay_payment_id' in payment_response:
            razorpay_payment_id = payment_response['razorpay_payment_id']
            razorpay_order_id = payment_response['razorpay_order_id']

            payment_instance = get_object_or_404(PaymentGateway, user_id=user_id, order_id=razorpay_order_id)
            if payment_instance:
                payment_instance.payment_id = razorpay_payment_id
                payment_instance.status = 'payment_received'
                payment_instance.save()
                user_instance = get_object_or_404(CustomUser, pk=user_id)
                user_instance.is_paid_premium = True
                user_instance.save()

            return render(request, 'success.html', {'message':'Your payment was successful \n You are now a premium Jobhub member!'})
        
        elif 'error' in payment_response:
            error_data = payment_response['error']
            payment_id = error_data['metadata']['payment_id']
            order_id = error_data['metadata']['order_id']
        
            payment_instance = get_object_or_404(PaymentGateway, user_id=user_id, order_id=order_id)
            if payment_instance:
                payment_instance.payment_id = payment_id
                payment_instance.status = 'payment_failed'
                payment_instance.save()
            
            return render(request, 'failure.html', {'message':'Your payment request failed, please try again'})

        else:
            return JsonResponse({'There was an error in handling the payment request'})
    
    return render(request, 'gateway.html')


# -------------------------------------------------------------------------------------------------------------------

def generate_resume(request):
    template_path = r'C:\Users\Sushma Yadav\OneDrive\Desktop\CareerScape\CareerScape\accounts\resume_template3.docx'
    if request.method == 'POST':
        username = request.user.username
        form = ResumeForm(request.POST)
        if form.is_valid():
            cleaned_form = form.cleaned_data
            print('form',form.cleaned_data)
            data = extract_resume_data(cleaned_form)
            doc = replace_placeholders(template_path, data)
            
            doc_bytes = BytesIO()
            doc.save(doc_bytes)
            doc_bytes.seek(0)

            response = FileResponse(doc_bytes, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename={username}_resume.docx'
            # print(response)
            return response
        else:
            errors = dict(form.errors.items())
            print('errors', errors)
            return JsonResponse({'success': False})

    return JsonResponse({})
@csrf_exempt
def success(request):
    return render(request, 'success.html')