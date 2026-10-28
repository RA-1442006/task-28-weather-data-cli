import os
import sys
import requests

# Reconfigure stdout to utf-8 if supported so degree symbol displays properly
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Map Open-Meteo WMO weather codes to human-readable descriptions
def get_condition(code):
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_codes.get(code, "Unknown")

def validate_city(city_name):
    # Reject empty input or input with only whitespace
    if not city_name or not city_name.strip():
        print("Error: City name cannot be empty. Please enter a valid city.")
        return False
        
    # Reject input that has no letters (e.g. only numbers or symbols)
    has_letter = any(char.isalpha() for char in city_name)
    if not has_letter:
        print("Error: City name must contain letters (cannot be only numbers or symbols).")
        return False
        
    return True

def get_coordinates(city_name):
    # Geocoding API converts city name to latitude and longitude
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1
    }
    
    try:
        # Check for simulated test errors if testing error handling
        test_error = os.environ.get("SIMULATE_ERROR", "").lower()
        if test_error == "connection":
            raise requests.exceptions.ConnectionError("Simulated network connection failure.")
        elif test_error == "timeout":
            raise requests.exceptions.Timeout("Simulated network request timeout.")

        response = requests.get(url, params=params, timeout=10)
        
        # Check HTTP status codes before using data
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                print("Error: Received invalid JSON response from geocoding service.")
                return None
                
            results = data.get("results")
            if not results:
                print("City not found, please check the spelling.")
                return None
                
            city_data = results[0]
            return {
                "name": city_data.get("name"),
                "country": city_data.get("country", ""),
                "latitude": city_data.get("latitude"),
                "longitude": city_data.get("longitude")
            }
        elif response.status_code == 404:
            print("Error: Geocoding service not found (HTTP 404).")
            return None
        elif response.status_code == 429:
            print("Error: API rate limit exceeded. Please try again later (HTTP 429).")
            return None
        else:
            print(f"Error: Geocoding service returned status code {response.status_code}.")
            return None

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the internet. Please check your network connection.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: A network error occurred: {e}")
        return None

def get_weather(lat, lon):
    # Weather forecast API retrieves current weather and daily forecast
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    try:
        # Check for simulated test errors if testing error handling
        test_error = os.environ.get("SIMULATE_ERROR", "").lower()
        if test_error == "connection":
            raise requests.exceptions.ConnectionError("Simulated network connection failure.")
        elif test_error == "timeout":
            raise requests.exceptions.Timeout("Simulated network request timeout.")

        response = requests.get(url, params=params, timeout=10)
        
        # Check HTTP status codes before using data
        if response.status_code == 200:
            try:
                return response.json()
            except Exception:
                print("Error: Received invalid JSON response from weather service.")
                return None
        elif response.status_code == 404:
            print("Error: Weather service endpoint not found (HTTP 404).")
            return None
        elif response.status_code == 429:
            print("Error: API rate limit exceeded. Please try again later (HTTP 429).")
            return None
        else:
            print(f"Error: Weather service returned status code {response.status_code}.")
            return None

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the weather service. Please check your internet connection.")
        return None
    except requests.exceptions.Timeout:
        print("Error: Request timed out. The server took too long to respond.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: A network error occurred: {e}")
        return None

def show_weather(city_info, weather_data):
    current = weather_data.get("current", {})
    daily = weather_data.get("daily", {})
    
    city = city_info["name"]
    country = city_info["country"]
    location = f"{city}, {country}" if country else city
    
    temp = current.get("temperature_2m", "N/A")
    feels_like = current.get("apparent_temperature", "N/A")
    humidity = current.get("relative_humidity_2m", "N/A")
    wind_speed = current.get("wind_speed_10m", "N/A")
    condition = get_condition(current.get("weather_code", -1))
    
    min_temps = daily.get("temperature_2m_min", [])
    max_temps = daily.get("temperature_2m_max", [])
    today_min = min_temps[0] if min_temps else "N/A"
    today_max = max_temps[0] if max_temps else "N/A"
    
    print()
    print("=" * 44)
    print(f" Current Weather for {location}")
    print("=" * 44)
    print(f" Condition:       {condition}")
    print(f" Temperature:     {temp}°C")
    print(f" Feels Like:      {feels_like}°C")
    print(f" Humidity:        {humidity}%")
    print(f" Wind Speed:      {wind_speed} km/h")
    print(f" Today's Min:     {today_min}°C")
    print(f" Today's Max:     {today_max}°C")
    print("=" * 44)

def show_forecast(weather_data):
    daily = weather_data.get("daily", {})
    dates = daily.get("time", [])
    min_temps = daily.get("temperature_2m_min", [])
    max_temps = daily.get("temperature_2m_max", [])
    
    days_to_show = min(3, len(dates), len(min_temps), len(max_temps))
    if days_to_show == 0:
        return
        
    print(" 3-Day Forecast:")
    print("-" * 44)
    print(f" {'Date':<14} {'Min Temp':<12} {'Max Temp':<12}")
    print("-" * 44)
    for i in range(days_to_show):
        date_str = dates[i]
        min_str = f"{min_temps[i]}°C"
        max_str = f"{max_temps[i]}°C"
        print(f" {date_str:<14} {min_str:<12} {max_str:<12}")
    print("=" * 44)
    print()

def process_city(city_name):
    # Validate input
    if not validate_city(city_name):
        return False
        
    city_info = get_coordinates(city_name.strip())
    if not city_info:
        return False
        
    weather_data = get_weather(city_info["latitude"], city_info["longitude"])
    if not weather_data:
        return False
        
    show_weather(city_info, weather_data)
    show_forecast(weather_data)
    return True

def main():
    print("Welcome to the Weather Data CLI!")
    
    # Check if city was provided as command line argument
    if len(sys.argv) > 1:
        city_arg = " ".join(sys.argv[1:]).strip()
        process_city(city_arg)
        
        # Ask if user wants to check another city
        while True:
            try:
                choice = input("Would you like to check another city? (y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nThank you for using Weather CLI. Goodbye!")
                return
                
            if choice in ["n", "no", "q", "quit"]:
                print("Thank you for using Weather CLI. Goodbye!")
                return
            elif choice in ["y", "yes"]:
                break
            else:
                print("Please enter 'y' for yes or 'n' / 'q' to quit.")

    # Interactive loop
    while True:
        try:
            city_input = input("Enter city name (or 'q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nThank you for using Weather CLI. Goodbye!")
            break
            
        if city_input.lower() in ["q", "quit"]:
            print("Thank you for using Weather CLI. Goodbye!")
            break
            
        success = process_city(city_input)
        if not success:
            # If invalid or not found, ask again
            continue
            
        # Ask if user wants to check another city
        ask_again = True
        while ask_again:
            try:
                choice = input("Would you like to check another city? (y/n): ").strip().lower()
            except (KeyboardInterrupt, EOFError):
                print("\nThank you for using Weather CLI. Goodbye!")
                return
                
            if choice in ["n", "no", "q", "quit"]:
                print("Thank you for using Weather CLI. Goodbye!")
                return
            elif choice in ["y", "yes"]:
                ask_again = False
            else:
                print("Please enter 'y' for yes or 'n' / 'q' to quit.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted. Goodbye!")
        sys.exit(0)
