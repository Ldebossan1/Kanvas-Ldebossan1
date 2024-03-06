from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.permissions import IsAdminAndAuthenticated
from .models import Content
from .serializers import ContentSerializer
from django.shortcuts import get_object_or_404
from courses.models import Course
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrStudentIsOwner
from django.http import Http404, JsonResponse
from rest_framework.views import status
from rest_framework.exceptions import NotFound


class ContentView(CreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminAndAuthenticated]

    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    lookup_url_kwarg = "course_id"

    def perform_create(self, serializer):
        course_id = self.kwargs["course_id"]

        try:
            obj_course = get_object_or_404(Course, id=course_id)
        except Http404:
            error = {"detail": "course not found."}

            raise JsonResponse(
                error,
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer.save(course=obj_course)


class ContentDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [
        IsAuthenticated,
        IsAdminOrStudentIsOwner,
    ]

    serializer_class = ContentSerializer
    queryset = Content.objects.all()
    lookup_url_kwarg = "content_id"

    def get_object(self):
        course_id = self.kwargs["course_id"]
        content_id = self.kwargs["content_id"]

        try:
            Course.objects.get(id=course_id)
            obj_content = Content.objects.get(id=content_id)
        except Course.DoesNotExist:
            raise NotFound(
                {"detail": "course not found."},
            )
        except Content.DoesNotExist:
            raise NotFound(
                {"detail": "content not found."},
            )

        self.check_object_permissions(
            self.request,
            obj_content,
        )
        return obj_content
