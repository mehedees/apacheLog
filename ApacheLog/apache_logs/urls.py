from django.conf.urls import url

from .views import create, parse_log, load_log_format, log_list

urlpatterns = [
    url(r'^upload_log/$', create, name='upload_log'),
    url(r'^parse/$', parse_log, name='parse_log'),
    url(r'^log_list/$', log_list, name='log_list'),
    url(r'^load_log_format/$', load_log_format, name='load_log_format'),
]
