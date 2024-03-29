from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    url(r'^$', views.DatumList.as_view()),
    url(r'^(?P<pk>[0-9]+)$', views.DatumDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
