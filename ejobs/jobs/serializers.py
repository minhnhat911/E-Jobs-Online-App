from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import (
    User, JobCategory, JobPost, Tag,
    EmployerProfile, CandidateProfile, JobApplication, Payment, ApplicationReview
)

class ItemSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Tự động lấy URL tuyệt đối cho các trường đặc thù nếu có
        for field in ['avatar', 'logo', 'cv_file', 'image']:
            if field in data and getattr(instance, field, None):
                data[field] = getattr(instance, field).url
        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserSerializer(ItemSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'avatar', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password) # Băm mật khẩu
        user.save()
        return user

class EmployerSerializer(ItemSerializer):
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_description', 'website', 'logo', 'is_approved']

class CandidateSerializer(ItemSerializer):
    class Meta:
        model = CandidateProfile
        fields = ['full_name', 'phone', 'experience_years', 'skills', 'cv_file']

class JobPostSerializer(ItemSerializer):
    category = CategorySerializer()
    tags = TagSerializer(many=True)
    employer = EmployerSerializer()

    class Meta:
        model = JobPost
        fields = [
            'id', 'title', 'salary_min', 'salary_max',
            'location', 'created_date', 'expired_date',
            'is_featured', 'category', 'tags', 'employer'
        ]

class JobPostDetailSerializer(JobPostSerializer):
    class Meta:
        model = JobPost
        fields = JobPostSerializer.Meta.fields + ['description', 'requirements', 'benefits']

class JobApplicationSerializer(ItemSerializer):
    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'candidate', 'cv_file', 'status', 'created_date']
        extra_kwargs = {
            'job': {'write_only': True},
            'candidate': {'write_only': True}
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['job_title'] = instance.job.title
        data['candidate_name'] = instance.candidate.full_name
        return data

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'service_type', 'amount', 'payment_method', 'status', 'created_date']

class ApplicationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationReview
        fields = ['id', 'application', 'employer', 'score', 'comment', 'created_date']
        read_only_fields = ['employer'] # Employer sẽ được lấy từ request.user trong View

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Điểm đánh giá phải từ 1 đến 5.")
        return value