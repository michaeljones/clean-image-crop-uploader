from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.upload, name='ajax-upload'),
    url(r'^crop/$', views.crop, name='cicu-crop'),
]
