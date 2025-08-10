from colorama import just_fix_windows_console
from termcolor import colored
from random import randrange
from enum import Enum

just_fix_windows_console()

class Mode(Enum):
    RENATE_VS_YOU = 0
    YOU_VS_RANDOM = 1
    RANDOM_VS_YOU = 2
    YOU_VS_FRIEND = 3

mode_names = {
    Mode.RENATE_VS_YOU: "Renate vs. You",
    Mode.YOU_VS_RANDOM: "You vs. Random",
    Mode.RANDOM_VS_YOU: "Random vs. You",
    Mode.YOU_VS_FRIEND: "You vs. Your Friend"
}

dim_min = 3
width_max = 25
height_max = 25

h_ruler_dist = 5
v_ruler_dist = 5
v_ruler_width = 3

space_lines = 50

menu_title_color = "magenta"
game_title_color = "cyan"
first_player_color = "green"
second_player_color = "blue"
first_player_old_color = "light_green"
second_player_old_color = "light_blue"
information_color = "yellow"
error_color = "red"
uncolored_cell_color = "white"

def space() -> None:
    for _ in range(space_lines):
        print()

def show_error(err : str) -> None:
    print(colored(f"{err} (press ENTER to continue and try again)", error_color))
    input()

def select_mode() -> Mode:
    while True:
        space()
        print(colored("~Which mode do you want to play in?~", menu_title_color))
        modes = [mode for mode in Mode]
        for i in range(len(modes)):
            print(colored(f"{i + 1})", information_color), mode_names[modes[i]])
        answer_str = input(colored("=> ", menu_title_color))
        try:
            answer = int(answer_str) - 1
            if 0 <= answer and answer < len(modes):
                return modes[answer]
        except:
            pass
        show_error("invalid mode")

def select_dim() -> (int, int):
    while True:
        space()
        print(colored("~Which size do you want the rectangle frame to be?~", menu_title_color))
        print(colored("(The expected format is \"<width> <height>\")", information_color))
        print(colored("(Both dimensions should be positive integers with " +
            f"{dim_min}<=width<={width_max} and {dim_min}<=height<={height_max})", information_color))
        answer_str = input(colored("=> ", menu_title_color))
        try:
            lst = answer_str.split(" ")
            if len(lst) != 2:
                raise Exception()
            width = int(lst[0])
            height = int(lst[1])
            if dim_min <= width and width <= width_max and dim_min <= height and height <= height_max:
                return (width, height)
        except:
            pass
        show_error("invalid dimensions")

class Player(Enum):
    FIRST = 1
    SECOND = 2

class GameState:
    mode : Mode
    width : int
    height : int
    cells : list[list[int]]
    # cells[y][x] = -1 for cell not on frame, 0 for uncolored cell on frame, 1 for cell colored by first player, 2 for cell colored by second player
    active_player : Player
    round : int
    newly_colored_cells : list[(int, int)]
    colored_cells_count : int

    def __init__(self, mode : Mode, width : int, height : int):
        self.mode = mode
        self.width = width
        self.height = height
        self.cells = [[-1 for _ in range(width)] for _ in range(height)]
        for x in range(width):
            self.cells[0][x] = 0
            self.cells[height - 1][x] = 0
        for y in range(height):
            self.cells[y][0] = 0
            self.cells[y][width - 1] = 0
        self.active_player = Player.FIRST
        self.round = 0
        self.newly_colored_cells = []
        self.colored_cells_count = 0

    def get(self, x : int, y : int) -> int:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return -1
        return self.cells[y][x]

    def colorize(self, x : int, y : int, color : int) -> None:
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return
        if self.cells[y][x] > 0:
            return
        self.cells[y][x] = color
        self.newly_colored_cells.append((x, y))
        self.colored_cells_count += 1

    def reset_newly_colored_cells(self) -> list[int]:
        temp = self.newly_colored_cells
        self.newly_colored_cells = []
        return temp

    def next_round(self) -> None:
        match self.active_player:
            case Player.FIRST:
                self.active_player = Player.SECOND
            case Player.SECOND:
                self.active_player = Player.FIRST
        self.round += 1

    def total_cell_count(self) -> int:
        return self.width * self.height - (self.width - 2) * (self.height - 2)

def cell(x : int, y : int, state : GameState) -> str:
    match state.get(x, y):
        case -1:
            return " "
        case 0:
            color = uncolored_cell_color
        case 1:
            color = first_player_color if (x, y) in state.newly_colored_cells else first_player_old_color
        case 2:
            color = second_player_color if (x, y) in state.newly_colored_cells else second_player_old_color
    return colored("■", color)

def v_ruler(line : str, i : int) -> str:
    pre = f"{i + 1}-" if i % v_ruler_dist == 0 else ""
    while len(pre) < v_ruler_width:
        pre = " " + pre
    suf = f"-{i + 1}" if i % v_ruler_dist == 0 else ""
    return f"{pre}{line}{suf}"

def print_state(state : GameState) -> None:
    space()
    print(colored("RenateErhardGame by Lexinon", game_title_color), colored(f"(mode \"{mode_names[state.mode]}\")", menu_title_color))
    h_ruler_str = ""
    while len(h_ruler_str) < state.width * 2:
        h_ruler_str += f"|{int(len(h_ruler_str) / 2 + 1)}" if len(h_ruler_str) % h_ruler_dist == 0 else " "
        if len(h_ruler_str) % 2 == 1:
            h_ruler_str += " "
    h_ruler_str = " " * v_ruler_width + h_ruler_str
    print(h_ruler_str)
    for y in range(state.height):
        h_str = ""
        for x in range(state.width):
            h_str += f"{cell(x, y, state)}{" " if x < state.width - 1 else ""}"
        print(v_ruler(h_str, y))
    print(h_ruler_str)

def finished(state : GameState) -> bool:
    for x in range(state.width):
        if state.get(x, 0) == 0 or state.get(x, state.height - 1) == 0:
            return False
    for y in range(1, state.height - 1):
        if state.get(0, y) == 0 or state.get(state.width - 1, y) == 0:
            return False
    return True

def call_player(state : GameState) -> None:
    match state.mode:
        case Mode.RENATE_VS_YOU:
            if state.round == 1:
                if state.width == state.height:
                    last_player_info = "Why did Renate only color one cell in the corner?"
                    next_player_call = "Let's find out by making your first move!"
                else:
                    last_player_info = f"Renate captured a line of {len(state.newly_colored_cells)} cells!"
                    next_player_call = "To see why this is smart, make your first move!"
            elif 2 * state.colored_cells_count <= state.total_cell_count():
                last_player_info = f"Renate colored {len(state.newly_colored_cells)} cell(s)."
                next_player_call = "Now it's your turn again!"
            else:
                last_player_info = f"Exactly {len(state.newly_colored_cells)} more cell(s) green."
                next_player_call = "Continue, if you think you have a chance!"
        case Mode.YOU_VS_RANDOM:
            if state.round == 0:
                last_player_info = ""
                next_player_call = "You make the first move!"
            else:
                last_player_info = f"Random colored {len(state.newly_colored_cells)} cell(s)."
                next_player_call = "Now it's your turn again!"
        case Mode.RANDOM_VS_YOU:
            if state.round == 1:
                last_player_info = f"Random got started by coloring {len(state.newly_colored_cells)} cell(s)."
                next_player_call = "What is your first move?"
            else:
                last_player_info = f"Random colored {len(state.newly_colored_cells)} cell(s)."
                next_player_call = "Now it's your turn again!"
        case Mode.YOU_VS_FRIEND:
            if state.round == 0:
                last_player_info = ""
                next_player_call = "It's the first players turn!"
            else:
                last_player_info = f"The {"first" if state.active_player == Player.SECOND else "second"} player colored {len(state.newly_colored_cells)} cell(s)."
                next_player_call = f"Now it's the {"first" if state.active_player == Player.FIRST else "second"} player's turn!"
    print(colored(last_player_info, first_player_color if state.active_player == Player.SECOND else second_player_color),
        colored(next_player_call, first_player_color if state.active_player == Player.FIRST else second_player_color))

def read_move(state : GameState) -> str:
    call_player(state)
    print(colored("(The expected format is \"<x1> <y1> <x2> <y2>\")", information_color))
    answer_str = input(colored("=> ", menu_title_color))
    try:
        lst = answer_str.split(" ")
        if len(lst) != 4:
            return "malformed input"
        x1 = int(lst[0]) - 1
        y1 = int(lst[1]) - 1
        x2 = int(lst[2]) - 1
        y2 = int(lst[3]) - 1
        if x1 > x2:
            temp = x1
            x1 = x2
            x2 = temp
        if y1 > y2:
            temp = y1
            y1 = y2
            y2 = temp
        if x1 < 0 or y1 < 0 or x2 >= state.width or y2 >= state.height:
            return "area not in rectangle frame"
        coherence_check = (state.round == 0)
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                if x > 0 and y > 0 and x < state.width - 1 and y < state.height - 1:
                    return "area not in rectangle frame"
                if state.get(x - 1, y) > 0 or state.get(x + 1, y) > 0 or state.get(x, y - 1) > 0 or state.get(x, y + 1) > 0:
                    coherence_check = True
                if state.get(x, y) > 0:
                    return "area already colored"
        if not coherence_check:
            return "uncolored area not coherent"
        state.newly_colored_cells = []
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                state.colorize(x, y, state.active_player.value)
    except:
        return "malformed input"
    return None

def print_result(state : GameState) -> None:
    print_state(state)
    match state.mode:
        case Mode.RENATE_VS_YOU:
            print(colored("Sorry, but Renate wins (once again)!", first_player_color))
        case Mode.YOU_VS_RANDOM:
            if state.active_player == Player.SECOND:
                print(colored("You win!", first_player_color))
            else:
                print(colored("Random wins!", second_player_color))
        case Mode.RANDOM_VS_YOU:
            if state.active_player == Player.SECOND:
                print(colored("Random wins!", first_player_color))
            else:
                print(colored("You win!", second_player_color))
        case Mode.YOU_VS_FRIEND:
            if state.active_player == Player.SECOND:
                print(colored("The first friend wins!", first_player_color))
            else:
                print(colored("The second friend wins!", second_player_color))

def renates_turn_width_eq_height(state : GameState) -> None:
    if state.round == 0:
        state.colorize(0, 0, 1)
    else:
        old_newly_colored_cells = state.reset_newly_colored_cells()
        if state.get(state.width - 2, state.height - 1) > 0:
            for y in range(state.height):
                state.colorize(state.width - 1, y, 1)
        elif state.get(state.width - 1, state.height - 2) > 0:
            for x in range(state.width):
                state.colorize(x, state.height - 1, 1)
        else:
            for (x, y) in old_newly_colored_cells:
                state.colorize(y, x, 1)

def renates_turn_width_gt_height(state : GameState) -> None:
    old_newly_colored_cells = state.reset_newly_colored_cells()
    if state.round == 0:
        for x in range(state.width):
            state.colorize(x, 0, 1)
    else:
        leftSideComplete = state.get(0, state.height - 2) > 0
        rightSideComplete = state.get(state.width - 1, state.height - 2) > 0
        if rightSideComplete:
            if leftSideComplete:
                for x in range(state.width):
                    state.colorize(x, state.height - 1, 1)
            elif state.get(1, state.height - 1) > 0:
                for y in range(state.height):
                    state.colorize(0, y, 1)
            else:
                i = state.width - 1
                while i >= state.height or state.get(i, state.height - 1) > 0 or state.get(0, state.height - 1 - i) > 0:
                    state.colorize(i, state.height - 1, 1)
                    state.colorize(0, state.height - 1 - i, 1)
                    i -= 1
        else:
            if state.get(state.width - 2, state.height - 1) > 0:
                for y in range(state.height):
                    state.colorize(state.width - 1, y, 1)
            elif leftSideComplete:
                i = state.width - 1
                while i >= state.height or state.get(state.width - 1 - i, state.height - 1) > 0 or state.get(state.width - 1, state.height - 1 - i) > 0:
                    state.colorize(state.width - 1 - i, state.height - 1, 1)
                    state.colorize(state.width - 1, state.height - 1 - i, 1)
                    i -= 1
            else:
                for (x, y) in old_newly_colored_cells:
                    state.colorize(state.width - 1 - x, y, 1)

def renates_turn_width_lt_height(state : GameState) -> None:
    old_newly_colored_cells = state.reset_newly_colored_cells()
    if state.round == 0:
        for y in range(state.height):
            state.colorize(0, y, 1)
    else:
        topComplete = state.get(state.width - 2, 0) > 0
        bottomComplete = state.get(state.width - 2, state.height - 1) > 0
        if bottomComplete:
            if topComplete:
                for y in range(state.height):
                    state.colorize(state.width - 1, y, 1)
            elif state.get(state.width - 1, 1) > 0:
                for x in range(state.width):
                    state.colorize(x, 0, 1)
            else:
                i = state.height - 1
                while i >= state.width or state.get(state.width - 1, i) > 0 or state.get(state.width - 1 - i, 0) > 0:
                    state.colorize(state.width - 1, i, 1)
                    state.colorize(state.width - 1 - i, 0, 1)
                    i -= 1
        else:
            if state.get(state.width - 1, state.height - 1) > 0:
                for x in range(state.width):
                    state.colorize(x, state.height - 1, 1)
            elif topComplete:
                i = state.height - 1
                while i >= state.width or state.get(state.width - 1, state.height - 1 - i) > 0 or state.get(state.width - 1 - i, state.height - 1) > 0:
                    state.colorize(state.width - 1, state.height - 1 - i, 1)
                    state.colorize(state.width - 1 - i, state.height - 1, 1)
                    i -= 1
            else:
                for (x, y) in old_newly_colored_cells:
                    state.colorize(x, state.height - 1 - y, 1)

def renates_turn(state : GameState) -> None:
    if state.width == state.height:
        renates_turn_width_eq_height(state)
    elif state.width > state.height:
        renates_turn_width_gt_height(state)
    else:
        renates_turn_width_lt_height(state)

# This will select a random cell on the rectangle frame and a random direction (clockwise/counterclockwise). In the first round, it will directly
# start coloring (a random amount of) cells in the chosen direction. Otherwise, it will search for the "end" of the colored area (in the chosen
# direction) and from there start coloring cells.
def randoms_turn(state : GameState) -> None:
    state.reset_newly_colored_cells()
    match randrange(2):
        case 0:
            x1 = randrange(state.width)
            y1 = 0 if randrange(2) == 0 else state.height - 1
        case 1:
            x1 = 0 if randrange(2) == 0 else state.width - 1
            y1 = randrange(state.height)
    clockwise = randrange(2) == 0
    if state.round != 0:
        keepSearching = True
        while keepSearching:
            if clockwise:
                if y1 == 0 and x1 < state.width - 1:
                    x2 = x1 + 1
                    y2 = y1
                elif x1 == state.width - 1 and y1 < state.height - 1:
                    x2 = x1
                    y2 = y1 + 1
                elif y1 == state.height - 1 and x1 > 0:
                    x2 = x1 - 1
                    y2 = y1
                else:
                    x2 = x1
                    y2 = y1 - 1
            else:
                if y1 == 0 and x1 > 0:
                    x2 = x1 - 1
                    y2 = y1
                elif x1 == 0 and y1 < state.height - 1:
                    x2 = x1
                    y2 = y1 + 1
                elif y1 == state.height - 1 and x1 < state.width - 1:
                    x2 = x1 + 1
                    y2 = y1
                else:
                    x2 = x1
                    y2 = y1 - 1
            if state.get(x1, y1) > 0 and state.get(x2, y2) == 0:
                keepSearching = False
            x1 = x2
            y1 = y2
    if clockwise:
        if y1 == 0 and x1 < state.width - 1:
            x2 = randrange(x1, state.width)
            y2 = y1
        elif x1 == state.width - 1 and y1 < state.height - 1:
            x2 = x1
            y2 = randrange(y1, state.height)
        elif y1 == state.height - 1 and x1 > 0:
            x2 = randrange(0, x1 + 1)
            y2 = y1
        else:
            x2 = x1
            y2 = randrange(0, y1 + 1)
    else:
        if y1 == 0 and x1 > 0:
            x2 = randrange(0, x1 + 1)
            y2 = y1
        elif x1 == 0 and y1 < state.height - 1:
            x2 = x1
            y2 = randrange(y1, state.height)
        elif y1 == state.height - 1 and x1 < state.width - 1:
            x2 = randrange(x1, state.width)
            y2 = y1
        else:
            x2 = x1
            y2 = randrange(0, y1 + 1)
    if x1 > x2:
        temp = x1
        x1 = x2
        x2 = temp
    if y1 > y2:
        temp = y1
        y1 = y2
        y2 = temp
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            state.colorize(x, y, state.active_player.value)

def game_loop() -> None:
    mode = select_mode()
    dim = select_dim()
    state = GameState(mode, dim[0], dim[1])
    while not finished(state):
        match state.mode:
            case Mode.RENATE_VS_YOU:
                if state.active_player == Player.FIRST:
                    renates_turn(state)
                    state.next_round()
                    continue
            case Mode.YOU_VS_RANDOM:
                if state.active_player == Player.SECOND:
                    randoms_turn(state)
                    state.next_round()
                    continue
            case Mode.RANDOM_VS_YOU:
                if state.active_player == Player.FIRST:
                    randoms_turn(state)
                    state.next_round()
                    continue
        print_state(state)
        err = read_move(state)
        if err != None:
            show_error(err)
        else:
            state.next_round()
    print_result(state)

game_loop()
