from django.contrib import admin

from cats.models import Cat

from .models import Colony


class CatInline(admin.TabularInline):
    model = Cat
    fields = ['name', 'breed', 'sex', 'is_adopted']
    extra = 0


@admin.register(Colony)
class ColonyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'estimated_cat_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'address', 'city', 'caretaker_name']
    inlines = [CatInline]
