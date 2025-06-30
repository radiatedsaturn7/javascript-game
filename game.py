import curses
import time
import math

from map_loader import Map
from player import Player

FRAME_DELAY = 1 / 30.0
VIEW_DISTANCE = 20.0
FOV = 0.7

MINIMAP_MAX_SIZE = 10


def draw_scene(stdscr, game_map: Map, player: Player):
    height, width = stdscr.getmaxyx()
    horizon = height // 3

    forward_x = math.sin(player.angle)
    forward_y = -math.cos(player.angle)
    left_x = math.cos(player.angle)
    left_y = math.sin(player.angle)

    for sy in range(horizon, height - 1):
        depth = ((sy - horizon + 1) / (height - horizon)) * VIEW_DISTANCE
        for sx in range(width - 1):
            offset = ((sx - width / 2) / (width / 2)) * depth * FOV
            wx = player.x + forward_x * depth + left_x * offset
            wy = player.y + forward_y * depth + left_y * offset
            ch = game_map.char_at(wx, wy)
            if ch in ('o', '~'):
                stdscr.addch(sy, sx, ord(ch), curses.color_pair(1))
            elif ch == '=':
                stdscr.addch(sy, sx, ord('='), curses.color_pair(3))
            else:
                stdscr.addch(sy, sx, ord(' '), curses.color_pair(5))

    # draw player ship near bottom center showing orientation
    ship_char = player.direction_arrow()
    stdscr.addch(height - 2, width // 2, ord(ship_char), curses.color_pair(2))

    # draw minimap in the top-left corner
    mini_h = min(game_map.height, MINIMAP_MAX_SIZE)
    mini_w = min(game_map.width, MINIMAP_MAX_SIZE)
    for my in range(mini_h):
        if my >= height:
            break
        for mx in range(mini_w):
            if mx >= width:
                break
            char = game_map.char_at(mx, my)
            color = curses.color_pair(5)  # track by default
            if char in ('o', '~'):
                color = curses.color_pair(1)
            elif char == '=':
                color = curses.color_pair(3)
            elif char != ' ':
                color = curses.color_pair(4)
            draw_char = char
            if int(player.x) == mx and int(player.y) == my:
                draw_char = player.direction_arrow()
                color = curses.color_pair(2)
            stdscr.addch(my, mx, ord(draw_char), color)

    # draw health bar at top right (scaled to 10 segments)
    max_len = 10
    filled = max(0, min(max_len, int((player.health / 100) * max_len)))
    health_str = 'HP:[' + '#' * filled + ' ' * (max_len - filled) + ']'
    start_x = max(0, width - len(health_str) - 1)
    for idx, ch in enumerate(health_str):
        if start_x + idx < width:
            color = curses.color_pair(3) if ch == '#' else curses.color_pair(4)
            stdscr.addch(0, start_x + idx, ord(ch), color)


def explosion_animation(stdscr, width, height):
    """Simple explosion effect when health reaches zero."""
    frames = ['***', '###', '   ']
    center_y = height - 2
    center_x = width // 2
    for frame in frames:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ch = frame[(dy + 1)] if abs(dy) == abs(dx) else frame[1]
                y = center_y + dy
                x = center_x + dx
                if 0 <= y < height and 0 <= x < width:
                    stdscr.addch(y, x, ord(ch), curses.color_pair(6))
        stdscr.refresh()
        time.sleep(0.15)


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # obstacles
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # player ship
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)    # start line
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)   # minimap features
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLACK)  # drivable track
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_RED)   # explosion

    game_map = Map.from_file('sample_map.txt')
    player = Player(x=game_map.start_x, y=game_map.start_y)

    last_time = time.time()
    left_timer = right_timer = throttle_timer = 0
    boost_request = False
    while True:
        keys = []
        while True:
            key = stdscr.getch()
            if key == -1:
                break
            keys.append(key)

        for key in keys:
            if key in (ord('q'), ord('Q')):
                return
            elif key == curses.KEY_LEFT:
                left_timer = 3
            elif key == curses.KEY_RIGHT:
                right_timer = 3
            elif key == ord(' '):
                throttle_timer = 3
            elif key in (ord('b'), ord('B')):
                boost_request = True

        if left_timer > 0:
            player.turn_left()
            left_timer -= 1
        if right_timer > 0:
            player.turn_right()
            right_timer -= 1

        player.throttle = throttle_timer > 0
        if throttle_timer > 0:
            throttle_timer -= 1
        if boost_request:
            player.start_boost()
            boost_request = False

        prev_x, prev_y = player.x, player.y
        player.update()
        if game_map.char_at(player.x, player.y) == 'o':
            player.x, player.y = prev_x, prev_y
            player.speed = 0
            player.health -= 1
            if player.health <= 0:
                height, width = stdscr.getmaxyx()
                explosion_animation(stdscr, width, height)
                break

        stdscr.erase()
        draw_scene(stdscr, game_map, player)
        stdscr.refresh()

        elapsed = time.time() - last_time
        sleep_time = max(0, FRAME_DELAY - elapsed)
        time.sleep(sleep_time)
        last_time = time.time()


if __name__ == "__main__":
    curses.wrapper(main)
