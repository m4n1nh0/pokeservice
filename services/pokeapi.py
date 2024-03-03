"""Access Pokémon API."""
import requests
import json


class Pokemon:
    """Class for accessing Pokémon API."""

    def __init__(self):
        """Initialize the Pokémon class."""
        self.poke_name = None
        self.url = 'https://pokeapi.co/api/v2/'

    async def get_pokemon(self, name):
        """Get a pokémon data from name in API.

        :param name: The name of the pokémon
        """
        self.poke_name = name
        pokemon = requests.get(f'{self.url}pokemon/' + self.poke_name)
        if pokemon.status_code != 200:
            return None
        poke_info = json.loads(pokemon.text)
        return poke_info

    async def get_pokemon_by_type(self, name):
        """Get all pokémon data from name in API.

        :param name: The name of the type
        """
        self.poke_name = name
        pokemon = requests.get(f'{self.url}type/' + self.poke_name)
        if pokemon.status_code != 200:
            return None
        type_info = json.loads(pokemon.text)
        return type_info
