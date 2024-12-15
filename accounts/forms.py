from typing import Any
from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation
from ckeditor.widgets import CKEditorWidget
from django.core.exceptions import ValidationError
from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'}))

    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'}))

    username = forms.CharField(required=True, max_length=100, label='Username', widget=forms.TextInput(attrs={'placeholder': 'Enter username'}))

    email = forms.EmailField(required=True, label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'}))

    company_name = forms.CharField(required=False, label='Company Name', widget=forms.TextInput(attrs={'class': 'company_name', 'placeholder': 'Enter Company Name'}))

    profile_type = forms.ChoiceField(choices=CustomUser.PROFILE_CHOICES, required=True, label='Profile Type')

    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
        help_text=password_validation.password_validators_help_text_html(),
        required=True,
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password again'}),
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'profile_type', 'company_name']





class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'E-mail'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'profile_picture', 'resume', 'company_name', 'company_website', 'linkedin_profile', 'skills', 'education', 'experience', 'location']
        

class PasswordVerificationForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'passwordInput'}))


class AccountDeletionForm(forms.Form):
    confirmation = forms.BooleanField(
        required=True,
        label='I understand that this action cannot be undone'
    )
    password = forms.CharField(
        required=True,
        label='confirm your password',
        widget=forms.PasswordInput
    )

class CreateJobForm(forms.Form):
    JOB_TYPES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('intern', 'Intern'),
        ('temporary', 'Temporary'),
        ('contract', 'Contract'),
    ]
    SALARY_CHOICES = [
        ('range', 'Range'),
        ('starting_at', 'Starting At'),
        ('upto', 'Up To'),
        ('exact_rate', 'Exact Rate'),
    ]
    SALARY_UNITS = [
        ('month', 'Month'),
        ('year', 'Year'),
    ]

    job_title = forms.CharField(label='Job Title', widget=forms.TextInput(attrs={'class': 'form-control'}),)
    location = forms.CharField(label='Location', widget=forms.TextInput(attrs={'class': 'form-control'}),)
    job_type = forms.ChoiceField(label='Job Type', choices=JOB_TYPES, widget=forms.Select(attrs={'class': 'form-control'}),)
    salary_type = forms.ChoiceField(label='Salary Type', choices=SALARY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}),)
    min_salary = forms.DecimalField(label='Min Salary', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}),)
    max_salary = forms.DecimalField(label='Max Salary', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}),)
    salary_unit = forms.ChoiceField(label='Salary Unit', choices=SALARY_UNITS, widget=forms.Select(attrs={'class': 'form-control'}),)
    job_description = forms.CharField(widget=CKEditorWidget(attrs={'id':'ckeditorwidgetid'}), label='Job Description')

class ResumeForm(forms.Form):
    # Personal Information
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'id':'resume_name'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'id':'resume_email'}))
    phone_number = forms.CharField(label='Phone Number', widget=forms.TextInput(attrs={'id':'resume_number'}))
    linkedin_link = forms.URLField(label='LinkedIn Link', widget=forms.URLInput(attrs={'id':'resume_linkedin'}))

    # Education
    education_title = forms.CharField(label='Education Title', widget=forms.TextInput(attrs={'id':'resume_education_title'}))
    college = forms.CharField(label='College', widget=forms.TextInput(attrs={'id':'resume_college'}))
    coursework = forms.CharField(label='Coursework', widget=forms.Textarea(attrs={'id':'resume_coursework'}))
    cgpa = forms.FloatField(label='CGPA (Pointer)', widget=forms.TextInput(attrs={'id':'resume_cgpa'}))
    year_of_graduation = forms.IntegerField(label='Year of Graduation', widget=forms.DateTimeInput(attrs={'id':'resume_graduation_year'}))

    # Work Experience
    company = forms.CharField(label='Company', widget=forms.TextInput(attrs={'id':'resume_company'}))
    role = forms.CharField(label='Role', widget=forms.TextInput(attrs={'id':'resume_role'}))
    description = forms.CharField(label='Description', widget=forms.Textarea(attrs={'id':'resume_wb_description'}))
    start_date = forms.DateField(label='Start Date', widget=forms.TextInput(attrs={'type': 'date', 'id':'resume_start_date'}))
    end_date = forms.DateField(label='End Date', widget=forms.TextInput(attrs={'type': 'date', 'id':'resume_end_date'}))

    # Projects
    project_title = forms.CharField(label='Project Title', widget=forms.TextInput(attrs={'id':'resume_project_title'}))
    tools_used = forms.CharField(label='Tools Used for Project', widget=forms.Textarea(attrs={'id':'resume_project_tools'}))
    project_description = forms.CharField(label='Project Description', widget=forms.Textarea(attrs={'id':'resume_project_description'}))

    # Skills
    skills = forms.CharField(label='Skills', widget=forms.Textarea(attrs={'id':'resume_skills'}))

    # Certifications
    certification_title = forms.CharField(label='Certification Title', widget=forms.TextInput(attrs={'id':'resume_cert_title'}))
    certification_link = forms.URLField(label='Certification Link', widget=forms.URLInput(attrs={'id':'resume_cert_link'}))