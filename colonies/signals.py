from django.db.models import F
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .models import Colony


def _increment(colony_id):
    if colony_id is not None:
        Colony.objects.filter(pk=colony_id).update(
            estimated_cat_count=F('estimated_cat_count') + 1
        )


def _decrement(colony_id):
    # Never go below zero: the estimate may have been edited by hand
    if colony_id is not None:
        Colony.objects.filter(pk=colony_id, estimated_cat_count__gt=0).update(
            estimated_cat_count=F('estimated_cat_count') - 1
        )


@receiver(pre_save, sender='cats.Cat')
def remember_previous_colony(sender, instance, **kwargs):
    instance._previous_colony_id = (
        sender.objects.filter(pk=instance.pk)
        .values_list('colony_id', flat=True)
        .first()
        if instance.pk
        else None
    )


@receiver(post_save, sender='cats.Cat')
def update_count_on_save(sender, instance, **kwargs):
    previous = instance._previous_colony_id
    if previous != instance.colony_id:
        _decrement(previous)
        _increment(instance.colony_id)


@receiver(post_delete, sender='cats.Cat')
def update_count_on_delete(sender, instance, **kwargs):
    _decrement(instance.colony_id)
