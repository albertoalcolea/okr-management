from django.conf.urls import patterns, url

from okr import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^archived/$', views.archived, name='archived'),
    url(r'^edit_kr/$', views.edit_kr, name='edit_kr'),
    url(r'^show_kr/(?P<id>\d+)$', views.show_kr, name='show_kr'),
)