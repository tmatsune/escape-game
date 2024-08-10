import random
import math
from .entity import Entity
from .utils import *
from .settings import CELL_SIZE
false = False
true = True

MAX_JUMPS = 20
MAX_DASHES = 3
FORCE_SCALAR_DECAY = .2
HURT_TIME = 1

class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.vel = [0, 0]
        self.speed = 4
        self.air_time = 0
        self.jumps = 1
        self.lives = 3
        self.dead = false
        self.dashes = MAX_DASHES
        self.dash_bar = 0
        self.hurt_timer = HURT_TIME
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
        self.force_scalar = 1
        self.mask = None
        self.just_hit = false

    def update(self, dt):
        super().update(dt)
        self.inputs = self.data.inputs.copy()
        if (self.inputs[0] or self.inputs[1]) and not self.state == 'hurt':
            self.change_state('run')
        
        if not self.inputs[0] and not self.inputs[1] and not self.inputs[2] and self.air_time == 0 and self.state != 'hurt':
            self.change_state('idle')
        if self.inputs[0]:
            self.flip = true
        elif self.inputs[1]:
            self.flip = false

        if self.state == 'hurt':
            self.hurt_timer -= dt
            if self.hurt_timer < 0:
                self.hurt_timer = HURT_TIME
                self.change_state('idle')

        speed_x = (self.inputs[1] - self.inputs[0])
        if self.force_scalar != 1 and not self.just_hit:
            if self.flip: 
                if speed_x == 0: speed_x = -1
                else: speed_x = -1.1
            else: 
                if speed_x == 0: speed_x = 1
                else: speed_x = 1.1
        elif self.force_scalar != 1:
            self.just_hit = false
            speed_x = 1.2 if self.flip else -1.2

        self.vel[0] = speed_x * self.speed * self.force_scalar
        self.vel[1] = min(14, self.vel[1]+1)
        
        if self.force_scalar > 1:
            self.force_scalar -= FORCE_SCALAR_DECAY
        elif self.force_scalar < 1:
            self.force_scalar = 1

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

        if self.dash_bar < 60:
            self.dash_bar += 1
        elif self.dash_bar >= 60:
            if self.dashes < MAX_DASHES:
                self.dashes += 1
                self.dash_bar = 0 

        if self.lives < 1 and not self.dead:
            self.death_explosion()
            self.dead = true 

    def jump(self):
        if self.jumps > 0:
            self.vel[1] = -10
            self.jumps -= 1

    def dodge(self, scalar):
        if self.dashes > 0:
            self.force_scalar = scalar
            self.dashes -= 1
            self.dash_bar = 0

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
            
        self.mask = pg.mask.from_surface(img)
        if self.lives > 0:
            surf.blit(img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

            if self.state == 'hurt':
                if math.sin(self.data.total_time) > 0:
                    sil = silhouette(img)
                    surf.blit(sil, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

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

    def hit(self):
        self.lives -= 1 
        self.change_state('hurt')
        self.just_hit = true 
        for i in range(5):
            color = random.choice([(190, 5, 55), (200, 30, 30), (180, 10, 10)])
            particle = ['blood', self.center(), [random.random() * 6 - 3, random.random() * 6 - 3], color, random.randrange(3, 5), random.uniform(.02, .06), 0]
            self.data.circle_particles.append(particle)
        for i in range(5):  # right
            fire = ['fire', self.data.player.pos.copy(), [random.uniform(3, 5) * math.cos(0), random.uniform(-1, 1)],
                    (10, 0, 0), random.randrange(5, 7), random.uniform(.12, .18), 0]
            self.data.circle_particles.append(fire)

        for i in range(5):  # right
            fire = ['fire', self.data.player.pos.copy(), [random.uniform(3, 5) * math.cos(math.pi), random.uniform(-1, 1)],
                     (10, 0, 0), random.randrange(5, 7), random.uniform(.12, .18), 0]
            self.data.circle_particles.append(fire)

        self.force_scalar = 2

    def death_explosion(self):
        for i in range(18):
            angle = random.uniform(-3.14, 3.14)
            speed = random.randrange(1, 2)
            particle = ['fire_ball', self.center(), [math.cos(angle) * speed, math.sin(angle) * speed], (245, 237, 186), random.randrange(4, 6), .04, 0]
            self.data.circle_particles.append(particle)
        for i in range(30):
            pos = self.center()
            fire = ['fire', [pos[0] + random.randrange(-2,2), pos[1] + random.randrange(10,20)], [random.uniform(-.5,.5), random.uniform(-1.2, -.5)], (10, 0, 0), random.randrange(8, 11), random.uniform(.12, .16), 0]
            self.data.circle_particles.append(fire)

        for i in range(30):
            color = random.choice([(190, 5, 55), (200, 30, 30), (180, 10, 10)])
            particle = ['blood', self.center(), [random.random() * 6 - 3, random.random() * 6 - 3], color, random.randrange(4, 6), random.uniform(.02, .06), -.2]
            self.data.circle_particles.append(particle)

        for i in range(18):
            ang = random.uniform(-math.pi, math.pi)
            spark = [self.data.player.center(), ang, random.randrange(7, 10), random.randrange(5, 7), random.uniform(.20, .24), 0.9, random.randrange(18, 22), random.uniform(.92, .98), (20, 6, 6)]
            self.data.sparks.append(spark)

