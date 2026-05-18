from django.contrib import admin
from .models import Doctor, Test, Test_Data, Stimulus, Response

# Register your models here.
admin.site.register(Doctor)
admin.site.register(Test)
admin.site.register(Test_Data)
admin.site.register(Stimulus)
admin.site.register(Response)
