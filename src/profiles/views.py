from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()

@login_required

def profile_list_view(request, *args, **kwargs):

    context = {
        "object_list": User.objects.filter(is_active=True)
    }

    return render(request, "profiles/list.html", context)

@login_required
def profile_detail_view(request, username=None, *args, **kwargs):
    user = request.user
    print(
        user.has_perm("subscriptions.basic"),
        user.has_perm("subscriptions.basic_ai"),
        user.has_perm("subscriptions.pro"),
        user.has_perm("subscriptions.advanced"),

                      
    )
    #user_groups = user.groups.all()
    #print("user_groups", user_groups)
    #if user_groups.filter(name="basic").exists():
    #    return HttpResponse("Basic Plan")
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    context = {
        "object": profile_user_obj,
        "instance": profile_user_obj,
        "owner": is_me
    }
    return render(request, "profiles/detail.html", context)
