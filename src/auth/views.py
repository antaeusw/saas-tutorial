from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

#from django.contrib.auth.models import User
from django.contrib.auth import get_user_model  #recommended way to get the user model over the above

User = get_user_model()

# Create your views here.
def login_view(request):
    print(request.method, request.POST or None)
    if request.method == "POST":
        username = request.POST.get("username" or None)
        password = request.POST.get("password" or None)
        if all([username, password]):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("login here!")
                return redirect('/')
            else:
                print("Invalid credentials")
        else:
            print("Missing username or password")

    return render(request, 'auth/login.html', {})

def register_view(request):
    if request.method == "POST":
        print(request.POST)
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        #Django Forms does this automatically
        #username_exists = User.objects.filter(username__iexact=username).exists()
        #email_exists = User.objects.filter(email__iexact=email).exists()

        try:
            User.objects.create_user(username, email=email, password=password)
        except:
            pass
            
    return render(request, 'auth/register.html', {})



