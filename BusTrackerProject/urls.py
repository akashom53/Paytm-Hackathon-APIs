"""BusTrackerProject URL Configuration

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
from django.conf.urls import url
from django.contrib import admin
from bustrackerapp import views as v
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from bustrackerapp import apis

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', v.index),
    url(r'^saveBus/', apis.saveBus),
    url(r'^getBusList/', apis.getBusList),
    url(r'^login/', apis.login),
    url(r'^updateBusLocation/', apis.updateBusLocation),
    url(r'^searchBusStops/', apis.searchBusStops),
    url(r'^searchBuses/', apis.searchBuses),
    url(r'^boardingConfirm/', apis.boardingConfirm),
    url(r'^exitConfirm/', apis.exitConfirm),
    url(r'^getBusData/', apis.getBusData),
    url(r'^getRouteStops/', apis.getRouteStops),
    url(r'^test/', apis.testjson),
]

urlpatterns += staticfiles_urlpatterns()