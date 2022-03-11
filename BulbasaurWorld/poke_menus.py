from pprint import pprint
from random import choice, choices, randint
import numpy as np
from curses import wrapper, newpad, curs_set, init_pair, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import curses

class MenuOption:
    def __init__(self, function, title, detail=''):
        self.function = function # Func called when menu option exercised
        self.title = title
        self.detail = detail

class Menu:
    def __init__(self, options, title):
        self.options = options # a list
        self.selected_option = 0
        self.max_width = 30
        self.box_top_left = '╔'
        self.box_top_right = '╗'
        self.box_bottom_left = '╚'
        self.box_bottom_right = '╝'
        self.box_horizontal = '═'
        self.box_vertical = '║'
        self.title = title

        # Shit for the pad
        self.pad_height = 4 + len(options) + 2
        self.pad_width = max(len(self.title), *map(lambda option: len(option.title), options)) + 4   # sick

        self.menu_pad = newpad(self.pad_height+2, self.pad_width+2)

    def get_renderable_pad(self):
        self.menu_pad.addstr(2,2,self.title)
        for i,option in enumerate(self.options):
            if self.selected_option != i:
                self.menu_pad.addstr(4+i, 2, option.title)
            else: self.menu_pad.addstr(4+i, 2, option.title, curses.color_pair(3))
        
        for i in range(self.pad_height):
            self.menu_pad.addch(i, 0, self.box_vertical)
            self.menu_pad.addch(i, self.pad_width, self.box_vertical)

        for j in range(self.pad_width):
            self.menu_pad.addch(0, j, self.box_horizontal)
            self.menu_pad.addch(self.pad_height, j, self.box_horizontal)
        
        self.menu_pad.addch(0, 0, self.box_top_left)
        self.menu_pad.addch(self.pad_height, 0, self.box_bottom_left)
        self.menu_pad.addch(0, self.pad_width, self.box_top_right)
        self.menu_pad.addch(self.pad_height, self.pad_width, self.box_bottom_right)

        return self.menu_pad
    
    def send_key(self,key):
        if key == KEY_UP:
            self.selected_option = max(0,self.selected_option-1)
        if key == KEY_DOWN:
            self.selected_option = min(len(self.options)-1,self.selected_option+1)
        if key == ord('\r') or key == ord('\n'):
            self.options[self.selected_option].function()