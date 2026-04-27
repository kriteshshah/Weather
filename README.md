# 🌤️ SkyLens — Django Weather App

A beautiful, full-featured weather application built with Django and the OpenWeatherMap API.
Features live current weather + 5-day forecast with a stunning dark glassmorphism UI.

---

## 📸 Features

- 🌡️ Live current temperature, feels-like, min/max
- 💨 Wind speed, humidity, pressure, visibility
- 🌅 Sunrise & sunset times
- 📅 5-day forecast with weather icons
- 🎨 Animated dark glassmorphism UI
- 📱 Fully responsive (mobile + desktop)
- ⚡ Fast — no JavaScript frameworks, pure CSS animations

---

## 🚀 Quick Setup Guide

### Step 1 — Get a FREE API Key

1. Go to 👉 [https://openweathermap.org/api](https://openweathermap.org/api)
2. Click **Sign Up** (it's free)
3. After signing in, go to **API Keys** tab
4. Copy your default API key (it activates within ~10 minutes)

---

### Step 2 — Add your API key to the project

Open this file:
```
weatherapp/settings.py
```

Find this line near the bottom:
```python
OPENWEATHER_API_KEY = 'YOUR_API_KEY_HERE'
```

Replace `YOUR_API_KEY_HERE` with your actual key:
```python
OPENWEATHER_API_KEY = 'abc123youractualkey'
```

---

### Step 3 — Install & Run

Open your terminal/command prompt in the project folder:

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv

# 2. Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start the server
python manage.py runserver
```

### Step 4 — Open in browser

Visit 👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

Type any city name and hit **Search**! 🎉

---

## 📁 Project Structure

```
weatherapp/
│
├── manage.py                    # Django entry point
├── requirements.txt             # Python dependencies
│
├── weatherapp/                  # Main Django config
│   ├── settings.py              # ← PUT YOUR API KEY HERE
│   ├── urls.py
│   └── wsgi.py
│
└── weather/                     # Weather app
    ├── views.py                 # All logic & API calls
    ├── urls.py                  # App routing
    ├── models.py
    └── templates/
        └── weather/
            └── index.html       # Full UI template
```

---

## 🔧 API Used

- **OpenWeatherMap** — [https://openweathermap.org](https://openweathermap.org)
  - `GET /data/2.5/weather` — Current weather
  - `GET /data/2.5/forecast` — 5-day / 3-hour forecast
  - Units: Metric (°C)

---

## 🛠️ Troubleshooting

| Issue | Fix |
|-------|-----|
| `Invalid API key` | Check that the key is pasted correctly in settings.py |
| `City not found` | Check spelling or try a larger nearby city |
| API key not working | Wait 10 minutes after registering — keys need activation |
| Port already in use | Use `python manage.py runserver 8080` to use port 8080 |

---

## ✨ Built With

- **Django 4.2** — Python web framework
- **Requests** — HTTP calls to weather API
- **OpenWeatherMap API** — Weather data
- **Pure CSS** — Animations, glassmorphism, responsive layout
- **Google Fonts** — Syne + DM Sans
# Weather
