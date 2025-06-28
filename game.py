import curses
import time
import math

from map_loader import Map
from player import Player

FRAME_DELAY = 1 / 30.0
VIEW_DISTANCE = 20.0
FOV = 0.7


def draw_scene(stdscr, game_map: Map, player: Player):
    height, width = stdscr.getmaxyx()
    horizon = height // 3

    forward_x = math.sin(player.angle)
    forward_y = -math.cos(player.angle)
    left_x = math.cos(player.angle)
    left_y = math.sin(player.angle)

    for sy in range(horizon, height):
        depth = ((sy - horizon + 1) / (height - horizon)) * VIEW_DISTANCE
        for sx in range(width):
            offset = ((sx - width / 2) / (width / 2)) * depth * FOV
            wx = player.x + forward_x * depth + left_x * offset
            wy = player.y + forward_y * depth + left_y * offset
            ch = game_map.char_at(wx, wy)
            if ch == 'o':
                stdscr.addch(sy, sx, ord('o'), curses.color_pair(1))
            elif ch == '=':
                stdscr.addch(sy, sx, ord('='), curses.color_pair(3))
            else:
                stdscr.addch(sy, sx, ord(' '), curses.color_pair(4))

    stdscr.addch(height - 2, width // 2, ord('A'), curses.color_pair(2))


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # walls
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # player
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # start line
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLUE)    # ground

    game_map = Map.from_file('sample_map.txt')
    player = Player(x=game_map.width / 2, y=game_map.height - 2)

    last_time = time.time()
    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        elif key == curses.KEY_LEFT:
            player.turn_left()
        elif key == curses.KEY_RIGHT:
            player.turn_right()

        player.throttle = key == ord(' ')
        player.update()

        stdscr.erase()
        draw_scene(stdscr, game_map, player)
        stdscr.refresh()

        elapsed = time.time() - last_time
        sleep_time = max(0, FRAME_DELAY - elapsed)
        time.sleep(sleep_time)
        last_time = time.time()


if __name__ == "__main__":
    curses.wrapper(main)
