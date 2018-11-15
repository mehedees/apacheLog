from django.conf.urls import url

from .views import create, parse_log, load_log_format, access_log_list, error_log_list

urlpatterns = [
    url(r'^upload_log/$', create, name='upload_log'),
    url(r'^parse/$', parse_log, name='parse_log'),
    url(r'^access_log$', access_log_list, name='access_log_list'),
    url(r'^error_log$', error_log_list, name='error_log_list'),
    url(r'^load_log_format/$', load_log_format, name='load_log_format'),
]
