from django.conf.urls import url
from .views import log_format_add_page, log_format_edit_page, log_format_list_page, log_format_delete_page, set_default_log_format


urlpatterns = [
    url(r'^add/$', log_format_add_page, name='log_format_add'),
    url(r'^(?P<id>\d+)/edit/$', log_format_edit_page, name='log_format_edit'),
    url(r'^list/$', log_format_list_page, name='log_format_list'),
    url(r'^(?P<id>\d+)/delete/$', log_format_delete_page, name='log_format_delete'),
    url(r'^(?P<id>\d+)/set_default_logformat/$', set_default_log_format, name='set_default_log_format'),
]
