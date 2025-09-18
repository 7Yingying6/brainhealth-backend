# OpenWeather API Key Setup Guide

## Get Free OpenWeather API Key

To display real-time weather data and UV index, you need to obtain a free OpenWeather API key.

### Step 1: Register Account
1. Visit [OpenWeatherMap Registration Page](https://openweathermap.org/register)
2. Fill in registration information (email, username, password, etc.)
3. Agree to terms of service and submit registration

### Step 2: Verify Email
1. Check your email inbox
2. Click the confirmation link in the verification email
3. Complete email verification

### Step 3: Get API Key
1. Log in to your OpenWeather account
2. Visit [API Keys Page](https://home.openweathermap.org/api_keys)
3. You will see a default API key has been generated
4. Copy this API key

### Step 4: Configure API Key
1. Open the `.env` file in the project (located at `backend/cognivue/.env`)
2. Replace your API key in the following line:
   ```
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```
3. Save the file

### Step 5: Restart Backend Service
Restart the Django development server to load the new API key.

## Free Plan Limitations
- 1000 API calls per day
- API key activation may take up to 2 hours
- Free access to current weather, 5-day forecast, and UV index data

## Important Notes
- Keep your API key secure, do not expose it in public code
- If the API key was just created, you may need to wait 1-2 hours for activation
- Make sure to use the correct API endpoint: `api.openweathermap.org`

After completing these steps, your application should be able to display real-time weather data and UV index properly.