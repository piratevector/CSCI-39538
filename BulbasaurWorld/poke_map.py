from pprint import pprint
from random import choice, choices, randint
import numpy as np
from curses import wrapper, newpad, curs_set, init_pair, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import curses
from poke_menus import Menu, MenuOption
from poke_battle import BattleScreen, Battle
from poke_entities import Player, Trainer, Pokemon, Item

class Tile:
    def __init__(self, environment, coords):   #passable=True):

        self.impassable = {
            'W', # water
            'T', # tree
            'C' # cliff
            }

        self.passable = environment not in self.impassable
        self.environment = environment
        self.entities = []
        self.coords = coords

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        self.entities = [e for e in self.entities if not e is entity]
    
    def get_render_info(self):
        if self.entities:
            return self.entities[-1].get_render_info() # Return render info for most important entity
        return self.environment

class Map:
    def __init__(self, player, map_string):                # grid_dimensions=[8,8]):
        self.player = player
        self.grid_dimensions = None
        self.actual_grid = None                            #self.create_grid()
        self.curr_menus = []
        self.create_grid(map_string)
        self.set_player_location()
        self.battle_screen = None
    
    # Menu you get when you pause
    def open_main_menu(self): 
        menu = Menu([MenuOption(self.open_bag_menu, 'Inventory'), MenuOption(self.open_poke_menu, 'Bulbasaurs'), MenuOption(self.close_menu, 'Back')], 'Main Menu')
        self.curr_menus.append(menu)

    def open_bag_menu(self):
        menu = self.player.get_items_menu(self.curr_menus)
        self.curr_menus.append(menu)

    def open_poke_menu(self):
        self.curr_menus.append(self.player.get_poke_menu(self.curr_menus.pop))

    def close_menu(self):
        self.curr_menus.pop()
    
    def set_player_location(self):
        coords = self.player.coords
        self.actual_grid[coords[0]][coords[1]].add_entity(self.player)
        for entity in self.actual_grid[coords[0]][coords[1]].entities:
            if entity.__class__ == Trainer or entity.__class__ == Pokemon:
                Battle(self.player, self, entity)
            if entity.__class__ == Item:
                self.player.bag.append(entity)
                self.actual_grid[coords[0]][coords[1]].remove_entity(entity)
    
    def move_player(self, direction): 
        # TO DO
        next_coords = (self.player.coords[0] + direction[0], self.player.coords[1] + direction[1])
        if self.check_passable(next_coords):
            self.remove_player(self.player.coords)
            self.player.update_coords(next_coords) # updating data value of where the player thinks they are
            self.set_player_location() # updates the map
    
    def check_passable(self, coords):
        if coords[0] < 0 or coords[0] > self.grid_dimensions[0]-1:
            return False
        if coords[1] < 0 or coords[1] > self.grid_dimensions[1]-1:
            return False
        return self.actual_grid[coords[0]][coords[1]].passable
    
    def remove_player(self, coords):
        self.actual_grid[coords[0]][coords[1]].remove_entity(self.player)

    def __str__(self):
        return '\n'.join(map(str,self.actual_grid))
    
    def __repr__(self):
        return f'grid: {self.actual_grid}, dimensions: {self.grid_dimensions}'
    
    def get_render_info(self):
        return map(lambda row: map(lambda tile: tile.get_render_info(), row), self.actual_grid)

    def create_grid(self, map_string):
        initial_grid = []

        # Determine terrain
        # seeds = []
        # for i in range(3):
        #     x = randint(0,7)
        #     y = randint(0,7)
        #     seeds.append([x,y])
        # terrains = ['water','land']
        # initial_terrain = choice(terrains)

        # for row in range(self.grid_dimensions[0]):
        #     initial_grid.append([])
        #     for column in range(self.grid_dimensions[1]):
        #         initial_grid[-1].append(Tile(' ', (row,column)))

        trainerAdded = False
        map_rows = map_string.split('\n')
        for i,row in enumerate(map_rows):
            temp_row = []
            for j,char in enumerate(row):
                temp_row.append(Tile(char, (i,j)))
                if char == ' ' and randint(0,10) == 0 and not trainerAdded: 
                    temp_row[-1].add_entity(Trainer('Bill DeBlasio', 10000000, None, 'i like cocks'))
                    trainerAdded = True
                if char == 'w' and randint(0,10) == 0:
                    temp_row[-1].add_entity(Pokemon.generate_random_poke())
                if char == ' ' and (not temp_row[-1].entities) and randint(0,200) == 0:
                    temp_row[-1].add_entity(Item.get_random_item())
            initial_grid.append(temp_row)
        self.actual_grid = initial_grid
        self.grid_dimensions = (len(initial_grid),len(initial_grid[0]))


        # for i,j in initial_grid:
        #     if [i,j] in seeds:


        return initial_grid