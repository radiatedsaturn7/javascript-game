import curses
import time
import math
import sys

from map_loader import Map
from player import Player
from ai import AIPlayer, AIOrchestrator

FRAME_DELAY = 1 / 30.0
# Rendering constants
# Increase view distance so the track stretches further out and appears less
# like a vertical ramp.
# Double the view distance so the horizon stretches further and objects
# can appear closer or farther away in the pseudo‑3D projection.
VIEW_DISTANCE = 120.0

# Slightly narrower field of view and a camera a bit closer to the player help
# reduce the "quarter-pipe" appearance.
FOV = 1.0
CHAR_RATIO = 0.5
CAMERA_OFFSET = 2.0
MAP_SCALE = 5.0
MINIMAP_MAX_SIZE = 10


def enter_fullscreen():
    """Switch terminal to the alternate buffer."""
    sys.stdout.write("\x1b[?1049h\x1b[H")
    sys.stdout.flush()


def exit_fullscreen():
    """Return terminal from the alternate buffer."""
    sys.stdout.write("\x1b[?1049l")
    sys.stdout.flush()

def load_background(path):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            if line.strip() == 'KEY:':
                break
            lines.append(line.rstrip('\n'))
    return lines


def load_ascii_art(path):
    lines = []
    with open(path, 'r') as f:
        for line in f:
            if line.strip() == 'KEY:':
                break
            lines.append(line.rstrip('\n'))
    return lines


BACKGROUND = load_background('sample_background.txt')
TITLE_ART = load_ascii_art('title.txt')
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


def show_title_screen(stdscr):
    """Display the ASCII title screen and wait for space to continue."""
    stdscr.erase()
    height, width = stdscr.getmaxyx()
    start_y = max(0, (height - len(TITLE_ART)) // 2)
    for idx, line in enumerate(TITLE_ART):
        x = max(0, (width - len(line)) // 2)
        if start_y + idx < height:
            stdscr.addstr(start_y + idx, x, line[: max(0, width - x)])
    stdscr.refresh()
    while True:
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q')):
            return False
        if ch == ord(' '):
            return True


def countdown(stdscr, draw_cb=None):
    """Display a short countdown before the race starts.

    If ``draw_cb`` is provided, it will be called each frame to draw the
    scene so the track and ships remain visible behind the timer.
    """
    height, width = stdscr.getmaxyx()
    for text in ["3", "2", "1", "GO!"]:
        if draw_cb:
            draw_cb()
        y = height // 2
        x = max(0, (width - len(text)) // 2)
        stdscr.addstr(y, x, text, curses.color_pair(14))
        stdscr.refresh()
        time.sleep(1)
    if draw_cb:
        draw_cb()


def draw_scene(stdscr, game_map: Map, player: Player, flash=None, background=None, ai_players=None):
    height, width = stdscr.getmaxyx()
    horizon = height // 3
    if flash is None:
        flash = {'x': None, 'y': None, 'timer': 0}
    if background is None:
        background = BACKGROUND
    if ai_players is None:
        ai_players = []

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
            tx = int(wx / MAP_SCALE)
            ty = int(wy / MAP_SCALE)
            ch = game_map.char_at(tx, ty)
            draw = ' '
            color = curses.color_pair(3)
            neighbors = [
                game_map.char_at(tx + dx, ty + dy)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            ]
            if ch == 'o':
                if flash['timer'] > 0 and flash['x'] == int(wx) and flash['y'] == int(wy):
                    color = curses.color_pair(10)
                else:
                    color = curses.color_pair(1)
                neighbors = [
                    game_map.char_at(tx + dx, ty + dy)
                    for dx in (-1, 0, 1)
                    for dy in (-1, 0, 1)
                    if not (dx == 0 and dy == 0)
                ]
                angle_to_cell = math.atan2(wy - cam_y, wx - cam_x)
                rel_ang = abs((angle_to_cell - player.angle + math.pi) % (2 * math.pi) - math.pi)
                shade_idx = min(3, int(rel_ang / (math.pi / 6)))
                if any(n != 'o' for n in neighbors):
                    shade_idx = min(shade_idx + 1, 3)
                shades = ['█', '▓', '▒', '░']
                draw = shades[shade_idx]
            elif ch == '~':
                color = curses.color_pair(4)
                draw = '░'
            elif ch == 'J':
                color = curses.color_pair(5)
                draw = '▓'
            elif ch == '#':
                color = curses.color_pair(6)
                draw = '▒'
            elif ch == '=':
                draw = '▓'
                if (int(wx) + int(wy)) % 2 == 0:
                    color = curses.color_pair(7)
                else:
                    color = curses.color_pair(10)
            # Apply simple blending at boundaries between different tiles
            if any(n != ch for n in neighbors):
                if draw == ' ':
                    draw = '░'
                elif draw in {'▓', '▒'}:
                    draw = '▒'
            stdscr.addch(sy, sx, ord(draw), color)

    def project(x, y):
        """Project world coordinates to screen coordinates and scale."""
        dx = x - cam_x
        dy = y - cam_y
        forward = dx * forward_x + dy * forward_y
        right = dx * right_x + dy * right_y
        if forward <= 0 or forward > VIEW_DISTANCE:
            return None
        sx = width // 2 + int((right / (forward * FOV)) * (width / 2) * CHAR_RATIO)
        sy = horizon + int((1 - forward / VIEW_DISTANCE) * (height - horizon))
        scale = max(1, int((VIEW_DISTANCE - forward) / (VIEW_DISTANCE / 3)))
        return sx, sy, scale


    def draw_ai(ai):
        """Render an AI racer with simple distance scaling and rotation."""
        pos = project(ai.x, ai.y)
        if not pos:
            return
        sx, sy, scale = pos
        char = ai.direction_arrow()
        for i in range(scale):
            y = sy - i
            if 0 <= y < height and 0 <= sx < width - 1:
                stdscr.addch(y, sx, ord(char), curses.color_pair(15))

    for ai in ai_players:
        draw_ai(ai)

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
        start_y = height - 4 - int(player.z)
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

    # draw minimap in the top-left corner with a border
    mini_h = min(game_map.height, MINIMAP_MAX_SIZE)
    mini_w = min(game_map.width, MINIMAP_MAX_SIZE)
    start_y = 1
    start_x = 1

    # keep player centered on the minimap
    px = int(player.x / MAP_SCALE)
    py = int(player.y / MAP_SCALE)
    map_start_x = max(0, min(game_map.width - mini_w, px - mini_w // 2))
    map_start_y = max(0, min(game_map.height - mini_h, py - mini_h // 2))

    for my in range(mini_h):
        if start_y + my >= height:
            break
        for mx in range(mini_w):
            if start_x + mx >= width:
                break
            map_x = map_start_x + mx
            map_y = map_start_y + my
            char = game_map.char_at(map_x, map_y)
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
            if px == map_x and py == map_y:
                draw_char = player.direction_arrow()
                color = curses.color_pair(2)
            stdscr.addch(start_y + my, start_x + mx, ord(draw_char), color)

    # minimap border
    if start_y - 1 >= 0 and start_x - 1 >= 0:
        for x in range(mini_w + 2):
            if start_x - 1 + x < width:
                stdscr.addch(start_y - 1, start_x - 1 + x, ord('#'), curses.color_pair(4))
        for x in range(mini_w + 2):
            if start_x - 1 + x < width and start_y + mini_h < height:
                stdscr.addch(start_y + mini_h, start_x - 1 + x, ord('#'), curses.color_pair(4))
        for y in range(mini_h):
            if start_y + y < height:
                if start_x - 1 >= 0:
                    stdscr.addch(start_y + y, start_x - 1, ord('#'), curses.color_pair(4))
                if start_x + mini_w < width:
                    stdscr.addch(start_y + y, start_x + mini_w, ord('#'), curses.color_pair(4))

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
    stdscr.nodelay(False)
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

    if not show_title_screen(stdscr):
        return

    game_map = Map.from_file('sample_map.txt')
    player = Player(x=game_map.start_x * MAP_SCALE, y=game_map.start_y * MAP_SCALE)
    ai_players = [
        AIPlayer(
            x=player.x,
            y=player.y + (i + 1)
        )
        for i in range(31)
    ]
    orchestrator = AIOrchestrator(player, ai_players)
    flash_wall = {'x': None, 'y': None, 'timer': 0}

    def draw_start_scene():
        stdscr.erase()
        draw_scene(stdscr, game_map, player, flash_wall, ai_players=ai_players)
        stdscr.refresh()

    draw_start_scene()
    countdown(stdscr, draw_cb=draw_start_scene)
    stdscr.nodelay(True)

    start_line_y = game_map.start_y * MAP_SCALE

    last_time = time.time()
    key_timers = {}

    KEY_HOLD_FRAMES = 6

    def press(k):
        # refresh timers for all currently pressed keys so multiple
        # simultaneous key presses remain active even if only one
        # generates repeat events
        for existing in list(key_timers.keys()):
            key_timers[existing] = KEY_HOLD_FRAMES
        key_timers[k] = KEY_HOLD_FRAMES

    while True:
        while True:
            key = stdscr.getch()
            if key == -1:
                break
            if key in (ord('q'), ord('Q')):
                return
            press(key)

        if key_timers.get(curses.KEY_LEFT, 0) > 0:
            player.turn_left()
        if key_timers.get(curses.KEY_RIGHT, 0) > 0:
            player.turn_right()
        if key_timers.get(curses.KEY_UP, 0) > 0:
            player.vertical_input(1)
        if key_timers.get(curses.KEY_DOWN, 0) > 0:
            player.vertical_input(-1)

        player.throttle = key_timers.get(ord(' '), 0) > 0

        if key_timers.get(ord('b'), 0) > 0 or key_timers.get(ord('B'), 0) > 0:
            player.start_boost()

        for k in list(key_timers.keys()):
            key_timers[k] -= 1
            if key_timers[k] <= 0:
                del key_timers[k]

        if flash_wall['timer'] > 0:
            flash_wall['timer'] -= 1

        prev_x, prev_y = player.x, player.y
        player.update()
        orchestrator.update(game_map)
        tile = game_map.char_at(player.x / MAP_SCALE, player.y / MAP_SCALE)
        if prev_y < start_line_y <= player.y:
            player.complete_lap()
        if tile == 'J':
            player.jump()
        if tile == 'o':
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
        draw_scene(stdscr, game_map, player, flash_wall, ai_players=ai_players)
        stdscr.refresh()

        elapsed = time.time() - last_time
        sleep_time = max(0, FRAME_DELAY - elapsed)
        time.sleep(sleep_time)
        last_time = time.time()


if __name__ == "__main__":
    enter_fullscreen()
    try:
        curses.wrapper(main)
    finally:
        exit_fullscreen()
