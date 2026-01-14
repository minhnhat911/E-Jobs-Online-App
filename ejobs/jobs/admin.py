from django.contrib import admin
from django.db.models import Count, Sum
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path
from .models import User, JobCategory, JobPost, Tag, EmployerProfile, CandidateProfile, JobApplication, Payment, ApplicationReview


class JobPostForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorUploadingWidget)
    requirements = forms.CharField(widget=CKEditorUploadingWidget)
    benefits = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = JobPost
        fields = '__all__'


class JobPostAdmin(admin.ModelAdmin):
    form = JobPostForm
    list_display = ['id', 'title', 'employer', 'category', 'status', 'is_featured', 'created_date']
    search_fields = ['title', 'employer__company_name']
    list_filter = ['category', 'status', 'is_featured', 'location']
    filter_horizontal = ['tags']


class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'user', 'is_approved', 'created_date']
    list_editable = ['is_approved']
    readonly_fields = ['logo_view']

    def logo_view(self, obj):
        if obj.logo:
            return mark_safe(f"<img src='{obj.logo.url}' width='100' />")
        return "No Logo"


class MyJobAdminSite(admin.AdminSite):
    site_header = 'HỆ THỐNG QUẢN TRỊ E-JOBS'
    site_title = 'Admin E-Jobs'
    index_title = 'Trang quản trị hệ thống'

    def get_urls(self):
        return [
            path('ejobs-stats/', self.admin_view(self.stats_view), name='ejobs_stats'),
        ] + super().get_urls()

    def stats_view(self, request):
        job_stats = JobCategory.objects.annotate(job_count=Count('jobpost')).order_by('-job_count')[:10].values('name', 'job_count')

        revenue_stats = Payment.objects.filter(status='SUCCESS').values('payment_method').annotate(total=Sum('amount'))

        user_stats = User.objects.values('role').annotate(total=Count('id'))

        return TemplateResponse(request, 'admin/ejobs_stats.html', {
            'job_stats': job_stats,
            'revenue_stats': revenue_stats,
            'user_stats': user_stats,
        })

# jobs/admin.py

class ApplicationReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'application', 'employer', 'score', 'created_date']
    list_filter = ['score', 'created_date']
    search_fields = ['application__candidate__full_name', 'employer__company_name']


admin_site = MyJobAdminSite(name='myadmin')

admin_site.register(User)
admin_site.register(JobCategory)
admin_site.register(Tag)
admin_site.register(CandidateProfile)
admin_site.register(JobApplication)
admin_site.register(Payment)
admin_site.register(EmployerProfile, EmployerProfileAdmin)
admin_site.register(JobPost, JobPostAdmin)
admin_site.register(ApplicationReview, ApplicationReviewAdmin)
