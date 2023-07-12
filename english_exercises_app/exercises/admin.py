from django.contrib import admin

from .models import Exercise, File, Memory

# Register your models here.
admin.site.register(Exercise)
admin.site.register(File)
admin.site.register(Memory)
