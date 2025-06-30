import curses
import time
import math

from map_loader import Map
from player import Player

FRAME_DELAY = 1 / 30.0
VIEW_DISTANCE = 20.0
FOV = 0.7
CHAR_RATIO = 0.5
CAMERA_OFFSET = 2.0
MAP_SCALE = 2.0

MINIMAP_MAX_SIZE = 10


def load_background(path):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            if line.strip() == 'KEY:':
                break
            lines.append(line.rstrip('\n'))
    return lines


BACKGROUND = load_background('sample_background.txt')
BG_COLOR_MAP = {
    '|': 13,
    '_': 13,
    'x': 13,
    '\\': 14,
    'X': 14,
    'o': 15,
    '!': 6,
    '~': 3,
    '*': 14,
    '.': 17,
}


def format_time(t: float) -> str:
    m = int(t // 60)
    s = t % 60
    return f"{m:02d}:{s:05.2f}"


def draw_scene(stdscr, game_map: Map, player: Player, flash=None, background=None):
    height, width = stdscr.getmaxyx()
    horizon = height // 3
    if flash is None:
        flash = {'x': None, 'y': None, 'timer': 0}
    if background is None:
        background = BACKGROUND

    forward_x = math.sin(player.angle)
    forward_y = -math.cos(player.angle)
    right_x = math.cos(player.angle)
    right_y = math.sin(player.angle)

    # camera slightly behind the player for a third-person view

    cam_x = player.x - forward_x * CAMERA_OFFSET
    cam_y = player.y - forward_y * CAMERA_OFFSET

    bg_h = len(background)
    bg_w = max(len(l) for l in background) if bg_h else 0
    for sy in range(horizon):
        if bg_h == 0:
            break
        rel_y = sy / max(1, horizon - 1)
        by = int(rel_y * bg_h)
        for sx in range(width):
            ang = (sx / width - 0.5) * FOV
            world_ang = (player.angle + ang) % (2 * math.pi)
            bx = int((world_ang / (2 * math.pi)) * bg_w)
            ch = ' '
            if 0 <= by < bg_h and 0 <= bx < len(background[by]):
                ch = background[by][bx]
            color_id = BG_COLOR_MAP.get(ch, 12)
            if ch == '.':
                color_id = 17 if player.frame % 2 == 0 else 18
            stdscr.addch(sy, sx, ord(ch), curses.color_pair(color_id))

    for sy in range(horizon, height - 1):
        depth = ((height - sy) / (height - horizon)) * VIEW_DISTANCE
        for sx in range(width - 1):
            offset = ((sx - width / 2) / (width / 2)) * depth * FOV * CHAR_RATIO
            wx = cam_x + forward_x * depth + right_x * offset
            wy = cam_y + forward_y * depth + right_y * offset
            ch = game_map.char_at(wx / MAP_SCALE, wy / MAP_SCALE)
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
        flame_lines = [flame_line]
        if player.speed > 0:
            flame_lines.append(flame_line)
        start_y = height - 4
        start_x = width // 2 - len(lines[0]) // 2
        for i, line in enumerate(lines):
            for j, ch in enumerate(line):
                y = start_y + i
                x = start_x + j
                if 0 <= y < height and 0 <= x < width:
                    stdscr.addch(y, x, ord(ch), curses.color_pair(2))
        i = len(lines)
        for k, fl in enumerate(flame_lines):
            for j, ch in enumerate(fl):
                y = start_y + i + k
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
            if int(player.x / MAP_SCALE) == mx and int(player.y / MAP_SCALE) == my:
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

    hud_lines = []
    hud_lines.append(f"Lap:{player.lap}")
    best = '--:--.--' if player.best_lap is None else format_time(player.best_lap)
    hud_lines.append(f"Best:{best}")
    hud_lines.append(f"Time:{format_time(player.total_time())}")
    hud_lines.append("Place:1st")
    hud_lines.append(f"A:{int(math.degrees(player.angle)) % 360:3d}")

    for idx, text in enumerate(hud_lines, start=1):
        start_x = max(0, width - len(text) - 1)
        if height > idx:
            for j, ch in enumerate(text):
                if start_x + j < width:
                    stdscr.addch(idx, start_x + j, ord(ch), curses.color_pair(4))


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
    curses.init_pair(12, curses.COLOR_BLUE, curses.COLOR_BLACK)    # background blue
    curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_BLACK)   # grey
    curses.init_pair(14, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # yellow
    curses.init_pair(15, curses.COLOR_GREEN, curses.COLOR_BLACK)   # green
    curses.init_pair(16, curses.COLOR_GREEN, curses.COLOR_BLACK)   # dark green
    curses.init_pair(17, curses.COLOR_RED, curses.COLOR_BLACK)     # blink bright
    curses.init_pair(18, curses.COLOR_RED, curses.COLOR_BLACK)     # blink dark

    game_map = Map.from_file('sample_map.txt')
    player = Player(x=game_map.start_x * MAP_SCALE, y=game_map.start_y * MAP_SCALE)
    flash_wall = {'x': None, 'y': None, 'timer': 0}

    start_line_y = game_map.start_y * MAP_SCALE

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
        if prev_y < start_line_y <= player.y:
            player.complete_lap()
        if game_map.char_at(player.x / MAP_SCALE, player.y / MAP_SCALE) == 'o':
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
