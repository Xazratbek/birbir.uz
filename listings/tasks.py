from celery_singleton import Singleton
from celery import shared_task
import time
from .models import Listing

@shared_task(base=Singleton)
def singleton_task(elon_id):
    time.sleep(20)
    elon = Listing.objects.filter(id=elon_id).first()
    print(elon.title)
    print("Singleton Vazifa taski ishladi 20 sekund")

@shared_task()
def oddy_task():
    time.sleep(15)
    print("Vazifa taski ishladi 15 sekund")