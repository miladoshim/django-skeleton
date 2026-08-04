import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_new_income_to_coach_notification
from .models import CoachIncome, Payout


@receiver(post_save, sender=CoachIncome)
def created_coach_income(sender, instance, created, *args, **kwargs):
    if created:
        print("----------------------new coach income--------------------")
        coach = instance.coach
        course = instance.course
        amount = instance.amount
        logging.info(f"create new coach income for {coach.uuid} {amount}")
        # send_new_income_to_coach_notification.delay(coach, course, amount)


@receiver(post_save, sender=Payout)
def created_coach_income(sender, instance, created, *args, **kwargs):
    if created:
        print("----------------------new payout created --------------------")
