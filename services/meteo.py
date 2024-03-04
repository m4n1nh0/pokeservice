"""Access Open-Meteo API."""
import requests


class OpenMeteoService:
    """Class for accessing meteorological data."""

    def __init__(self):
        """Initialize this class."""
        self.url = "https://api.open-meteo.com/v1/forecast"

    def get_temperature(self, longitude, latitude):
        """Get temperature.

        :param longitude: from my city or other
        :param latitude: from my city or other
        :returns temperature value
        """

        responses = requests.get(self.url + '?latitude=' + latitude
                                 + '&longitude=' + longitude +
                                 '&current=temperature_2m')
        data = responses.json()

        return data['current']['temperature_2m']

    @staticmethod
    def get_pokemon_type_by_temperature(temperature):
        """Get pokemon type name.

        :param temperature: float value
        :returns type name
        """

        if temperature >= 30:
            return 'fire'
        elif 20 <= temperature < 30:
            return 'rock'
        elif 10 <= temperature < 20:
            return 'normal'
        elif 0 <= temperature < 10:
            return 'water'
        else:
            return 'ice'
