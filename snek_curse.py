import curses as cs
import time
import threading
import copy
import random

# Direction const
D_RIGHT = 1
D_LEFT = 2
D_TOP = 3
D_DOWN = 4
# Draw const
DRAW_BG = 1
DRAW_WALLS = 2
DRAW_SNAKE = 3
DRAW_CHERRY = 4
BORDER_WIDTH = 70
BORDER_HEIGHT = 30
# Globals
direction = D_LEFT
game_over = False


class Cell:
    def __init__(self, x, y, c):
        self.x = x
        self.y = y
        self.repr = c

    def __eq__(self, other):
        if isinstance(other, Cell):
            return self.x == other.x and self.y == other.y
        else:
            return NotImplemented

    def __ne__(self, other):
        res = self.__eq__(other)
        if res == NotImplemented:
            return res
        else:
            return not res


class Player:
    def __init__(self):
        self.dir = D_LEFT
        self.cells = [Cell(40, 13, '@'), Cell(41, 13, '*'), Cell(42, 13, '*')]
        self.head = self.cells[0]
        self.score = 0


class Cherry:
    def __init__(self):
        self.pos = Cell(random.randint(1, BORDER_WIDTH),
                        random.randint(1, BORDER_HEIGHT), '$')


def game_loop(player, cherry, scr):
    global game_over
    # Player movement
    player.dir = direction
    dst_cell = copy.deepcopy(player.head)
    dst_cell.repr = '*'                     # Restore non-head repr
    if player.dir == D_RIGHT:
        player.head.x = player.head.x + 1
    elif player.dir == D_LEFT:
        player.head.x = player.head.x - 1
    elif player.dir == D_TOP:
        player.head.y = player.head.y - 1
    elif player.dir == D_DOWN:
        player.head.y = player.head.y + 1
    for n in range(1, len(player.cells)):
        src_cell = copy.deepcopy(player.cells[n])
        player.cells[n] = dst_cell
        dst_cell = copy.deepcopy(src_cell)
    # Player eats cherry, gets new cherry, adds new block to player's tail
    if player.head.x == cherry.pos.x and player.head.y == cherry.pos.y:
        cherry.pos.x = random.randint(1, BORDER_WIDTH - 4)
        cherry.pos.y = random.randint(1, BORDER_HEIGHT - 5)
        player.cells.append(dst_cell)
        player.score = player.score + 10
    # Game over checks
    for n in range(1, len(player.cells)):
        if player.head == player.cells[n]:
            game_over = True
    if player.head.x < 1 or player.head.x > BORDER_WIDTH - 2:
        game_over = True
    elif player.head.y < 1 or player.head.y > BORDER_HEIGHT - 1:
        game_over = True
    # Draw everything
    draw(scr, player, cherry)
    return


def get_input(scr):
    global direction
    global game_over
    new_dir = direction
    while True:
        c = chr(scr.getch())
        if c == 'w' and direction != D_DOWN:
            new_dir = D_TOP
        elif c == 's' and direction != D_TOP:
            new_dir = D_DOWN
        elif c == 'd' and direction != D_LEFT:
            new_dir = D_RIGHT
        elif c == 'a' and direction != D_RIGHT:
            new_dir = D_LEFT
        elif c == 'q':
            game_over = True
        direction = new_dir
    return


def draw(scr, player, cherry):
    scr.clear()
    # Upper border
    scr.addstr('#'*BORDER_WIDTH+'\n', cs.color_pair(DRAW_WALLS))
    # Side borders
    for i in range(1, BORDER_HEIGHT):
        scr.addstr('#', cs.color_pair(DRAW_WALLS))
        scr.addstr(' '*(BORDER_WIDTH-2), cs.color_pair(DRAW_BG))
        scr.addstr('#\n', cs.color_pair(DRAW_WALLS))
    # Lower border
    scr.addstr('#'*BORDER_WIDTH+'\n', cs.color_pair(DRAW_WALLS))
    # Player draw
    for i in range(0, len(player.cells)):
        c = player.cells[i]
        if 0 < c.x < BORDER_WIDTH - 1\
                and 0 < c.y < BORDER_HEIGHT:
            scr.addch(c.y, c.x, c.repr, cs.color_pair(DRAW_SNAKE))
    # Cherry draw
    scr.addch(cherry.pos.y, cherry.pos.x,
              cherry.pos.repr, cs.color_pair(DRAW_CHERRY))
    # Score string
    scr.addstr(BORDER_HEIGHT + 1, 0,
               'Your score: {}\n'.format(player.score), cs.color_pair(0))
    scr.refresh()
    return


def main():
    # Screen initializing
    scr = cs.initscr()
    cs.cbreak()
    cs.noecho()
    cs.start_color()
    cs.init_pair(DRAW_BG, cs.COLOR_WHITE, cs.COLOR_WHITE)
    cs.init_pair(DRAW_WALLS, cs.COLOR_RED, cs.COLOR_RED)
    cs.init_pair(DRAW_SNAKE, cs.COLOR_CYAN, cs.COLOR_WHITE)
    cs.init_pair(DRAW_CHERRY, cs.COLOR_GREEN, cs.COLOR_WHITE)
    # Game initializing
    player = Player()
    cherry = Cherry()
    input_thread = threading.Thread(target=get_input, daemon=True, args=(scr, ))
    input_thread.start()
    # Game loop starts here
    while not game_over:
        game_thread = threading.Thread(target=game_loop,
                                       args=(player, cherry, scr, ))
        game_thread.start()
        time.sleep(0.2)
        game_thread.join()
    # Console to default state
    scr.addstr('GAME OVER\n')
    scr.refresh()
    cs.endwin()
    return

if __name__ == '__main__':
    main()
