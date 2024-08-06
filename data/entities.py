import random
import math
from .entity import Entity
from .utils import *
from .settings import CELL_SIZE
false = False
true = True

MAX_JUMPS = 2

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.vel = [0, 0]
        self.speed = 4
        self.air_time = 0
        self.jumps = 1
        self.health = 100
        self.hurt_timer = 0
        self.img_offset = [0, 0]
        self.flip = false
        self.inputs = [False, False, False, False]
        self.jumped = False
        self.image_base_dimensions = [CELL_SIZE, CELL_SIZE]
        self.scale = [1, 1]
        self.squish_velocity = 0
        self.firerate = 4
        self.fire_timer = 4
        self.jumps = MAX_JUMPS

    def update(self, dt):
        super().update(dt)
        self.inputs = self.data.inputs.copy()
        if self.inputs[0] or self.inputs[1]:
            self.change_state('run')

        
        if not self.inputs[0] and not self.inputs[1] and not self.inputs[2] and self.air_time == 0 and self.state != 'hurt':
            self.change_state('idle')
        if self.inputs[0]:
            self.flip = true
        elif self.inputs[1]:
            self.flip = false

        self.vel[0] = (self.inputs[1] - self.inputs[0]) * self.speed
        self.vel[1] = min(14, self.vel[1]+1)

        hitable_rects = self.data.tile_map.get_surrounding_tiles(self.center())
        collisions = self.movement(self.vel, hitable_rects)

        self.squash_effect(collisions)

        if collisions['down']:
            self.vel[1] = 0
            self.air_time = 0
            self.jumps = MAX_JUMPS
        else:
            self.air_time += 1

        if self.data.left_clicked:
            pass
        else:
            self.fire_timer = self.firerate

    def jump(self):
        if self.jumps > 0:
            self.vel[1] = -10
            self.jumps -= 1

    def render(self, surf, offset=[0, 0]):
        offset = offset.copy()
        if self.anim.config['offset']:
            offset[0] += self.anim.config['offset'][0]
            offset[1] += self.anim.config['offset'][1]
        img = self.anim.image()
        if self.scale != [1, 1]:
            img = pg.transform.scale(img, (int(self.scale[0] * self.image_base_dimensions[0]), int(self.scale[1] * self.image_base_dimensions[1])))
            x_diff = (CELL_SIZE - img.get_width()) // 2
            y_diff = (CELL_SIZE - img.get_height()) // 2
            offset[0] -= x_diff
            offset[1] -= y_diff * 2
        if self.flip:
            img = pg.transform.flip(img, self.flip, false)
        if self.anim.config['outline']:
            outline(surf, img, ((
                self.pos[0] - offset[0]), (self.pos[1] - offset[1])), self.anim.config['outline'])
        surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def squash_effect(self, collisions):

        self.scale[1] += self.squish_velocity
        self.scale[1] = max(0.3, min(self.scale[1], 1.5))
        self.scale[0] = 2 - self.scale[1]

        if self.scale[1] > 1:
            self.squish_velocity -= 0.026
        elif self.scale[1] < 1:
            self.squish_velocity += 0.026
        if self.squish_velocity > 0:
            self.squish_velocity -= 0.016
        if self.squish_velocity < 0:
            self.squish_velocity += 0.016

        if self.squish_velocity != 0:
            if (abs(self.squish_velocity) < 0.06) and (abs(self.scale[1] - 1) < 0.06):
                self.scale[1] = 1
                self.squish_velocity = 0

        if collisions['down']:
            if self.vel[1] > 6:
                self.squish_velocity = -0.14

    def test_func(self):
        pass
