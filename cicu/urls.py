from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.upload, name='ajax-upload'),
    re_path(r'^crop/$', views.crop, name='cicu-crop'),
]
