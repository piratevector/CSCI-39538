from pprint import pprint
from random import choice, choices, randint
import numpy as np
from curses import wrapper, newpad, curs_set, init_pair, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import curses
from functools import partial
from poke_utils import Controller, Renderer
from poke_mapstring import map_string
from poke_map import Map
from poke_entities import Pokemon, Player
from poke_menus import Menu, MenuOption
from splash_screen import splash_screen, splash_screen_won, splash_screen_lost

def main_loop(name, terminal):

    curs_set(0)
    
    player = Player(name=name)
    game_map = Map(player, map_string)
    controller = Controller(terminal, game_map)
    renderer = Renderer(terminal, game_map)
    #renderer.render()
    
    # Splash screen
    y,x = terminal.getmaxyx()
    lines = splash_screen.split('\n')
    height = len(lines)
    width = max(*map(len,lines))
    splash_pad = newpad(height+3, width+3)
    for index,line in enumerate(lines):
        splash_pad.addstr(index,1,line)
    terminal.refresh()
    splash_pad.refresh(0,0,0,0,y-1,x-1)
    terminal.getch()

    # Starter Pokemon etc
    starter_choices = [Pokemon.generate_random_poke() for _ in range(3)]
    starter_selected=False

    def choose_starter(poke):
        player.set_starter(poke)
        game_map.curr_menus.pop()

    starter_menu = Menu([MenuOption(partial(choose_starter,poke), f'{poke.name}: {poke.type_of_pokemon}') for poke in starter_choices], 'Choose your Bulbasaur!')
    game_map.curr_menus.append(starter_menu)
    renderer.render()

    # Character movement
    while True:
        controller.handle_input()
        renderer.render()
        if (len(player.pokemon_list) >= 4) or player.is_defeated:
            break
    # Splash screen
    terminal.erase()
    y,x = terminal.getmaxyx()
    game_end_screen = splash_screen_won if player.is_defeated == False else splash_screen_lost
    lines = game_end_screen.split('\n')
    height = len(lines)
    width = max(*map(len,lines))
    splash_pad = newpad(height+3, width+3)
    for index,line in enumerate(lines):
        splash_pad.addstr(index,1,line)
    terminal.refresh()
    splash_pad.refresh(0,0,0,0,y-1,x-1)
    terminal.getch()




if __name__ == "__main__":          # "name guard"
    # poke_grid = grid()
    # poke_grid.create_grid()
    name = input('Hey! What\'s your name?\n\n')
    wrapper(partial(main_loop,name))
    wrapper()


# poke_grid = grid()
# poke_grid.create_grid()
#ray_ray = Pokemon('Ray Ray', 'Rayquaza', 'Dragon', {'fly' : 70, 'dragon burst' : 150}, '170')
#ariel = Player('Ariel', [ray_ray, 'pika'], ['potion', 'full restore'], 312341214)

# print(poke_grid.__repr__())
# print(poke_grid)