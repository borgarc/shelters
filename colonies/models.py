from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ColonyQuerySet(models.QuerySet):
    def with_cat_count(self):
        return self.annotate(cat_count=models.Count('cats'))


class Colony(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    caretaker_name = models.CharField(max_length=100, blank=True)
    caretaker_phone = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ColonyQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'colonies'

    def __str__(self):
        return self.name
