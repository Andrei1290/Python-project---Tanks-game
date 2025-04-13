import pygame
import time
import math
from bullet import Bullet
from tank import Tank
from smoke import Smoke

class EnemyTank(Tank):
    def __init__(self, x, y, image_t, bullet_image, target_player, fire_sound=None):
        super().__init__(x, y, image_t, bullet_image, fire_sound)
        self.target_player = target_player
        self.step_size = 10
        self.grid_size = 80
        self.move_delay = 0.1
        self.last_move_time = time.time()
        self.min_distance = 50
        self.path_stack = []
        self.visited = set()
        self.current_direction = None
        self.directions = [0, 90, 180, 270]
        self.distance_moved = 0
        self.target_cell = None
        self.stuck_timer = 0
        self.stuck_threshold = 5.0
        self.last_turn_time = time.time()
        self.turn_delay = 0.1

    def check_collision(self, walls, new_rect, player=None, enemies=None):
        for wall in walls:
            if new_rect.colliderect(wall.rect):
                return True
        if player and new_rect.colliderect(player.rect) and player.alive():
            return True
        if enemies:
            for enemy in enemies:
                if enemy != self and new_rect.colliderect(enemy.rect) and enemy.alive():
                    return True
        return False

    def get_possible_directions(self, walls, from_pos, player, enemies):
        possible_directions = []
        original_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        original_rect.center = from_pos
        for direction in self.directions:
            new_rect = original_rect.copy()
            if direction == 0:
                new_rect.y -= self.grid_size
            elif direction == 90:
                new_rect.x += self.grid_size
            elif direction == 180:
                new_rect.y += self.grid_size
            elif direction == 270:
                new_rect.x -= self.grid_size
            if not self.check_collision(walls, new_rect, player, enemies):
                grid_pos = (new_rect.centerx // self.grid_size, new_rect.centery // self.grid_size)
                if grid_pos not in self.visited:
                    possible_directions.append(direction)
        return possible_directions

    def move_to_direction(self, direction, player, enemies):
        now = time.time()
        if direction != self.direction and now - self.last_turn_time < self.turn_delay:
            direction = self.current_direction if self.current_direction is not None else self.direction
        else:
            self.direction = direction
            self.last_turn_time = now

        original_rect = self.rect.copy()
        if direction == 0:
            self.rect.y -= self.step_size
        elif direction == 90:
            self.rect.x += self.step_size
        elif direction == 180:
            self.rect.y += self.step_size
        elif direction == 270:
            self.rect.x -= self.step_size

        self.rect.x = max(0, min(self.rect.x, 800 - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, 800 - self.rect.height))

        if self.check_collision(self.target_player.walls, self.rect, player, enemies):
            self.rect = original_rect
            return False

        self.distance_moved += self.step_size
        self.current_direction = direction
        return True

    def sees_player(self, player, direction):
        tolerance = 10
        if direction == 0:
            return (abs(self.rect.centerx - player.rect.centerx) <= tolerance and
                    self.rect.centery > player.rect.centery)
        elif direction == 180:
            return (abs(self.rect.centerx - player.rect.centerx) <= tolerance and
                    self.rect.centery < player.rect.centery)
        elif direction == 90:
            return (abs(self.rect.centery - player.rect.centery) <= tolerance and
                    self.rect.centerx < player.rect.centerx)
        elif direction == 270:
            return (abs(self.rect.centery - player.rect.centery) <= tolerance and
                    self.rect.centerx > player.rect.centerx)
        return False

    def update(self, player, bullet_group, walls, enemies=None, smoke_group=None):
        now = time.time()
        if now - self.last_move_time < self.move_delay:
            return

        self.target_player.walls = walls

        sees_player = False
        target_direction = self.direction
        for direction in self.directions:
            if now - self.last_turn_time >= self.turn_delay:
                if self.sees_player(player, direction):
                    sees_player = True
                    target_direction = direction
                    self.direction = direction
                    self.last_turn_time = now
                    break
            else:
                if self.sees_player(player, self.direction):
                    sees_player = True
                    target_direction = self.direction
                    break

        if sees_player and now - self.last_shot_time >= self.shot_delay:
            self.shoot(bullet_group)
            self.last_shot_time = now
            self.stuck_timer = 0
            self.image = pygame.transform.rotate(self.image_t, -self.direction)
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)
            self.last_move_time = now
            return

        # Спавн дыма при низком здоровье
        if self.health == 1 and smoke_group is not None:
            if time.time() - self.last_smoke_time >= self.smoke_delay:
                smoke = Smoke(self.rect.centerx, self.rect.centery)
                smoke_group.add(smoke)
                self.last_smoke_time = time.time()

        self.stuck_timer += now - self.last_move_time
        if self.stuck_timer > self.stuck_threshold:
            self.visited.clear()
            self.path_stack.clear()
            self.stuck_timer = 0
            self.current_direction = None
            self.distance_moved = 0

        if self.current_direction is not None and self.distance_moved < self.grid_size:
            success = self.move_to_direction(self.current_direction, player, enemies)
            if not success:
                self.distance_moved = self.grid_size
        else:
            self.distance_moved = 0
            current_grid_pos = (self.rect.centerx // self.grid_size, self.rect.centery // self.grid_size)

            if current_grid_pos not in self.visited:
                self.visited.add(current_grid_pos)

            possible_directions = self.get_possible_directions(walls, self.rect.center, player, enemies)

            if possible_directions:
                self.path_stack.append({
                    'pos': self.rect.center,
                    'directions_tried': [],
                    'direction_from': self.current_direction
                })

                best_direction = None
                min_distance = float('inf')
                player_pos = (player.rect.centerx, player.rect.centery)
                for direction in possible_directions:
                    new_pos = list(self.rect.center)
                    if direction == 0:
                        new_pos[1] -= self.grid_size
                    elif direction == 90:
                        new_pos[0] += self.grid_size
                    elif direction == 180:
                        new_pos[1] += self.grid_size
                    elif direction == 270:
                        new_pos[0] -= self.grid_size
                    distance = math.hypot(player_pos[0] - new_pos[0], player_pos[1] - new_pos[1])
                    if distance < min_distance:
                        min_distance = distance
                        best_direction = direction

                if now - self.last_turn_time >= self.turn_delay:
                    success = self.move_to_direction(best_direction, player, enemies)
                    if success:
                        self.path_stack[-1]['directions_tried'].append(best_direction)
                    else:
                        self.path_stack.pop()
                        self.distance_moved = self.grid_size
                else:
                    if self.current_direction in possible_directions:
                        success = self.move_to_direction(self.current_direction, player, enemies)
                        if success:
                            self.path_stack[-1]['directions_tried'].append(self.current_direction)
                        else:
                            self.path_stack.pop()
                            self.distance_moved = self.grid_size
                    else:
                        self.distance_moved = self.grid_size
            else:
                if self.path_stack:
                    last_fork = self.path_stack.pop()
                    self.rect.center = last_fork['pos']
                    self.visited = set(pos for pos in self.visited if math.hypot(pos[0] * self.grid_size - last_fork['pos'][0], pos[1] * self.grid_size - last_fork['pos'][1]) > self.grid_size)
                    self.current_direction = last_fork['direction_from']
                    self.distance_moved = 0
                else:
                    self.current_direction = None

        self.image = pygame.transform.rotate(self.image_t, -self.direction)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

        self.last_move_time = now