from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.chart, name='chart'),
	url(r'newdata/?$', views.newdata, name='newdata'),
]
