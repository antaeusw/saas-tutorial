from django.core.management.base import BaseCommand
from subscriptions.models import Subscription
from typing import Any


class Command(BaseCommand):

    """ Sync subscriptions permissions to user groups """


    def handle(self, *args:Any, **options: Any):
        qs = Subscription.objects.filter(active=True)
        for obj in qs:
            #print(obj.groups.all())
            sub_perms = obj.permissions.all()
            for group in obj.groups.all():
                group.permissions.set(sub_perms)
                #for per in obj.permissions.all():
                #    group.permissions.add(per)
            #print(obj.permissions.all())


