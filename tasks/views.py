from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
from .models import Task
from .forms import TaskForm

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
        'progress_percentage': progress_percentage,
        'tasks_added_this_week': tasks_added_this_week,
        'overdue_tasks': overdue_tasks,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tasks/tasks.html', {'tasks': tasks})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
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
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'POST':
        task_title = task.title
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted successfully!')
        return redirect('tasks')
    return redirect('tasks')

def user_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'tasks/signup.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')

@login_required
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            # Handle empty due date
            if not task.to_complete_at:
                task.to_complete_at = None
                
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('tasks')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def update_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('tasks')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def calendar(request):
    user_tasks = Task.objects.filter(user=request.user)
    
    # Prepare calendar events data
    calendar_events = []
    for task in user_tasks:
        # Determine color based on task status and priority
        if task.completed:
            color = '#10B981'  # Green for completed
        elif task.is_overdue:
            color = '#EF4444'  # Red for overdue
        else:
            if task.priority == 'high':
                color = '#EF4444'  # Red for high priority
            elif task.priority == 'medium':
                color = '#F59E0B'  # Yellow for medium priority
            else:
                color = '#3B82F6'  # Blue for low/no priority
        
        event_data = {
            'id': task.id,
            'title': task.title,
            'start': task.to_complete_at.isoformat() if task.to_complete_at else None,
            'color': color,
            'extendedProps': {
                'description': task.description or '',
                'priority': task.priority or '',
                'completed': task.completed,
                'is_overdue': task.is_overdue,
                'created_at': task.created_at.isoformat(),
            }
        }
        calendar_events.append(event_data)
    
    # Convert to JSON string
    calendar_events_json = json.dumps(calendar_events)
    
    # Get tasks for the next 7 days for the upcoming deadlines sidebar
    upcoming_tasks = user_tasks.filter(
        to_complete_at__gte=timezone.now(),
        to_complete_at__lte=timezone.now() + timedelta(days=7)
    ).order_by('to_complete_at')
    
    # Calculate stats
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()
    pending_tasks = user_tasks.filter(completed=False).count()
    overdue_tasks = user_tasks.filter(
        to_complete_at__lt=timezone.now(), 
        completed=False
    ).count()
    
    # Monthly stats (simplified)
    monthly_stats = []
    today = timezone.now()
    for i in range(7):  # Last 7 days
        date = today - timedelta(days=i)
        day_tasks = user_tasks.filter(
            to_complete_at__date=date.date()
        ).count()
        monthly_stats.append({
            'date': date,
            'count': day_tasks,
            'percentage': min(day_tasks * 20, 100) if day_tasks > 0 else 0
        })
    
    context = {
        'calendar_events_json': calendar_events_json,
        'upcoming_tasks': upcoming_tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'monthly_stats': monthly_stats,
    }
    return render(request, 'tasks/calendar.html', context)