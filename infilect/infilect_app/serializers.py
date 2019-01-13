from rest_framework import serializers
from .models import Group, Photo
from django.db import transaction
from django.contrib.auth import get_user_model

User = get_user_model()


class GroupSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        with transaction.atomic():
            group = Group(**validated_data)
            group.save()
            return group

    class Meta:
        model = Group
        fields = ('id', 'name', 'created_by', 'created_at', 'photos')


class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.CharField(required=False)

    def create(self, validated_data):
        with transaction.atomic():
            f = Photo(**validated_data)
            f.save()
        return f

    class Meta:
        model = Photo
        fields = ('id', 'title', 'ownership', 'group', 'image', 'url')


class GroupPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('id', 'title', 'ownership', 'group', 'image', 'url')
