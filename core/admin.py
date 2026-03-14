from django.contrib import admin
from .models import Temple, Blog


@admin.register(Temple)
class TempleAdmin(admin.ModelAdmin):
    list_display = ('name', 'status')


admin.site.register(Blog)
