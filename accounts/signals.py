from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Account, BalanceAdjustment


@receiver(pre_save, sender=Account)
def set_starting_balance_datetime(sender, instance, created, **kwargs):
    """Set datetime of starting balance update if changed"""
    if (
        "update_fields" in kwargs
        and "starting_balance" in kwargs["update_fields"]
        and "starting_balance_datetime" not in kwargs["update_fields"]
    ):
        instance.starting_balance_datetime = timezone.now()


@receiver(pre_save, sender=BalanceAdjustment)
def update_balance_with_adjustment(sender, instance, created, **kwargs):
    if created:
        old_amount = 0
    else:
        old_obj = BalanceAdjustment.objects.get(pk=instance.pk)
        old_amount = old_obj.amount

    instance.account.update_balance(old_amount, instance.amount)


@receiver(post_delete, sender=BalanceAdjustment)
def remove_adjustment(sender, instance, **kwargs):
    old_amount = instance.amount
    instance.account.update_balance(old_amount, 0)
