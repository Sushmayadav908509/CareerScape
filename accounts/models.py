# JobHub\accounts\models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
import uuid
from django.contrib.postgres.fields import ArrayField

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, profile_type='job_seeker', **extra_fields):
        email = self.normalize_email(email)
        unique_key = str(uuid.uuid4())
        user = self.model(username=username, email=email, profile_type=profile_type, unique_key=unique_key, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)
    
class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    unique_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    
    company_name = models.CharField(max_length=100, null=True, blank=True)
    company_website = models.URLField(max_length=200, null=True, blank=True)
    linkedin_profile = models.URLField(max_length=200, null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    education = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    bookmarks = ArrayField(models.CharField(max_length=16), default=list, blank=True)
    is_paid_premium = models.BooleanField(default=False)
    
    PROFILE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('recruiter', 'Recruiter'),
    ]

    profile_type = models.CharField(max_length=20, choices=PROFILE_CHOICES, default='job_seeker')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    groups = models.ManyToManyField(Group, verbose_name=('groups'), blank=True, related_name='custom_user_groups')
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='custom_user_permissions'
    )

    def delete_user_data(self):
        LookUpJob.objects.filter(user_unique_key = self.unique_key).delete()
    
    def delete(self, using=None, keep_parents=False):
        self.delete_user_data()
        super().delete(using=using, keep_parents=keep_parents)

    def __str__(self):
        return self.email
    

class PaymentGateway(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=10)
    order_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255,null=True, blank=True)
    status = models.CharField(max_length=20,default='created')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    receipt = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)



class LookUpJob(models.Model):
    user_unique_key = models.UUIDField(unique=True)
    jobid = ArrayField(models.CharField(max_length=16), default=list, blank=True)

    def __str__(self):
        return f"{self.user_unique_key} - {self.jobid}"



    
def user_directory_path(instance, filename):
    return f"user_{instance.unique_key}/{filename}"
