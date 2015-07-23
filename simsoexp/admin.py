from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(ConfigurationFile)
admin.site.register(TestSet)
admin.site.register(SchedulingPolicy)
admin.site.register(Results)
admin.site.register(TestCategory)
admin.site.register(Notification)

# $uper$trongp@$$w0rd