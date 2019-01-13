from django.conf.urls import url
from infilect_app import views as views


urlpatterns = [
    url(r'^api/v1/login/$', views.LoginView.as_view()),
    url(r'^api/v1/groups/$', views.GroupView.as_view()),
    url(r'api/v1/photos/$', views.PhotoView.as_view()),
    url(r'api/v1/group/(?P<group_id>[0-9a-f-]+)$',
        views.GroupPhotoView.as_view()),
    url(r'api/v1/photos/(?P<photo_id>[0-9a-f-]+)$',
        views.PhotoDetailView.as_view()),

    url(r'^api/v1/logout/$', views.LogoutView.as_view())
]
