from player import Player
import math


class AIPlayer(Player):
    """Improved AI driver that prefers boosts and avoids obstacles."""

    def __init__(self, *args, difficulty: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.throttle = True
        self.difficulty = difficulty

    def _score_direction(self, ang: float, look_dist: float, game_map) -> float:
        """Score a direction based on the tile at the lookahead location."""
        lx = self.x + math.sin(ang) * look_dist
        ly = self.y - math.cos(ang) * look_dist
        tile = game_map.char_at(lx / 5.0, ly / 5.0)
        score = 0.0
        if tile == 'o':
            score -= 5
        else:
            score += 1
            if tile == 'B':
                score += 3
            if tile == 'J':
                score += 2
            if tile == 'H' and self.health < 80:
                score += 2
        return score

    def update_ai(self, game_map):
        look_dist = 3.0
        angles = [-0.3, 0.0, 0.3]
        scores = [self._score_direction(self.angle + a, look_dist, game_map) for a in angles]
        best_idx = scores.index(max(scores))
        if angles[best_idx] < 0:
            self.turn_left()
        elif angles[best_idx] > 0:
            self.turn_right()

        # throttle only if the path ahead is clear
        front_x = self.x + math.sin(self.angle) * look_dist
        front_y = self.y - math.cos(self.angle) * look_dist
        front = game_map.char_at(front_x / 5.0, front_y / 5.0)
        self.throttle = front != 'o'
        super().update()


class AIOrchestrator:
    """Adjust overall AI difficulty to keep the race interesting."""

    def __init__(self, player: Player, ai_players: list):
        self.player = player
        self.ai_players = ai_players

    def _progress(self, racer, game_map) -> float:
        start_x = game_map.start_x * 5.0
        start_y = game_map.start_y * 5.0
        return math.hypot(racer.x - start_x, racer.y - start_y)

    def update(self, game_map):
        player_prog = self._progress(self.player, game_map)
        ai_progs = [self._progress(ai, game_map) for ai in self.ai_players]
        best_ai = max(ai_progs) if ai_progs else 0.0

        for ai in self.ai_players:
            if player_prog - best_ai > 20:
                ai.BASE_ACCEL = min(0.03, ai.BASE_ACCEL + 0.005)
            elif best_ai - player_prog > 20:
                ai.BASE_ACCEL = max(0.015, ai.BASE_ACCEL - 0.005)
            ai.update_ai(game_map)

