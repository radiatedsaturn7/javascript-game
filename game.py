import curses
import time
import math

from map_loader import Map
from player import Player

FRAME_DELAY = 1 / 30.0
VIEW_DISTANCE = 20.0
FOV = 0.7

MINIMAP_MAX_SIZE = 10


def draw_scene(stdscr, game_map: Map, player: Player, flash=None):
    height, width = stdscr.getmaxyx()
    horizon = height // 3
    if flash is None:
        flash = {'x': None, 'y': None, 'timer': 0}

    forward_x = math.sin(player.angle)
    forward_y = -math.cos(player.angle)
    right_x = math.cos(player.angle)
    right_y = math.sin(player.angle)

    # camera slightly behind the player for a third-person view
    cam_x = player.x - forward_x
    cam_y = player.y - forward_y

    for sy in range(horizon, height - 1):
        depth = ((height - sy) / (height - horizon)) * VIEW_DISTANCE
        for sx in range(width - 1):
            offset = ((sx - width / 2) / (width / 2)) * depth * FOV
            wx = cam_x + forward_x * depth + right_x * offset
            wy = cam_y + forward_y * depth + right_y * offset
            ch = game_map.char_at(wx, wy)
            draw = ' '
            color = curses.color_pair(3)
            if ch == 'o':
                if flash['timer'] > 0 and flash['x'] == int(wx) and flash['y'] == int(wy):
                    color = curses.color_pair(10)
                else:
                    color = curses.color_pair(1)
                draw = 'o'
            elif ch == '~':
                color = curses.color_pair(4)
                draw = '~'
            elif ch == 'J':
                color = curses.color_pair(5)
                draw = 'J'
            elif ch == '#':
                color = curses.color_pair(6)
                draw = '#'
            elif ch == '=':
                draw = '#'
                if (int(wx) + int(wy)) % 2 == 0:
                    color = curses.color_pair(7)
                else:
                    color = curses.color_pair(10)
            stdscr.addch(sy, sx, ord(draw), color)

    # draw player ship near bottom center showing orientation
    def draw_ship():
        lines = ["   _|^|_", "--/O--O\\--"]
        flames = "oo" if player.frame % 2 == 0 else "OO"
        if player.lean < -0.5:
            lines = ["  _/|^|_", "-/O--O\\---"]
        elif player.lean > 0.5:
            lines = [" _|^|_\\ ", "---/O--O\\-"]
        flame_line = f"   {flames[0]}  {flames[1]}"
        start_y = height - 4
        start_x = width // 2 - len(lines[0]) // 2
        for i, line in enumerate(lines):
            for j, ch in enumerate(line):
                y = start_y + i
                x = start_x + j
                if 0 <= y < height and 0 <= x < width:
                    stdscr.addch(y, x, ord(ch), curses.color_pair(2))
        i = len(lines)
        for j, ch in enumerate(flame_line):
            y = start_y + i
            x = start_x + j
            if 0 <= y < height and 0 <= x < width:
                color = curses.color_pair(9) if player.boosting else curses.color_pair(8)
                stdscr.addch(y, x, ord(ch), color)
    draw_ship()

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
            color = curses.color_pair(3)  # road by default
            if char == 'o':
                color = curses.color_pair(1)
            elif char == '~':
                color = curses.color_pair(4)
            elif char == 'J':
                color = curses.color_pair(5)
            elif char == '#':
                color = curses.color_pair(6)
            elif char == '=':
                color = curses.color_pair(7)
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

    angle_str = f"A:{int(math.degrees(player.angle)) % 360:3d}"
    start_x = max(0, width - len(angle_str) - 1)
    if height > 1:
        for idx, ch in enumerate(angle_str):
            if start_x + idx < width:
                stdscr.addch(1, start_x + idx, ord(ch), curses.color_pair(4))


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
                    stdscr.addch(y, x, ord(ch), curses.color_pair(11))
        stdscr.refresh()
        time.sleep(0.15)


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # wall
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)    # ship body
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)    # road
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)     # water
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)     # jump pad
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # dirt
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)    # start line checker
    curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)      # flame
    curses.init_pair(9, curses.COLOR_BLUE, curses.COLOR_BLACK)     # boost flame
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)   # empty / flash
    curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_RED)    # explosion

    game_map = Map.from_file('sample_map.txt')
    player = Player(x=game_map.start_x, y=game_map.start_y)
    flash_wall = {'x': None, 'y': None, 'timer': 0}

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

        if flash_wall['timer'] > 0:
            flash_wall['timer'] -= 1

        prev_x, prev_y = player.x, player.y
        player.update()
        if game_map.char_at(player.x, player.y) == 'o':
            flash_wall['x'] = int(player.x)
            flash_wall['y'] = int(player.y)
            flash_wall['timer'] = 3
            player.x = prev_x - math.sin(player.angle) * 0.5
            player.y = prev_y + math.cos(player.angle) * 0.5
            player.speed = -0.2
            player.health -= 1
            if player.health <= 0:
                height, width = stdscr.getmaxyx()
                explosion_animation(stdscr, width, height)
                break

        stdscr.erase()
        draw_scene(stdscr, game_map, player, flash_wall)
        stdscr.refresh()

        elapsed = time.time() - last_time
        sleep_time = max(0, FRAME_DELAY - elapsed)
        time.sleep(sleep_time)
        last_time = time.time()


if __name__ == "__main__":
    curses.wrapper(main)
