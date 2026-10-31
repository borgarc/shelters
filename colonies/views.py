from rest_framework import viewsets
from rest_framework.decorators import action

from cats.serializers import CatSerializer

from .models import Colony
from .serializers import ColonySerializer


class ColonyViewSet(viewsets.ModelViewSet):
    queryset = Colony.objects.with_cat_count()
    serializer_class = ColonySerializer

    @action(detail=True)
    def cats(self, request, pk=None):
        colony = self.get_object()
        page = self.paginate_queryset(colony.cats.all())
        serializer = CatSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
