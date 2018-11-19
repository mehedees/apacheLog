from django.contrib import admin
from .models import ApacheErrorLog, ApacheAccessLog

# Register your models here.
admin.site.register(ApacheErrorLog)
admin.site.register(ApacheAccessLog)
