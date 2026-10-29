from django.contrib import admin

from .models import Cat


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ['name', 'breed', 'sex', 'is_adopted', 'colony', 'created_at']
    list_filter = ['sex', 'is_adopted', 'colony']
    search_fields = ['name', 'breed']
