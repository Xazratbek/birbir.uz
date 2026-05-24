from celery_singleton import Singleton
from celery import shared_task
import time
from uuid import UUID

from .models import Listing


@shared_task(base=Singleton)
def singleton_task(elon_id=None, *args, **kwargs):
    time.sleep(20)

    if elon_id is None:
        print("singleton_task ga listing id berilmadi")
        return

    if isinstance(elon_id, UUID):
        elon_id = str(elon_id)

    elon = Listing.objects.filter(id=elon_id).first()
    if elon is None:
        print(f"Listing topilmadi: {elon_id}")
        return

    print(elon.title)
    print("Singleton Vazifa taski ishladi 20 sekund")


@shared_task()
def oddy_task():
    time.sleep(15)
    print("Vazifa taski ishladi 15 sekund")
