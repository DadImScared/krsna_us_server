"""KrsnaUs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from harikatha.views import AccountConfirm, GoogleLogin, FacebookLogin

regex = r"[\s\d\w().+-_',:&]+"

urlpatterns = [
    url(r'^api/v1/', include('harikatha.urls'), name='harikatha'),
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include('allauth.urls')),
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>{0})/$'.format(regex),
        AccountConfirm.as_view(), name="account_confirm_email"),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^rest-auth/google/$', GoogleLogin.as_view(), name='google_login'),
    url(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login')
]

# urlpatterns += staticfiles_urlpatterns()
