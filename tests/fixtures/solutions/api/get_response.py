import requests
from typing import Dict, Any, Optional


class WeatherClient:
    def __init__(self, api_key: str, base_url: str = "https://api.openweathermap.org/data/2.5"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_current_weather(self, city: str) -> Dict[str, Any]:
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_forecast(self, city: str, days: int = 5) -> Dict[str, Any]:
        url = f"{self.base_url}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "cnt": days * 8
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict[str, Any]:
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()


class NewsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
    
    def get_top_headlines(self, country: str = "us", category: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/top-headlines"
        params = {
            "country": country,
            "apiKey": self.api_key
        }
        
        if category:
            params["category"] = category
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def search_articles(self, query: str, sort_by: str = "publishedAt") -> Dict[str, Any]:
        url = f"{self.base_url}/everything"
        params = {
            "q": query,
            "sortBy": sort_by,
            "apiKey": self.api_key
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()