from django.conf.urls import patterns, url

from okr import views


urlpatterns = patterns('',
    url(r'^$', views.visible, name='index'),
    url(r'^archived/$', views.archived, name='archived'),
    url(r'^archived/page/(?P<page>\d+)$', views.archived_paged, name='archived_paged'),
    url(r'^edit_kr/$', views.edit_kr, name='edit_kr'),
    url(r'^show_kr/(?P<id>\d+)$', views.show_kr, name='show_kr'),
    url(r'^add_kr/(?P<o>\d+)$', views.add_kr, name='add_kr'),
    url(r'^delete_kr/(?P<id>\d+)/$', views.delete_kr, name='delete_kr'),
    url(r'^add_obj/$', views.add_obj, name='add_obj'),
    url(r'^edit_obj/(?P<id>\d+)$', views.edit_obj, name='edit_obj'),
    url(r'^delete_obj/(?P<id>\d+)/$', views.delete_obj, name='delete_obj'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
)