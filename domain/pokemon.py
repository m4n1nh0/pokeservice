"""Pokémon research json data ."""
import random
from typing import Any


class Pokemon:
    """Pokémon class."""

    def __init__(self, poke_data: dict, poke_type=False):
        """Pokémon constructor.

        :param poke_data: dict
        :param poke_type: True if poke type selected
        """
        self.poke_data = poke_data
        self.type = poke_type
        self.letter = ['i', 'a', 'm']

    async def get_abilities(self):
        """Get abilities.

        :return: dict with abilities
        """
        abilities = []
        if self.type:
            return abilities

        for i in range(0, len(self.poke_data['abilities'])):
            hidden = self.poke_data['abilities'][i]['is_hidden']
            name = self.poke_data['abilities'][i]['ability']['name']
            abilities.append({'isHidden': hidden, 'name': name})

        return abilities

    async def get_name(self):
        """Get name.

        :return: name
        """
        if self.type:
            return None
        return self.poke_data['name']

    async def get_types(self) -> list:
        """Get types of pokémon.
        :returns: possibles names types (fire, water, earth, normal, ...)"""
        types = []
        if self.type:
            return types

        for i in range(0, len(self.poke_data['types'])):
            name = self.poke_data['types'][i]['type']['name']
            types.append({'name': name})
        return types

    async def get_random_pokemon_types(self) -> Any | None:
        """Get one pokémon randomly selected by specify type.
        :returns: possibles pokémon"""
        pokemon = None
        if not self.type:
            return pokemon

        if len(self.poke_data['pokemon']) > 0:
            pokemon = [poke['pokemon']['name']
                       for poke in self.poke_data['pokemon']]
            pokemon = random.choice(pokemon)

        return pokemon

    async def get_larger_pokemon_name(self) -> Any | None:
        """Get pokémon with larger name selected by specify type.
        :returns: larger pokémon name"""
        pokemon = None
        if not self.type:
            return pokemon

        if len(self.poke_data['pokemon']) > 0:
            pokemon = [poke['pokemon']['name']
                       for poke in self.poke_data['pokemon']]
            pokemon = max(pokemon, key=len)

        return pokemon

    async def get_pokemon_name_in_letter(self) -> Any | None:
        """Get pokémon with letter in name with random
        selected by specify type.

        :returns: random pokémon name"""
        pokemon = None
        if not self.type:
            return pokemon

        if len(self.poke_data['pokemon']) > 0:
            pokemon = [poke['pokemon']['name']
                       for poke in self.poke_data['pokemon']]
            contains = []
            for letter in self.letter:
                for poke_name in pokemon:
                    if letter in poke_name:
                        await self.set_contains(poke_name, contains)
            pokemon = random.choice(contains)
        return pokemon

    @staticmethod
    async def set_contains(poke_name, contains):
        """Append pokémon name in contains.

        :param poke_name: pokémon name
        :param contains: list of pokémon names
        """
        if poke_name not in contains:
            contains.append(poke_name)



