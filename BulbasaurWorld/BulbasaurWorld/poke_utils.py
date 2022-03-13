from pprint import pprint
from random import choice, choices, randint
import numpy as np
from curses import wrapper, newpad, curs_set, init_pair, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import curses

class Controller:

    def __init__(self, terminal, game_map):
        self.terminal = terminal
        self.game_map = game_map
    
    def handle_input(self):
        k = self.terminal.getch()

        if self.game_map.curr_menus:
            self.game_map.curr_menus[-1].send_key(k)
            return
        
        if k == ord('m'):
            self.game_map.open_main_menu()
            return

        if k == KEY_UP:
            self.game_map.move_player((-1,0))
        if k == KEY_DOWN:
            self.game_map.move_player((1,0))
        if k == KEY_LEFT:
            self.game_map.move_player((0,-1))
        if k == KEY_RIGHT:
            self.game_map.move_player((0,1))



class Renderer:

    def __init__(self, terminal, game_map):
        self.terminal = terminal
        self.game_map = game_map
        self.terminal_dimensions = terminal.getmaxyx()
        self.map_pad = newpad(game_map.grid_dimensions[0]+1, game_map.grid_dimensions[1]+1)
        
        init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Water
        init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN) # Tree
        init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # Cliff
        init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK) # Tall grass
        init_pair(5, curses.COLOR_YELLOW, curses.COLOR_YELLOW) # Path   
        
        self.color_map = {
            'W' : curses.color_pair(1), # water
            'T' : curses.color_pair(2), # tree
            'C' : curses.color_pair(3), # cliff
            'w' : curses.color_pair(4), # tall grass
            'p' : curses.color_pair(5), # path
        }
    
    def render(self):
        self.map_pad.erase()
        for i,row in enumerate(self.game_map.get_render_info()):
            for j,char in enumerate(row):
                if char in self.color_map:
                    self.map_pad.addch(i,j,char, self.color_map[char])
                else: self.map_pad.addch(i,j,char)
        
        # These numbers are:
        # 1,2: The top left corner on the map to start showing from
        # 3,4: The top left corner of the terminal to start painting the pad on
        # 5,6: The bottom right corner of the terminal to paint the pad on

        player_loc = self.game_map.player.coords
        terminal_top_left = (0,0)
        terminal_bottom_right = self.terminal_dimensions[0]-2, self.terminal_dimensions[1]-2
        
        # Get half the window to center the player
        height = self.terminal_dimensions[0]//2
        width = self.terminal_dimensions[1]//2
        max_y = self.game_map.grid_dimensions[0]-self.terminal_dimensions[0]
        max_x = self.game_map.grid_dimensions[1]-self.terminal_dimensions[1]

        game_map_top_left = [player_loc[0] - height, player_loc[1] - width]
        
        game_map_top_left[0] = max(game_map_top_left[0], 0)
        game_map_top_left[0] = min(game_map_top_left[0], max_y)
        game_map_top_left[1] = max(game_map_top_left[1], 0)
        game_map_top_left[1] = min(game_map_top_left[1], max_x)

        self.map_pad.refresh(*game_map_top_left, *terminal_top_left, *terminal_bottom_right)

        for menu in self.game_map.curr_menus:
            menu_pad = menu.get_renderable_pad()
            menu_pad.refresh(0,0,*terminal_top_left,*terminal_bottom_right)
        
        if self.game_map.battle_screen:
            battle_screen_pad = self.game_map.battle_screen.get_renderable_pad()
            battle_screen_pad.refresh(0, 0, height, width, self.terminal_dimensions[0]-2, self.terminal_dimensions[1]-2)