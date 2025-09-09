from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# import json

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