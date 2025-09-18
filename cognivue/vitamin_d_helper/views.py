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
    Get weather data from Open-Meteo API (free, no API key required)
    """
    try:
        # Default coordinates (Melbourne)
        lat, lon = -37.8136, 144.9631
        location_name = "Melbourne, Australia"
        
        # Try to get coordinates from profile
        if profile.has_location():
            lat, lon = profile.latitude, profile.longitude
            # Try to get location name from reverse geocoding
            detailed_location, country = reverse_geocode(lat, lon)
            if detailed_location:
                location_name = detailed_location
            else:
                # Show coordinates if reverse geocoding fails
                location_name = f"Location ({lat:.4f}, {lon:.4f})"
        elif profile.city:
            # For city names, we'll use geocoding to get coordinates
            geocode_result = geocode_city(profile.city)
            if geocode_result:
                lat, lon = geocode_result['lat'], geocode_result['lon']
                location_name = geocode_result['name']
        else:
            # For default Melbourne coordinates, ensure we have the city name
            location_name = "Melbourne, Australia"
        
        # Get weather data from Open-Meteo API
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current': 'temperature_2m,relative_humidity_2m,weather_code,uv_index',
            'timezone': 'auto'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current = data.get('current', {})
        
        # Map weather codes to descriptions
        weather_code = current.get('weather_code', 0)
        condition = get_weather_description(weather_code)
        
        return {
            'location': location_name,
            'condition': condition,
            'temp': round(current.get('temperature_2m', 22)),
            'uv_index': round(current.get('uv_index', 5)),
            'humidity': round(current.get('relative_humidity_2m', 60)),
        }
        
    except Exception as e:
        print(f"Weather API error: {e}")
        # Return default data if API fails
        return {
            'location': 'Melbourne, Australia',
            'condition': 'Partly Cloudy',
            'temp': 22,
            'uv_index': 5,
            'humidity': 60,
        }

def get_weather_description(weather_code):
    """
    Map Open-Meteo weather codes to human-readable descriptions
    """
    weather_codes = {
        0: 'Clear Sky',
        1: 'Mainly Clear',
        2: 'Partly Cloudy',
        3: 'Overcast',
        45: 'Fog',
        48: 'Depositing Rime Fog',
        51: 'Light Drizzle',
        53: 'Moderate Drizzle',
        55: 'Dense Drizzle',
        56: 'Light Freezing Drizzle',
        57: 'Dense Freezing Drizzle',
        61: 'Slight Rain',
        63: 'Moderate Rain',
        65: 'Heavy Rain',
        66: 'Light Freezing Rain',
        67: 'Heavy Freezing Rain',
        71: 'Slight Snow',
        73: 'Moderate Snow',
        75: 'Heavy Snow',
        77: 'Snow Grains',
        80: 'Slight Rain Showers',
        81: 'Moderate Rain Showers',
        82: 'Violent Rain Showers',
        85: 'Slight Snow Showers',
        86: 'Heavy Snow Showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with Slight Hail',
        99: 'Thunderstorm with Heavy Hail'
    }
    return weather_codes.get(weather_code, 'Unknown')

def geocode_city(city_name):
    """
    Get coordinates for a city using Open-Meteo geocoding API
    """
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            'name': city_name,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = data.get('results', [])
        
        if results:
            result = results[0]
            return {
                'lat': result['latitude'],
                'lon': result['longitude'],
                'name': f"{result['name']}, {result.get('country', '')}"
            }
        
        return None
        
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None

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
    Reverse geocode coordinates to get detailed location information
    Using Nominatim (OpenStreetMap) free geocoding API
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lon,
            'zoom': 18,
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'VitaminDHelper/1.0 (your-email@example.com)'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        address = data.get('address', {})
        
        # Build detailed location string
        location_parts = []
        
        # Add suburb/neighbourhood if available
        if address.get('neighbourhood'):
            location_parts.append(address['neighbourhood'])
        elif address.get('suburb'):
            location_parts.append(address['suburb'])
        
        # Add city
        if address.get('city'):
            location_parts.append(address['city'])
        elif address.get('municipality'):
            location_parts.append(address['municipality'])
        
        # Add state if available
        if address.get('state'):
            location_parts.append(address['state'])
        
        # Add country
        country = address.get('country', 'Australia')
        location_parts.append(country)
        
        location_name = ', '.join(location_parts)
        return location_name, country
            
    except Exception as e:
        print(f"Reverse geocoding error for coordinates ({lat}, {lon}): {e}")
        print(f"Request URL: {url}")
        print(f"Request params: {params}")
        pass
    
    return None, None


# API Views for Frontend Integration
@csrf_exempt
def get_weather_api(request):
    """API endpoint to get weather data"""
    if request.method == 'GET':
        try:
            # Get location from query parameters
            lat = request.GET.get('lat')
            lon = request.GET.get('lon')
            city = request.GET.get('city')
            
            # Create a temporary profile object for weather data
            class TempProfile:
                def __init__(self):
                    self.latitude = float(lat) if lat else None
                    self.longitude = float(lon) if lon else None
                    self.city = city
                
                def has_location(self):
                    return self.latitude is not None and self.longitude is not None
            
            profile = TempProfile()
            weather_data = get_weather_data(profile)
            
            # Return mock data if no API key is configured
            if not weather_data:
                weather_data = {
                    'location': 'Melbourne, Australia',
                    'condition': 'Partly Cloudy',
                    'temp': 22,
                    'uv_index': 6,
                    'humidity': 65
                }
            
            return JsonResponse({
                'success': True,
                'weather': weather_data,
                'is_good_conditions': is_good_conditions(weather_data)
            })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def get_skin_types_api(request):
    """API endpoint to get all skin types"""
    if request.method == 'GET':
        try:
            skin_types = SkinType.objects.all()
            data = []
            for skin_type in skin_types:
                data.append({
                    'id': skin_type.id,
                    'type': skin_type.type,
                    'name': skin_type.get_type_display(),
                    'min_exposure_minutes': skin_type.min_exposure_minutes,
                    'max_exposure_minutes': skin_type.max_exposure_minutes
                })
            
            return JsonResponse({
                'success': True,
                'skin_types': data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def get_recommendation_api(request):
    """API endpoint to get sun exposure recommendation"""
    if request.method == 'GET':
        try:
            skin_type_id = request.GET.get('skin_type_id')
            
            if not skin_type_id:
                return JsonResponse({
                    'success': False,
                    'error': 'skin_type_id parameter is required'
                })
            
            try:
                skin_type = SkinType.objects.get(id=skin_type_id)
                
                # Calculate recommended time (midpoint of range)
                recommended_minutes = (skin_type.min_exposure_minutes + skin_type.max_exposure_minutes) // 2
                
                return JsonResponse({
                    'success': True,
                    'recommendation': {
                        'skin_type': {
                            'id': skin_type.id,
                            'type': skin_type.type,
                            'name': skin_type.get_type_display()
                        },
                        'min_minutes': skin_type.min_exposure_minutes,
                        'max_minutes': skin_type.max_exposure_minutes,
                        'recommended_minutes': recommended_minutes,
                        'recommended_seconds': recommended_minutes * 60
                    }
                })
                
            except SkinType.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Skin type not found'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})