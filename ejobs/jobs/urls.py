from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register('categories', views.CategoryViewSet, basename='category')
router.register('jobposts', views.JobPostViewSet, basename='jobpost')
router.register('users', views.UserViewSet, basename='user')

# router.register('reviews', views.ApplicationReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]