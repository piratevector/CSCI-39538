from random import choice, randint, sample
import pandas as pd
from poke_menus import Menu, MenuOption
from functools import partial

generator = pd.read_csv('~/Documents/Advanced Python/attacks.csv')

class Pokemon:

    possible_names = list(generator['name'])
    possible_poke_types = list(generator['type'])
    possible_poke_natures = list(generator['nature'])
    possible_poke_moves = list(generator['moves'])

    def __init__(self, name, type_of_pokemon, nature, moves, health):
        self.name = name
        self.type_of_pokemon = type_of_pokemon
        self.nature = nature
        self.moves = moves
        self.health = health
        self.total_health = health
    
    def get_render_info(self):
        return 'w'
    
    def get_moves(self, target_poke, detail=False):
        def get_move_function(damage):
            def f():
                target_poke.health = max(target_poke.health - damage,0)
            return f
        if detail == True:
            return [(get_move_function(damage),name + f': {damage}') for name,damage in self.moves.items()]    
        return [(get_move_function(damage),name) for name,damage in self.moves.items()]
    
    @classmethod
    def generate_random_poke(cls, *, poke_name=None, poke_type=None,\
         poke_nature=None, poke_moves=None, poke_health=None):
        if poke_name == None:
            poke_name = choice(cls.possible_names)
        if poke_type == None:
            poke_type = choice(cls.possible_poke_types) + ' Bulbasaur'
        if poke_nature == None:
            poke_nature = choice(cls.possible_poke_natures)
        if poke_moves == None:
            num_moves = randint(1,4)
            moves = sample(cls.possible_poke_moves, num_moves)
            poke_moves = {move: randint(5,120) for move in moves}
        if poke_health == None:
            poke_health = randint(10,50)*10
        
        return Pokemon(poke_name,poke_type,poke_nature,poke_moves,poke_health)


POKE = Pokemon.generate_random_poke()
#BULBA = Pokemon('Ben', 'Bulbasaur', 'green', {'tackle' : 10, 'hug': 100}, 170)
#GREG = Pokemon('Greg', 'Bulbasaur', 'green', {'tackle' : 10, 'hug': 50}, 170)

class Player:

    def __init__(self, pokemon_list=[], name='Erix', bag=[], money=0, coords = (11,15)):
        self.name = name
        self.pokemon_list = pokemon_list
        self.bag = bag
        self.money = money
        self.coords = coords
        self.curr_poke = None #pokemon_list[0]
    
    def set_starter(self, poke):
        self.pokemon_list.append(poke)
        self.curr_poke = poke
    
    def get_render_info(self):
        return 'P'

    def update_coords(self, coords):
        self.coords = coords
    
    @property
    def is_defeated(self):
        if len(self.pokemon_list) == 0:
            return False
        for poke in self.pokemon_list:
            if poke.health:
                return False
        return True
    
    def choose_poke(self,poke, close_menu):
        self.curr_poke = poke
        close_menu()
    
    def get_poke_menu(self, close_menu):
        curr_pokemons = [(partial(self.choose_poke, poke,close_menu),poke.type_of_pokemon + ' *' if poke is self.curr_poke else poke.type_of_pokemon) for poke in self.pokemon_list if poke.health]
        menu_options = map(lambda x: MenuOption(*x), curr_pokemons)
        return Menu(list(menu_options), 'Choose Poke')
    
    def get_items_menu(self, menu_stack):
        
        def item_helper(f, item_index):
            def inner():
                f(self.curr_poke)
                menu_stack.pop()
                self.bag.pop(item_index)
            return inner
    
        def map_item_to_menu_option(item, item_index):
            return MenuOption(item_helper(item.item_function,item_index), item.item_name)

        menu_options = [map_item_to_menu_option(item,item_index) for item_index,item in enumerate(self.bag)]
        #map(lambda item: MenuOption(partial(item.item_function, self.curr_poke), item.item_name), self.bag)
        menu_options.append(MenuOption(menu_stack.pop, 'Cancel'))
        return Menu(list(menu_options), 'Use Item')

class Trainer:

    def __init__(self, name, pokemon_gifted, fun_fact='', award_amount=0, pokemon_list=None):
        self.name = name
        self.pokemon_list = pokemon_list if pokemon_list else [Pokemon.generate_random_poke() for _ in range(2)]
        self.award_amount = award_amount
        self.pokemon_gifted = pokemon_gifted
        self.fun_fact = fun_fact
    
    def get_render_info(self):
        return '9'

    def get_next_poke(self):
        for poke in self.pokemon_list:
            if poke.health:
                return poke
        else: return None
    
    @classmethod
    def generate_random_trainer(cls, /, *, name=None, award_amount=None,\
         pokemon_gifted=None, fun_fact=None, pokemon_list=None):
        if name == None:
            name = choice(cls.possible_names)
        
        return Trainer(name, award_amount, pokemon_gifted, fun_fact, pokemon_list)

class Item:

    def __init__(self, item_name, item_function):
        self.item_name = item_name
        self.item_function = item_function
    
    def get_render_info(self):
        if self.item_name == 'potion':
            return '¡'
        if self.item_name == 'pokeball':
            return 'o'
        else: return '@'
    
    @classmethod
    def get_random_item(cls):
        possible_names = ['potion', 'TM', 'pokeball']
        item_choice = choice(possible_names)
        
        if item_choice == 'potion':
            def effect(poke):
                poke.health = poke.total_health
            return Item('potion', effect)

        if item_choice == 'pokeball':
            poke = Pokemon.generate_random_poke()
            return Item('pokeball', poke)

        possible_poke_moves = list(generator['moves'])
        move = choice(possible_poke_moves)
        def effect(poke):
            poke.moves.update({move : randint(5,120)})
        return Item(f'TM: {move}', effect)
    
    def use_item(self, item):
        return item.item_function
    
    # Have player get the method to show you the list of items, and item can have a method that takes the 
    # list of pokemon and gives you a menu of which pokemon to use the item on
    