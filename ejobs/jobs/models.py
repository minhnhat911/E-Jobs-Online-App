from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('EMPLOYER', 'Employer'),
        ('CANDIDATE', 'Candidate')
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    avatar = CloudinaryField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class BaseModel(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CandidateProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    experience_years = models.IntegerField(default=0)
    skills = models.TextField()
    cv_file = CloudinaryField(null=True, blank=True)

    def __str__(self):
        return self.full_name

class EmployerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255)
    company_description = models.TextField()
    company_address = models.TextField()
    website = models.CharField(max_length=255, null=True, blank=True)
    logo = CloudinaryField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class JobCategory(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class JobPost(BaseModel):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed')
    )

    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name='job_posts')

    title = models.CharField(max_length=255)
    description = RichTextField()
    requirements = RichTextField()
    salary_min = models.DecimalField(max_digits=12, decimal_places=2)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2)
    benefits = RichTextField()
    location = models.CharField(max_length=255)
    expired_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')

    def __str__(self):
        return self.title

class JobApplication(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    )

    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    cv_file = CloudinaryField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.candidate} - {self.job}"

class ApplicationReview(BaseModel):
    application = models.OneToOneField(JobApplication, on_delete=models.CASCADE, related_name='review')
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    comment = models.TextField()

    def __str__(self):
        return f"Review - {self.application}"

class Payment(BaseModel):
    SERVICE_CHOICES = (
        ('FEATURED_JOB', 'Featured Job'),
        ('PRIORITY_CV', 'Priority CV')
    )

    METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('PAYPAL', 'PayPal'),
        ('STRIPE', 'Stripe'),
        ('MOMO', 'MoMo'),
        ('ZALOPAY', 'ZaloPay')
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    transaction_code = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.transaction_code
