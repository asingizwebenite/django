from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

def landing(request):
    return render(request, 'tasks/landing.html')

@login_required
def dashboard(request):
    user = request.user
    user_tasks = Task.objects.filter(user=user)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()
    
    # Calculate progress percentage safely
    progress_percentage = 0
    if total_tasks > 0:
        progress_percentage = (completed_tasks / total_tasks) * 100
    
    one_week_ago = timezone.now() - timedelta(days=7)
    tasks_added_this_week = user_tasks.filter(created_at__gte=one_week_ago).count()
    overdue_tasks = user_tasks.filter(to_complete_at__lt=timezone.now(), completed=False).count()

    recent_tasks = user_tasks.order_by('-created_at')[:5]
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percentage': progress_percentage,  # Add this line
        'tasks_added_this_week': tasks_added_this_week,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user)  # Corrected filter syntax
    return render(request, 'tasks/tasks.html', {'tasks': tasks})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'tasks/login.html', {'error': 'Invalid credentials'})
    return render(request, 'tasks/login.html')

@login_required
def toggle_task(request, id):
    if request.method == 'POST':
        try:
            # Get the task belonging to the current user
            task = Task.objects.get(id=id, user=request.user)
            
            # Toggle the completed status
            task.completed = not task.completed
            task.save()
            
            return JsonResponse({
                'success': True,
                'completed': task.completed,
                'task_id': task.id
            })
            
        except Task.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Task not found'
            }, status=404)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)


@login_required
def delete_task(request, id):
    task = get_object_or_404(Task, id=id)
    task.delete()
    return redirect('tasks')

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/signup.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('/')

@login_required
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        Task.objects.create(title=title, description=description, user=request.user)  # Associate with user
        return redirect('tasks')
    return render(request, 'tasks/task_form.html')

@login_required
def update_task(request, id):
    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.completed = 'completed' in request.POST
        task.save()
        return redirect('tasks')
    return render(request, 'tasks/task_form.html', {'task': task})