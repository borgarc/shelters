from rest_framework import serializers

from .models import Colony


class ColonySerializer(serializers.ModelSerializer):
    cat_count = serializers.SerializerMethodField()

    class Meta:
        model = Colony
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def get_cat_count(self, obj):
        # Use the queryset annotation when available to avoid an extra query
        if hasattr(obj, 'cat_count'):
            return obj.cat_count
        return obj.cats.count()
