import unittest
from unittest.mock import patch

from map_loader import Map
from player import Player
import game
import math


class DummyScreen:
    def __init__(self, height=5, width=10):
        self.height = height
        self.width = width
        self.calls = []

    def getmaxyx(self):
        return self.height, self.width

    def addch(self, y, x, ch, attr=0):
        if y >= self.height or x >= self.width:
            raise IndexError('addch out-of-bounds')
        self.calls.append((y, x, ch))

    def erase(self):
        pass

    def refresh(self):
        pass


class MapTests(unittest.TestCase):
    def test_char_at_bounds(self):
        m = Map(['ab', 'cd'])
        self.assertEqual(m.char_at(0, 0), 'a')
        self.assertEqual(m.char_at(1, 1), 'd')
        # Out of bounds should return wall character 'o'
        self.assertEqual(m.char_at(-1, -1), 'o')
        self.assertEqual(m.char_at(5, 5), 'o')


class PlayerTests(unittest.TestCase):
    def test_update_and_turn(self):
        p = Player()
        p.throttle = True
        p.update()
        self.assertGreater(p.speed, 0)
        before_x, before_y = p.x, p.y
        p.turn_right()
        p.update()
        self.assertNotEqual((before_x, before_y), (p.x, p.y))
        p.throttle = False
        p.update()
        self.assertLessEqual(p.speed, 1.0)

    def test_direction_arrow(self):
        p = Player()
        p.angle = 0.0
        self.assertEqual(p.direction_arrow(), '^')
        p.angle = math.pi / 2
        self.assertEqual(p.direction_arrow(), '>')
        p.angle = math.pi
        self.assertEqual(p.direction_arrow(), 'v')
        p.angle = 3 * math.pi / 2
        self.assertEqual(p.direction_arrow(), '<')


class TrackTests(unittest.TestCase):
    def test_offset_clamped(self):
        from track import Track
        t = Track()
        for _ in range(100):
            off = t.update()
            self.assertGreaterEqual(off, -1.0)
            self.assertLessEqual(off, 1.0)


class DrawSceneTests(unittest.TestCase):
    def test_draw_scene_with_small_screen(self):
        scr = DummyScreen(height=4, width=6)
        m = Map(['oooooo', 'o    o', 'oooooo'])
        p = Player(x=2, y=2)
        with patch.object(game.curses, 'color_pair', return_value=0):
            # Should not raise IndexError from DummyScreen.addch
            game.draw_scene(scr, m, p)
        for y, x, _ in scr.calls:
            self.assertLess(y, scr.height)
            self.assertLess(x, scr.width)


if __name__ == '__main__':
    unittest.main()
