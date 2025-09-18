from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import TimerSession
import json

def timer_page(request):
    """Main timer page"""
    return render(request, 'timer/timer.html')

# @csrf_exempt
# def start_timer(request):
#     """API endpoint to start timer"""
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             duration = int(data.get('duration', 0))
            
#             # Here you could save to database if user is authenticated
#             # if request.user.is_authenticated:
#             #     TimerSession.objects.create(user=request.user, duration=duration)
            
#             return JsonResponse({
#                 'success': True,
#                 'duration': duration,
#                 'message': f'Timer started for {duration} seconds'
#             })
#         except (ValueError, TypeError):
#             return JsonResponse({'success': False, 'error': 'Invalid duration'})
    
#     return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def start_timer(request, minutes=0):
    # Convert minutes to seconds for the timer
    seconds = int(minutes) * 60
    
    return render(request, 'timer/timer.html', {
        'initial_seconds': seconds,
        'minutes': minutes,
        'title': f'Sun Exposure Timer - {minutes} minutes'
    })

def timer_view(request, minutes=None):
    if minutes:
        # Convert to seconds for the timer
        seconds = int(minutes) * 60
    else:
        seconds = 0
    
    return render(request, 'timer/timer.html', {
        'initial_seconds': seconds,
        'recommended_minutes': minutes
    })

def timer_api(request, minutes):
    """API endpoint for timer data"""
    seconds = int(minutes) * 60
    return JsonResponse({
        'seconds': seconds,
        'minutes': minutes,
        'recommended': True
    })

@csrf_exempt
@require_http_methods(["POST"])
def save_timer_session(request):
    """API endpoint to save a completed timer session"""
    try:
        data = json.loads(request.body)
        duration = int(data.get('duration', 0))  # Duration in seconds
        completed = data.get('completed', True)
        
        # Create timer session
        session = TimerSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            duration=duration,
            completed=completed
        )
        
        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'message': 'Timer session saved successfully',
            'session': {
                'id': session.id,
                'duration': session.duration,
                'formatted_duration': session.formatted_duration(),
                'created_at': session.created_at.isoformat(),
                'completed': session.completed
            }
        })
    except (ValueError, TypeError, KeyError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_timer_sessions(request):
    """API endpoint to get user's timer sessions"""
    try:
        # Get recent sessions (last 30 days)
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        
        if request.user.is_authenticated:
            sessions = TimerSession.objects.filter(
                user=request.user,
                created_at__gte=thirty_days_ago
            ).order_by('-created_at')[:20]
        else:
            # For anonymous users, return recent anonymous sessions
            sessions = TimerSession.objects.filter(
                user=None,
                created_at__gte=thirty_days_ago
            ).order_by('-created_at')[:20]
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': session.id,
                'duration': session.duration,
                'formatted_duration': session.formatted_duration(),
                'created_at': session.created_at.isoformat(),
                'date': session.created_at.strftime('%a, %d %b'),
                'time': session.created_at.strftime('%H:%M'),
                'completed': session.completed
            })
        
        return JsonResponse({
            'success': True,
            'sessions': sessions_data,
            'count': len(sessions_data)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)