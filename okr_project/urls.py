from django.conf.urls import include, url
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()

# remove "Auth" menu's from admin
admin.site.unregister(Group)


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^okr/', include('okr.urls', namespace='okr')),
]


# Static content
urlpatterns += staticfiles_urlpatterns()