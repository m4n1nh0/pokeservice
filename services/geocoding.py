"""Access Geocoding API."""
import requests


class Geocoding:
    """Class for accessing geolocation."""

    def __init__(self, city: str):
        """Initialize the geocoding class.

        :param city: The city to geolocation, defaults to 'Aracaju' in scheme
        """
        self.city = city
        self.url = 'https://geocoding-api.open-meteo.com/v1/search?name='
        self.result_city = requests.get(self.url + self.city)

    def get_longitude(self):
        """Get the longitude."""
        location = self.result_city.json()
        return str(location['results'][0]['longitude'])

    def get_latitude(self):
        """Get the latitude."""
        location = self.result_city.json()
        return str(location['results'][0]['latitude'])
