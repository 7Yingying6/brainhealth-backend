import json
import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import UserProfile, SkinType
from .forms import SkinTypeForm, CityForm
from math import ceil

@login_required
def vitamin_d_helper(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle skin type form submission
    if 'skin_type_submit' in request.POST:
        form = SkinTypeForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('vitamin_d_helper')
    else:
        form = SkinTypeForm(instance=profile)
    
    # Handle city form submission
    if 'city_submit' in request.POST:
        city_form = CityForm(request.POST, instance=profile)
        if city_form.is_valid():
            # Clear coordinates when manually entering city
            profile.latitude = None
            profile.longitude = None
            city_form.save()
            return redirect('vitamin_d_helper')
    else:
        city_form = CityForm(instance=profile)
    
    # Get weather data
    weather_data = get_weather_data(profile)
    
    # Get recommendation
    recommendation = None
    if profile.skin_type:
        recommendation = {
            'min_minutes': profile.skin_type.min_exposure_minutes,
            'max_minutes': profile.skin_type.max_exposure_minutes
        }
    
    timer_seconds = None
    if recommendation:
        # Use the midpoint of the recommended range
        recommended_mid = (recommendation['min_minutes'] + recommendation['max_minutes']) // 2
        timer_seconds = recommended_mid * 60

    context = {
        'form': form,
        'city_form': city_form,
        'weather_data': weather_data,
        'recommendation': recommendation,
        'is_good_conditions': is_good_conditions(weather_data) if weather_data else False,
        'has_location': profile.has_location(),
        'profile': profile,
        'timer_seconds':timer_seconds,
    }
    
    return render(request, 'vitamin_d_helper.html', context)


def get_weather_data(profile):
    """
    Get weather data for Australian locations
    """
    try:
        # Priority 1: Manual city (user explicitly entered this)
        if profile.city:
            print(f"Using manual city: {profile.city}")
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': f"{profile.city},AU",  # Always append ,AU for Australia
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
        
        # Priority 2: Coordinates from geolocation
        elif profile.has_location():
            print("Using coordinates from geolocation")
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'lat': profile.latitude,
                'lon': profile.longitude,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
        
        # Priority 3: Default fallback to Melbourne
        else:
            print("Using default location: Melbourne")
            url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': 'Melbourne,AU',
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        uv_index = get_uv_index(data['coord']['lat'], data['coord']['lon'])
        
        return {
            'location': f"{data['name']}, Australia",
            'condition': data['weather'][0]['description'].title(),
            'temp': round(data['main']['temp']),
            'uv_index': uv_index,
            'humidity': data['main']['humidity'],
        }
        
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def get_uv_index(lat, lon):
    """
    Get UV index using OpenWeather's One Call API
    """
    try:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            'lat': lat,
            'lon': lon,
            'exclude': 'minutely,hourly,daily,alerts',
            'appid': settings.OPENWEATHER_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        return ceil(data.get('current', {}).get('uvi', 0))
        
    except:
        return 0

def is_good_conditions(weather_data):
    """
    Determine if conditions are good for sun exposure
    """
    uv_index = weather_data.get('uv_index', 0)
    # Good conditions if UV index is between 3 and 7 (moderate)
    return 3 <= uv_index <= 7

@login_required
@require_POST
@csrf_exempt
def update_location_from_coords(request):
    """
    AJAX endpoint to update user location from coordinates
    """
    try:
        data = json.loads(request.body)
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.latitude = latitude
        profile.longitude = longitude
        
        # Reverse geocode to get city and country
        city, country = reverse_geocode(latitude, longitude)
        if city:
            profile.city = city
        if country:
            profile.country = country
        
        profile.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Location updated successfully',
            'city': city,
            'country': country
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

def reverse_geocode(lat, lon):
    """
    Reverse geocode coordinates to get city and country
    Using OpenWeather's reverse geocoding API
    """
    try:
        url = "http://api.openweathermap.org/geo/1.0/reverse"
        params = {
            'lat': lat,
            'lon': lon,
            'limit': 1,
            'appid': settings.OPENWEATHER_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data and len(data) > 0:
            return data[0].get('name'), data[0].get('country')
            
    except:
        pass
    
    return None, None