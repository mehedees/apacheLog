from __future__ import unicode_literals

from django.db import models
from sites.models import Site


class LogFormats(models.Model):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    log_type = models.CharField(max_length=20, choices=[('access_log', 'Access Log'), ('error_log', 'Error Log')], default='access_log')
    log_format = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __unicode__(self):
        return self.log_format
