from curses import wrapper, newpad, curs_set, init_pair, KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT
import curses
from poke_menus import Menu, MenuOption
from random import randint, choice
from poke_entities import Pokemon, Trainer

def confirm():
    pass

class BattleScreen:
    def __init__(self, player, opponent, player_pokemon, opponent_pokemon):
        self.player = player
        self.opponent = opponent
        self.player_pokemon = player_pokemon
        self.opponent_pokemon = opponent_pokemon
        self.pad_width = 40
        self.pad_height = 10
        self.battle_status_pad = newpad(self.pad_height+2,self.pad_width+2)
        self.box_top_left = '╔'
        self.box_top_right = '╗'
        self.box_bottom_left = '╚'
        self.box_bottom_right = '╝'
        self.box_horizontal = '═'
        self.box_vertical = '║'
    
    def erase(self):
        self.battle_status_pad.erase()
        self.battle_status_pad.refresh(0,0,0,0,0,0)

    def get_renderable_pad(self):
        
        self.battle_status_pad.erase()
        for i in range(self.pad_height):
            self.battle_status_pad.addch(i, 0, self.box_vertical)
            self.battle_status_pad.addch(i, self.pad_width, self.box_vertical)

        for j in range(self.pad_width):
            self.battle_status_pad.addch(0, j, self.box_horizontal)
            self.battle_status_pad.addch(self.pad_height, j, self.box_horizontal)
        
        self.battle_status_pad.addch(0, 0, self.box_top_left)
        self.battle_status_pad.addch(self.pad_height, 0, self.box_bottom_left)
        self.battle_status_pad.addch(0, self.pad_width, self.box_top_right)
        self.battle_status_pad.addch(self.pad_height, self.pad_width, self.box_bottom_right)

        min_len = min(self.pad_width-len('trainer: ' + self.opponent.name)-1, self.pad_width-len('type: ' + self.opponent_pokemon.type_of_pokemon)-1)
        self.battle_status_pad.addstr(1, min_len, 'trainer: ' + self.opponent.name)
        self.battle_status_pad.addstr(2, min_len, 'poke: ' + self.opponent_pokemon.name)
        self.battle_status_pad.addstr(3, min_len, 'type: ' + self.opponent_pokemon.type_of_pokemon)
        self.battle_status_pad.addstr(4, min_len, 'health: ' + f'{self.opponent_pokemon.health}/{self.opponent_pokemon.total_health}')
        
        self.battle_status_pad.addstr(self.pad_height-4, 1, 'player: ' + self.player.name)
        self.battle_status_pad.addstr(self.pad_height-3, 1, 'poke: ' + self.player_pokemon.name)
        self.battle_status_pad.addstr(self.pad_height-2, 1, 'type: ' + self.player_pokemon.type_of_pokemon)
        self.battle_status_pad.addstr(self.pad_height-1, 1, 'health: ' + f'{self.player_pokemon.health}/{self.player_pokemon.total_health}')

        return self.battle_status_pad

class Battle:
    def __init__(self, player, game_map, opponent):
        if type(opponent) == Pokemon:
            opponent = Trainer(name='Wild Bulbasaur', pokemon_gifted=opponent, pokemon_list = [opponent], fun_fact = 'GRR')
        self.menu_stack = game_map.curr_menus
        self.player = player
        self.opponent = opponent
        self.curr_player_poke = player.curr_poke
        self.curr_opponent_poke = opponent.get_next_poke() #pokemon_list[0]
        self.menu_stack.append(
            Menu([MenuOption(self.choose_attack, 'Fight'),
            MenuOption(self.choose_item, 'Item'),
            MenuOption(self.choose_player_poke, 'Pokemon'),
            MenuOption(self.choose_flee, 'Flee')],
            'Battle'))
        self.game_map = game_map
        game_map.battle_screen = BattleScreen(self.player, self.opponent, self.curr_player_poke, self.curr_opponent_poke)

    def choose_attack(self):
        self.menu_stack.append(
            Menu(list(map(lambda move: MenuOption(self.process_turn_factory(move[0]), move[1]), self.curr_player_poke.get_moves(self.curr_opponent_poke, detail=True))), self.curr_player_poke.name)
        )

    def choose_item(self):
        self.menu_stack.append(
            self.player.get_items_menu(self.menu_stack)
        )

    def choose_player_poke(self):
        def cleanup():
            self.menu_stack.pop()
            self.curr_player_poke = self.player.curr_poke
            self.game_map.battle_screen = BattleScreen(self.player, self.opponent, self.curr_player_poke, self.curr_opponent_poke)
        self.menu_stack.append(self.player.get_poke_menu(cleanup))

    def choose_flee(self):
        self.end_battle(outcome='fled')
    
    def end_battle(self, outcome):
        self.game_map.battle_screen.erase()
        while self.menu_stack:
            self.menu_stack.pop()
        def end_battle_callback():
            if outcome == 'lost':
                # self.game_map.is_lost == True
                return
            self.game_map.battle_screen = None
            self.menu_stack.pop()
            if outcome == 'fled':
                return
            if outcome == 'won':
                y,x = self.player.coords
                self.game_map.actual_grid[y][x].remove_entity(self.opponent)
                self.player.money += self.opponent.award_amount
                if self.opponent.pokemon_gifted:
                    self.opponent.pokemon_gifted.health = self.opponent.pokemon_gifted.total_health
                    self.player.pokemon_list.append(self.opponent.pokemon_gifted)
                self.menu_stack.append(Menu([MenuOption(self.menu_stack.pop, 'okay')], f'Fun fact! {self.opponent.fun_fact}'))
        self.menu_stack.append(Menu([MenuOption(end_battle_callback, 'okay')], f'Player {outcome}!'))
    
    def process_turn_factory(self, player_move_function):
        opp_move_function, move_name = choice(list(self.curr_opponent_poke.get_moves(self.curr_player_poke)))

        def process_turn():
            player_move_function()
            if self.curr_opponent_poke.health:
                opp_move_function()
            #self.curr_player_poke.health = max(self.curr_player_poke.health - move_damage, 0)
            self.menu_stack.append(Menu([MenuOption(self.resolve_turn, 'okay')], f'{self.curr_opponent_poke.name} used {move_name}'))
            #self.resolve_turn()
        return process_turn
    
    def resolve_turn(self):
        if not self.curr_opponent_poke.health:
            self.curr_opponent_poke = self.opponent.get_next_poke()
            if not self.curr_opponent_poke:
                return self.end_battle(outcome = 'won')
            self.game_map.battle_screen = BattleScreen(self.player, self.opponent, self.curr_player_poke, self.curr_opponent_poke)
        if not self.curr_player_poke.health:
            if self.player.is_defeated:
                return self.end_battle(outcome = 'lost')
            self.choose_player_poke()
            return
            #self.game_map.battle_screen = BattleScreen(self.player, self.opponent, self.curr_player_poke, self.curr_opponent_poke)
        while len(self.menu_stack) > 1:
            self.menu_stack.pop()
             