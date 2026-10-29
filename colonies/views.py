from django.db.models import Count
from rest_framework import viewsets
from rest_framework.decorators import action

from cats.serializers import CatSerializer

from .models import Colony
from .serializers import ColonySerializer


class ColonyViewSet(viewsets.ModelViewSet):
    queryset = Colony.objects.annotate(num_cats=Count('cats'))
    serializer_class = ColonySerializer

    @action(detail=True)
    def cats(self, request, pk=None):
        colony = self.get_object()
        page = self.paginate_queryset(colony.cats.all())
        serializer = CatSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
