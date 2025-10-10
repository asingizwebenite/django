from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def landing(request):
    return render(request, tasks)

@login_required
def dashboard(request):
    tasks = Task.objects.all()
    return render(request, 'tasks/dashboard.html',{'tasks':tasks})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username, password=password )

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        
       
    return render(request, 'tasks/login.html')
   


def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(dashboard)
    else:
        form = UserCreationForm()
    return redirect(request, 'login.html', {'form':form})



def user_logout(request):
    logout(request)
    return redirect('/')







