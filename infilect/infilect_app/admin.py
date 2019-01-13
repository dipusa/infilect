from django.contrib import admin

from .models import CustomUser, Photo, Group

admin.site.register(CustomUser)
admin.site.register(Photo)
admin.site.register(Group)
