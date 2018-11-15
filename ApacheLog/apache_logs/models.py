from __future__ import unicode_literals

from django.db import models

# Create your models here.
from sites.models import Site
from log_formats.models import LogFormats


class ApacheAccessLog(models.Model):

    REQUEST_METHODS = (
        ('GET', 'Get'),
        ('POST', 'POST'),
        ('PUT', 'Put'),
        ('DELETE', 'Delete'),
        ('HEAD', 'Head'),
        ('CONNECT', 'Connect'),
        ('OPTIONS', 'Options'),
        ('TRACE', 'Trace'),
        ('PATCH', 'Patch'),
    )

    full_line = models.TextField(unique=True)
    remote_host = models.GenericIPAddressField(null=True)
    remote_logname = models.TextField(null=True)
    remote_user = models.TextField(null=True)
    request_first_line = models.TextField(null=True)
    request_header_referer = models.TextField(null=True)
    request_header_user_agent = models.TextField(null=True)
    request_header_user_agent_browser_family = models.TextField(null=True)
    request_header_user_agent_browser_version_string = models.CharField(max_length=10, null=True)
    request_header_user_agent_is_mobile = models.NullBooleanField()
    request_header_user_agent_os_family = models.CharField(max_length=25, null=True)
    request_header_user_agent_os_version_string = models.CharField(max_length=10, null=True)
    request_http_ver = models.CharField(max_length=10, null=True)
    request_method = models.CharField(max_length=10, null=True, choices=REQUEST_METHODS)
    request_url = models.TextField()
    request_url_fragment = models.TextField(null=True)
    request_url_hostname = models.TextField(null=True)
    request_url_netloc = models.TextField(null=True)
    request_url_password = models.TextField(null=True)
    request_url_path = models.TextField(null=True)
    request_url_port = models.IntegerField(null=True)
    request_url_query = models.TextField(null=True)
    request_url_query_dict = models.TextField(null=True)
    request_url_query_list = models.TextField(null=True)
    request_url_query_simple_dict = models.TextField(null=True)
    request_url_scheme = models.TextField(null=True)
    request_url_username = models.TextField(null=True)
    response_bytes = models.DecimalField(decimal_places=6, max_digits=60, null=True)
    status = models.IntegerField(null=True)
    time_received = models.TextField(null=True)
    time_received_datetimeobj = models.DateTimeField(null=True)
    time_received_isoformat = models.TextField(null=True)
    time_received_tz_datetimeobj = models.DateTimeField(null=True)
    time_received_tz_isoformat = models.TextField(null=True)
    time_received_utc_datetimeobj = models.DateTimeField(null=True)
    time_received_utc_isoformat = models.TextField(null=True)
    time_second = models.DecimalField(decimal_places=6, max_digits=60, null=True)
    time_millisecond = models.DecimalField(decimal_places=6, max_digits=60, null=True)

    log_format = models.ForeignKey(LogFormats, on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=True, null=True)

    @property
    def request_header_user_agent__browser__family(self):
        return self.request_header_user_agent_browser_family

    @request_header_user_agent__browser__family.setter
    def request_header_user_agent__browser__family(self, value):
        self.request_header_user_agent_browser_family = value

    @property
    def request_header_user_agent__browser__version_string(self):
        return self.request_header_user_agent_browser_version_string

    @request_header_user_agent__browser__version_string.setter
    def request_header_user_agent__browser__version_string(self, value):
        self.request_header_user_agent_browser_version_string = value

    @property
    def request_header_user_agent__is_mobile(self):
        return self.request_header_user_agent_is_mobile

    @request_header_user_agent__is_mobile.setter
    def request_header_user_agent__is_mobile(self, value):
        self.request_header_user_agent_is_mobile = value

    @property
    def request_header_user_agent__os__family(self):
        return self.request_header_user_agent_os_family

    @request_header_user_agent__os__family.setter
    def request_header_user_agent__os__family(self, value):
        self.request_header_user_agent_os_family = value

    @property
    def request_header_user_agent__os__version_string(self):
        return self.request_header_user_agent_os_version_string

    @request_header_user_agent__os__version_string.setter
    def request_header_user_agent__os__version_string(self, value):
        self.request_header_user_agent_os_version_string = value

    @property
    def response_bytes_clf(self):
        return self.response_bytes

    @response_bytes_clf.setter
    def response_bytes_clf(self, value):
        try:
            value = float(value)
        except Exception as e:
            value = None
        self.response_bytes = value

    @property
    def time_s(self):
        return self.time_second

    @time_s.setter
    def time_s(self, value):
        try:
            value = float(value)
        except Exception as e:
            value = None
        self.time_second = value

    @property
    def time_us(self):
        return self.time_millisecond

    @time_us.setter
    def time_us(self, value):
        try:
            value = float(value)
        except Exception as e:
            value = None
        self.time_millisecond = value

    @property
    def response_time(self):
        if self.time_millisecond:
            return self.time_millisecond/1000000
        else:
            0

    @property
    def receive_time(self):
        if self.time_received_datetimeobj:
            return self.time_received_datetimeobj.strftime("%d/%b/%Y:%H:%M:%S")
        else:
            ""



class ApacheErrorLog(models.Model):
    full_line = models.TextField()
    time = models.TextField()
    log_module = models.TextField(null=True)
    log_level = models.TextField()
    pid = models.IntegerField(null=True)
    tid = models.IntegerField(null=True)
    src_fileName = models.TextField(null=True)
    status = models.TextField(null=True)
    remote_host = models.GenericIPAddressField(null=True)
    error_msg = models.TextField(null=True)
    referer = models.TextField(null=True)
    log_format = models.ForeignKey(LogFormats, on_delete=models.CASCADE, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, blank=True, null=True)

    def __unicode__(self):
        return "<Error Log :: %s :: %s :: %s :: %s :: %s :: %s :: %s :: %s :: %s :: %s :: %s :: %s :: %s>" % (self.full_line, self.time, self.log_module, self.log_level, self.pid, self.tid, self.src_fileName, self.status, self.remote_host, self.error_msg, self.referer, self.log_format, self.site)