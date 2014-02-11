from django.conf.urls import patterns, url

from okr import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^archived/$', views.archived, name='archived'),
    url(r'^edit_kr/$', views.edit_kr, name='edit_kr'),
    url(r'^show_kr/(?P<id>\d+)$', views.show_kr, name='show_kr'),
    url(r'^add_kr/(?P<o>\d+)$', views.add_kr, name='add_kr'),
    url(r'^add_obj/$', views.add_obj, name='add_obj'),
    url(r'^edit_obj/(?P<id>\d+)$', views.edit_obj, name='edit_obj'),
)