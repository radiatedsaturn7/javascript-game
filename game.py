import curses
import time
from typing import List

from track import Track
from player import Player

FRAME_DELAY = 1 / 30.0


def draw_track(stdscr, center_x: int, horizon: int, track: Track, player: Player):
    height, width = stdscr.getmaxyx()
    max_depth = height - horizon - 1
    track_center = center_x + int(track.offset * center_x)
    for depth in range(max_depth):
        perspective = depth / max_depth
        road_width = int(perspective * width * 0.6) + 3
        left = track_center - road_width // 2
        right = track_center + road_width // 2
        y = horizon + depth
        if 0 <= y < height:
            if left >= 0:
                stdscr.addch(y, min(width - 1, left), ord('|'), curses.color_pair(1))
            if right < width:
                stdscr.addch(y, min(width - 1, right), ord('|'), curses.color_pair(1))
            for x in range(max(0, left + 1), min(width - 1, right)):
                stdscr.addch(y, x, ord(' '), curses.color_pair(4))

    # draw player
    bottom_y = height - 2
    lane_width = (width * 0.6) / player.lanes
    player_x = track_center - int((width * 0.6) / 2) + int(lane_width * player.position + lane_width / 2)
    player_x = max(0, min(width - 1, player_x))
    stdscr.addch(bottom_y, player_x, ord('A'), curses.color_pair(2))


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # track edges
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # player
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLUE)  # road surface

    height, width = stdscr.getmaxyx()
    center_x = width // 2
    horizon = height // 4
    track = Track()
    player = Player()

    last_time = time.time()
    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        elif key == curses.KEY_LEFT:
            player.move_left()
        elif key == curses.KEY_RIGHT:
            player.move_right()

        track.update()

        stdscr.erase()
        draw_track(stdscr, center_x, horizon, track, player)
        stdscr.refresh()

        # maintain frame rate
        elapsed = time.time() - last_time
        sleep_time = max(0, FRAME_DELAY - elapsed)
        time.sleep(sleep_time)
        last_time = time.time()


if __name__ == "__main__":
    curses.wrapper(main)
