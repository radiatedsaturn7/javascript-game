from player import Player
import math

class AIPlayer(Player):
    """Simple AI driver that follows the track."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.throttle = True

    def update_ai(self, game_map):
        # Look ahead and steer away from walls
        look_dist = 2.0
        front_x = self.x + math.sin(self.angle) * look_dist
        front_y = self.y - math.cos(self.angle) * look_dist
        front = game_map.char_at(front_x / 4.0, front_y / 4.0)
        if front == 'o':
            # try turning
            left_a = self.angle - 0.4
            left_x = self.x + math.sin(left_a) * look_dist
            left_y = self.y - math.cos(left_a) * look_dist
            right_a = self.angle + 0.4
            right_x = self.x + math.sin(right_a) * look_dist
            right_y = self.y - math.cos(right_a) * look_dist
            left = game_map.char_at(left_x / 4.0, left_y / 4.0)
            right = game_map.char_at(right_x / 4.0, right_y / 4.0)
            if left != 'o':
                self.turn_left()
            elif right != 'o':
                self.turn_right()
            else:
                self.turn_left()
        else:
            # small random jitter to simulate steering
            pass
        super().update()

