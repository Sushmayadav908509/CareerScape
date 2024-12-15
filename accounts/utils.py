from django.core.mail import send_mail, BadHeaderError
from jobscraper.models import ScrapedData
from docx import Document
import uuid
from datetime import datetime
from typing import Dict

def send_otp(email, otp):
    subject = 'Your OTP for Verification'
    message = f"Your OTP is: {otp}"
    from_email = 'manishsalavkar78@gmail.com'
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        return True
    except BadHeaderError:
        print("Invalid header found")
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")


def generate_jobid():
    while True:
        jobid = str(uuid.uuid4()).replace("-", "")[:16]
        if jobid not in ScrapedData.objects.values_list('jobid', flat=True):
            return jobid

def generate_receipt():
    unique_id = str(uuid.uuid4()).replace('-','')[:16]
    return unique_id
        

def extract_form_data(form):
    job_title = form.cleaned_data['job_title']
    location = form.cleaned_data['location']
    job_types = form.cleaned_data['job_type']
    min_salary = form.cleaned_data['min_salary']
    max_salary = form.cleaned_data['max_salary']
    salary_unit = form.cleaned_data['salary_unit']
    job_description = form.cleaned_data['job_description']

    return job_title, location, job_types, min_salary, max_salary, salary_unit, job_description

def extract_resume_data(data: Dict) -> Dict:
    resume_data = {}
    resume_data['name'] = data.get('name')
    resume_data['email'] = data.get('email')
    resume_data['phone_number'] = data.get('phone_number')
    resume_data['linkedin_link'] = data.get('linkedin_link')
    resume_data['education_title'] = data.get('education_title')
    resume_data['college'] = data.get('college')
    resume_data['coursework'] = data.get('coursework')
    resume_data['cgpa'] = data.get('cgpa')
    resume_data['year_of_graduation'] = data.get('year_of_graduation')
    resume_data['company'] = data.get('company')
    resume_data['role'] = data.get('role')
    resume_data['description'] = data.get('description')
    resume_data['start_date'] = data.get('start_date')
    resume_data['end_date'] = data.get('end_date')
    resume_data['project_title'] = data.get('project_title')
    resume_data['tools_used'] = data.get('tools_used')
    resume_data['project_description'] = data.get('project_description')
    resume_data['skills'] = data.get('skills')
    resume_data['certification_title'] = data.get('certification_title')
    resume_data['cert_link'] = data.get('certification_link')

    # Convert date strings to datetime objects
    resume_data['start_date'] = resume_data['start_date'].strftime('%Y-%m-%d') if resume_data['start_date'] else None
    resume_data['end_date'] = resume_data['end_date'].strftime('%Y-%m-%d') if resume_data['end_date'] else None


    return resume_data

template_path = r'C:\Users\Tanmay\Documents\JobHub\JobHub\accounts\resume_template1.docx'

def replace_placeholders(template_path: str, data: Dict) -> Document:
    doc = Document(template_path)

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            for key, value in data.items():
                if f'<<{key}>>' in run.text:
                    run.text = run.text.replace(f'<<{key}>>', str(value))
    return doc