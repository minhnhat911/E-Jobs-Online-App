from rest_framework import viewsets, generics, status, parsers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JobCategory, JobPost, User, JobApplication, CandidateProfile
from . import serializers, paginators, perms


class CategoryViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = JobCategory.objects.all()
    serializer_class = serializers.CategorySerializer


class JobPostViewSet(viewsets.ViewSet, generics.ListAPIView, generics.RetrieveAPIView):
    queryset = JobPost.objects.filter(active=True, status='OPENING').order_by('-created_date')
    serializer_class = serializers.JobPostSerializer
    pagination_class = paginators.ItemPaginator

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return serializers.JobPostDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        query = self.queryset.select_related('category', 'employer')

        q = self.request.query_params.get('q')
        if q:
            query = query.filter(Q(title__icontains=q) | Q(employer__company_name__icontains=q))

        cate_id = self.request.query_params.get('category_id')
        if cate_id:
            query = query.filter(category_id=cate_id)

        loc = self.request.query_params.get('location')
        if loc:
            query = query.filter(location__icontains=loc)

        salary = self.request.query_params.get('salary')
        if salary:
            query = query.filter(salary_max__gte=salary)

        return query

    @action(methods=['post'], url_path='apply', detail=True,
            permission_classes=[perms.IsCandidate])  # Chỉ ứng viên mới được apply
    def apply_job(self, request, pk):
        job = self.get_object()

        # Kiểm tra xem ứng viên này đã nộp đơn cho công việc này chưa
        existing_app = JobApplication.objects.filter(job=job, candidate__user=request.user).exists()
        if existing_app:
            return Response({"detail": "Bạn đã nộp đơn cho công việc này rồi."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Lấy hồ sơ ứng viên của user hiện tại
            candidate = request.user.candidateprofile
        except CandidateProfile.DoesNotExist:
            return Response({"detail": "Bạn cần cập nhật hồ sơ ứng viên trước khi ứng tuyển."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Xử lý CV: Ưu tiên CV mới upload, nếu không thì dùng CV mặc định trong Profile
        cv_file = request.FILES.get('cv_file') or candidate.cv_file
        if not cv_file:
            return Response({"detail": "Vui lòng đính kèm file CV."},
                            status=status.HTTP_400_BAD_REQUEST)

        app = JobApplication.objects.create(
            job=job,
            candidate=candidate,
            cv_file=cv_file
        )

        return Response(serializers.JobApplicationSerializer(app).data,
                        status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = serializers.UserSerializer
    parser_classes = [parsers.MultiPartParser]

    def get_permissions(self):
        if self.action in ['get_current_user']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(methods=['get', 'patch'], url_path='current-user', detail=False)
    def get_current_user(self, request):
        user = request.user
        if request.method.__eq__('PATCH'):
            s = serializers.UserSerializer(user, data=request.data, partial=True)
            s.is_valid(raise_exception=True)
            s.save()

        return Response(serializers.UserSerializer(user).data, status=status.HTTP_200_OK)

