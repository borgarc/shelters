from django.db import models


class Cat(models.Model):
    class Sex(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=1, choices=Sex.choices)
    birth_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_adopted = models.BooleanField(default=False)
    colony = models.ForeignKey(
        'colonies.Colony',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cats',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
