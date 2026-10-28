# Weather Data CLI

A clean, beginner-friendly command-line weather application built in Python using the `requests` library and the free [Open-Meteo APIs](https://open-meteo.com/).

---

## Project Objective

The objective of this project is to build a practical command-line application that retrieves real-time weather information and a 3-day forecast for any given city. It demonstrates fundamental software engineering practices:
- Consuming REST APIs over HTTP
- Geocoding city names into geographical coordinates (latitude and longitude)
- Parsing nested JSON data structures
- Clean terminal output formatting
- Robust defensive error handling for network errors, timeouts, invalid user input, and HTTP error codes

---

## Tools Used

- **Python 3**: Core programming language.
- **`requests` library**: For issuing HTTP GET requests with timeouts.
- **Open-Meteo Geocoding API**: Resolves city names into geographical coordinates (`https://geocoding-api.open-meteo.com/v1/search`).
- **Open-Meteo Weather Forecast API**: Fetches current meteorological metrics and daily forecasts (`https://api.open-meteo.com/v1/forecast`).

---

## Features

1. **Flexible Invocation**:
   - Run with a city argument directly: `python weather_cli.py London`
   - Or run interactively without arguments: `python weather_cli.py`
2. **Interactive Loop**:
   - After displaying weather data, the program asks if you want to look up another city (`y`/`n`) or type `q` to quit.
3. **Clean & Useful Weather Overview**:
   - City and Country name
   - Current Temperature (°C)
   - "Feels Like" Apparent Temperature (°C)
   - Relative Humidity (%)
   - Wind Speed (km/h)
   - Human-readable Weather Condition (mapped from WMO weather codes, e.g. "Clear sky", "Moderate rain showers", "Partly cloudy")
   - Today's Minimum and Maximum Temperature
4. **3-Day Forecast Table**:
   - Neatly aligned ASCII table showing Date, Min Temp, and Max Temp.
5. **No Tracebacks**:
   - All network interruptions, invalid city names, and abnormal inputs are handled cleanly with user-friendly messages.

---

## Installation

1. Navigate to the project directory:
   ```bash
   cd weather_data_cli
   ```

2. (Optional but recommended) Create and activate a virtual environment:
   - **Windows**:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Run

### Option 1: Direct City Name Argument
```bash
python weather_cli.py London
```
Or for multi-word city names:
```bash
python weather_cli.py New York
```

### Option 2: Interactive Prompt
```bash
python weather_cli.py
```
You will be prompted to enter a city name:
```text
Enter city name (or 'q' to quit): Tokyo
```

---

## Sample Formatted Output

```text
============================================
 Current Weather for London, United Kingdom
============================================
 Condition:       Partly cloudy
 Temperature:     8.3°C
 Feels Like:      5.8°C
 Humidity:        81%
 Wind Speed:      9.4 km/h
 Today's Min:     8.2°C
 Today's Max:     15.4°C
============================================
 3-Day Forecast:
--------------------------------------------
 Date           Min Temp     Max Temp    
--------------------------------------------
 2026-10-28     8.2°C        15.4°C      
 2026-10-29     10.5°C       15.8°C      
 2026-10-30     8.8°C        14.9°C      
============================================

Would you like to check another city? (y/n): 
```

---

## Error Handling & Security

- **HTTP Status Codes**:
  - `200`: Success; parses JSON and extracts payload.
  - `404`: Displays `"Error: Service endpoint not found (HTTP 404)."`
  - `429`: Displays `"Error: API rate limit exceeded. Please try again later (HTTP 429)."`
  - Other codes: Displays the specific HTTP status code returned by the server.
- **Input Validation**:
  - Empty input or whitespace-only strings are rejected with a clear prompt to enter a valid city name.
  - Numbers-only or symbols-only inputs (e.g. `12345`, `!@#$%`) are rejected before making unnecessary API calls.
  - Non-existent cities (e.g. `xyzabc123`) return an empty geocoding result, resulting in `"City not found, please check the spelling."` and prompting the user again.
- **Connection Failures & Timeouts**:
  - All network calls use `timeout=10`.
  - Specific exception handling for `requests.exceptions.ConnectionError`, `requests.exceptions.Timeout`, and general `requests.exceptions.RequestException`.
  - Malformed responses are guarded against with JSON decode error handling.
  - `KeyboardInterrupt` (Ctrl+C) and `EOFError` exit politely without traceback dumps.
- **API Key Security**:
  - Open-Meteo is completely free and requires no API key.
  - If a key-based API (such as OpenWeatherMap) were used, API keys should **never** be hardcoded in source code or pushed to source control. Instead, store keys in an environment variable or in a local `.env` file that is listed in `.gitignore`. A sample `.env.example` is provided for reference.

---

## API Questions & Answers

### 1. How do APIs authenticate requests?
APIs authenticate client requests through several common mechanisms:
- **API Keys**: A unique secret token passed as an HTTP query parameter (`?api_key=...`) or custom header (e.g. `X-API-Key: ...`).
- **Bearer Tokens / OAuth 2.0**: Standardized security tokens passed in the `Authorization` header (`Authorization: Bearer <token>`), widely used for user delegation and expiring session access.
- **HTTP Basic Authentication**: Credentials formatted as `username:password` and base64-encoded in the `Authorization: Basic ...` header.
- **Mutual TLS (mTLS)**: Cryptographic certificates exchanged at the transport layer to verify client identity.

### 2. What happens when an API returns a 404?
An HTTP `404 Not Found` response indicates that the server could not find the requested resource or URI endpoint. This occurs when:
- The API URL path or endpoint name is misspelled or has been deprecated.
- A resource identifier passed in the URL does not exist on the server.

A well-behaved application should inspect the status code, avoid attempting to parse non-existent body data, and inform the user with a descriptive error message instead of failing abruptly.

### 3. How would you handle API rate limits?
When an API responds with `429 Too Many Requests` (or approaches designated rate quota limits):
1. **Inspect `Retry-After` Header**: Read the HTTP `Retry-After` response header to identify the exact number of seconds the client must wait before retrying.
2. **Exponential Backoff and Jitter**: If retrying programmatically, wait exponentially longer between attempts (e.g., 1s, 2s, 4s, 8s) combined with random jitter to prevent server thundering herds.
3. **Response Caching**: Store retrieved data in memory or a local cache (e.g., caching weather data for 15–30 minutes) to minimize repeated redundant requests for identical queries.
4. **Client-side Throttling**: Regulate outgoing request frequency with rate limiters or queues to keep traffic within allowed tier limits.
