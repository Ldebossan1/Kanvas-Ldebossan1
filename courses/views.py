from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminOrGetMethodPermission, IsAdminAndAuthenticated
from .serializers import CourseSerializer, StudentSerializer
from .models import Course
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from rest_framework.views import status
from accounts.models import Account
from students_courses.models import StudentCourse
from rest_framework.exceptions import ValidationError


class CourseView(ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrGetMethodPermission]

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_queryset(self) -> Course:
        user_admin = self.request.user.is_superuser
        course_id = self.request.user.id

        if not user_admin:
            return Course.objects.filter(students=course_id)

        return Course.objects.all()

    def perform_create(self, serializer):
        founded_instructor = "instructor"

        if not founded_instructor in serializer.validated_data:
            serializer.save()
        else:
            serializer.save(instructor=serializer.validated_data[founded_instructor])


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsAdminOrGetMethodPermission]

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_url_kwarg = "course_id"

    def get_queryset(self) -> Course:
        user_admin = self.request.user.is_superuser
        course_id = self.request.user.id

        if not user_admin:
            return Course.objects.filter(students=course_id)

        return Course.objects.all()


class StudentView(RetrieveUpdateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminAndAuthenticated]
    queryset = Course.objects.all()
    serializer_class = StudentSerializer
    lookup_url_kwarg = "course_id"

    def perform_update(self, serializer):
        students_courses = serializer.validated_data.get(
            "students_courses",
            [],
        )

        course_id = self.kwargs["course_id"]
        try:
            course = get_object_or_404(Course, id=course_id)
        except Http404:
            error_message = {"detail": "course not found."}

            raise JsonResponse(
                error_message,
                status=status.HTTP_404_NOT_FOUND,
            )

        emails_not_founded = []
        for course_data in students_courses:
            email = course_data.get("student", {}).get("email")
            if email:
                try:
                    student = Account.objects.get(email=email)
                    StudentCourse.objects.create(
                        course=course,
                        student=student,
                    )
                    course.students.add(student)
                except Account.DoesNotExist:
                    emails_not_founded.append(email)

        if emails_not_founded:
            email_list = ", ".join(emails_not_founded)

            raise ValidationError(
                {"detail": f"No active accounts was found: {email_list}."},
            )
