from __future__ import unicode_literals

from django.db import models


class Site(models.Model):
    site_name = models.CharField(max_length=100)
    site_url = models.CharField(max_length=400, unique=True)


    def __unicode__(self):
        return self.site_name