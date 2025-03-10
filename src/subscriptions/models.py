from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

User = settings.AUTH_USER_MODEL # the string of "auth.User"


# Create your models here.

ALLOW_CUSTOM_GROUPS = True

SUBSCRIPTION_PERMISSIONS = [
    ("advanced", "Advanced Perm"), #access by "subscriptions.advanced"
    ("pro", "Pro Perm"), #access by "subscriptions.pro"
    ("basic", "Basic Perm"), #access by "subscriptions.basic"
    ("basic_ai", "Basic AI Perm"), #access by "subscriptions.basic_ai"
]

class Subscription(models.Model):
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission,
                    limit_choices_to={
                        "content_type__app_label": "subscriptions",
                         "codename__in":[p[0] for p in SUBSCRIPTION_PERMISSIONS]
                         })
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.subscription.name if self.subscription else 'No Subscription'}"

def user_sub_post_save(sender, instance, created, *args, **kwargs):
    usr_sub_instance = instance
    user = usr_sub_instance.user
    subscription_obj = usr_sub_instance.subscription
    groups_ids = []
    if subscription_obj is not None:
        groups = subscription_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids) #set the groups to the user according to the subscription
    else:
        subs_qs = Subscription.objects.filter(active = True)
        if subscription_obj is not None:
            subs_qs = subs_qs.exclude(id = subscription_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        current_groups = user.groups.all().values_list('id', flat=True) #[1,2,3]
        groups_ids_set = set(groups_ids) 
        current_groups_set = set(current_groups)-subs_groups_set
        final_group_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_group_ids)

post_save.connect(user_sub_post_save, sender=UserSubscription)