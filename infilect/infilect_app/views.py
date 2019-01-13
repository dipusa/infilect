from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from .forms import LoginForm, PhotoUploadForm
from .models import Token, Group, Photo
from .serializers import GroupSerializer, PhotoSerializer, GroupPhotoSerializer
from .authentication import JWTAuthentication
from django.core.exceptions import ObjectDoesNotExist
from .paginator_mixin import PaginatorMixin
from rest_framework.settings import api_settings

# Create your views here.
User = get_user_model()


class LoginView(APIView):
    def post(self, request, format=None):
        form = LoginForm(request.data)
        if form.is_valid():
            tokens_and_user_detail = Token.generate_auth_token(form.user)
            tokens_and_user_detail['user_id'] = str(form.user.id)
            tokens_and_user_detail['username'] = form.user.username
            tokens_and_user_detail['first_name'] = form.user.first_name
            tokens_and_user_detail['last_name'] = form.user.last_name
            tokens_and_user_detail['full_name'] = form.user.full_name
            return Response(tokens_and_user_detail)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupView(APIView, PaginatorMixin):
    authentication_classes = (JWTAuthentication, PaginatorMixin)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request):
        user_id = request.user.get('user_id')
        group = Group.objects.filter(created_by=user_id)
        page = self.paginate_queryset(group)
        serializer = GroupSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        request.data['created_by'] = request.user.get('user_id')
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                Group.objects.get(name=request.data['name'])
            except ObjectDoesNotExist:
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            else:
                return Response({'error': "Group already exist"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class PhotoView(APIView, PaginatorMixin):
    authentication_classes = (JWTAuthentication, PaginatorMixin)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def post(self, request):
        form = PhotoUploadForm(request.data)
        if form.is_valid():
            form.save()
            return Response(form.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        group_id = request.query_params.get('group_id', None)
        if group_id is None:
            return Response(
                {'error': "pass group_id as query params to get photos"},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            photos = Photo.objects.filter(group=group_id)
            page = self.paginate_queryset(photos)
            serializer = GroupPhotoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)


class GroupPhotoView(APIView, PaginatorMixin):
    authentication_classes = (JWTAuthentication, PaginatorMixin)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request, group_id):
        photos = Photo.objects.filter(group=group_id)
        page = self.paginate_queryset(photos)
        serializer = GroupPhotoSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        pass


class PhotoDetailView(APIView):
    authentication_classes = (JWTAuthentication,)

    def get(self, request, photo_id):
        try:
            photos = Photo.objects.get(id=photo_id)
            serializer = PhotoSerializer(photos)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {'error': "No photos exists associated with the id you provided"},
                status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = (JWTAuthentication,)

    def post(self, request):
        user_id = request.user.get('user_id')
        Token.invalidateRefreshToken(user_id)
        return Response({"success": "Logout successfull"}, status=status.HTTP_200_OK)
