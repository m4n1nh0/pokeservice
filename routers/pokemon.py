"""Service router for Pokémon API."""

from fastapi import APIRouter

from services.pokeapi import Pokemon
from domain.pokemon import Pokemon as PokeRules
from utils.utils import Utils

router = APIRouter(tags=["Pokemon"], prefix="/pokemon")


@router.get("/chose_one_pokemon/{poke_name}")
async def search_pokemon_by_name(poke_name: str):
    """Search pokémon by name.
    :param poke_name: the name of the pokémon
    :return all data from selected pokémon database
    """
    poke_data = await Pokemon().get_pokemon(poke_name)
    if not poke_data:
        raise Utils.api_exception(
            message="Pokemon não encontrado com este "
                    "nome: {}".format(poke_name),
            status=404)
    return poke_data


@router.get("/chose_pokemon_type/{poke_name}")
async def get_pokemon_type_by_name(poke_name: str):
    """Get pokémon type by name.
    :param poke_name: the name of the pokémon
    :return type of pokémon name
    """
    poke_data = await Pokemon().get_pokemon(poke_name)
    if not poke_data:
        raise Utils.api_exception(
            message="Pokemon não encontrado com este "
                    "nome: {}".format(poke_name),
            status=404)
    poke_type = await PokeRules(poke_data).get_types()
    if len(poke_type) == 0:
        raise Utils.api_exception(
            message="Pokemon {} sem tipo definido!"
            .format(poke_name),
            status=401)
    return poke_type


@router.get("/chose_pokemon_by_type/{type_name}")
async def get_pokemon_by_type_name(type_name: str):
    """Get random by pokémon type by name.
    :param type_name: the name of the pokémon
    :return random pokémon by type_name
    """
    poke_api = Pokemon()
    type_data = await poke_api.get_pokemon_by_type(type_name)
    if not type_data:
        raise Utils.api_exception(
            message="Tipo de pokémon não encontrado com este "
                    "nome: {}".format(type_name),
            status=404)
    poke_name = await PokeRules(
        poke_data=type_data, poke_type=True).get_random_pokemon_types()
    if len(poke_name) == 0:
        raise Utils.api_exception(
            message="Sem pokémon para este typo {}!"
            .format(type_name),
            status=404)
    poke_data = await poke_api.get_pokemon(poke_name)
    return poke_data


@router.get("/larger_pokemon_name_by_type/{type_name}")
async def get_larger_pokemon_name_by_type(type_name: str):
    """Get larger pokémon name by type.
    :param type_name: the name of the pokémon
    :return pokémon larger name in type
    """
    poke_api = Pokemon()
    type_data = await poke_api.get_pokemon_by_type(type_name)
    if not type_data:
        raise Utils.api_exception(
            message="Tipo de pokémon não encontrado com este "
                    "nome: {}".format(type_name),
            status=404)
    poke_name = await PokeRules(
        poke_data=type_data, poke_type=True).get_larger_pokemon_name()
    if len(poke_name) == 0:
        raise Utils.api_exception(
            message="Sem pokémon para este typo {}!"
            .format(type_name),
            status=404)
    poke_data = await poke_api.get_pokemon(poke_name)
    return poke_data
