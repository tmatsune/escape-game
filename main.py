import pygame as pg
import sys 
from enum import Enum
from data.asset_manager import Asset_Manager
from data.tilemap import Tile_Map 
from data.settings import *
from data.entities import * 
from data.particles import * 
from data.utils import * 

false = False
true = True
inf = float('inf')
n_inf = float('-inf')

class Decor(Enum):
    LEFT_TORCH = 0
    RIGHT_TORCH = 1

class State(Enum):
    START_MENU = 0
    PAUSE = 1
    GAME_ON = 2 
    FORCED_PAUSE = 3
    TRANSITION = 4

class Data:
    def __init__(self, app) -> None:
        self.app = app
        self.total_time = 0
        self.offset = [0, 0]
        self.player = None
        self.inputs = [False, False, False, False]
        self.left_clicked = false
        self.screenshake = 0
        self.edges = [inf, n_inf, inf, n_inf]  # x, -x, y, -y
        self.mouse_pos = [0, 0]
        self.e_handler = Event_Handler(self)

        self.enemies = []

        self.particles = []
        self.sparks = []
        self.circles = []
        self.circle_particles = []
        self.enemy_projectiles = []

        self.asset_manager = Asset_Manager()
        self.tile_map = Tile_Map(self)
        self.load_map(self.e_handler.level)
        

        load_particle_images('data/assets/images/particles')
        load_projectile_images('data/assets/images/projectiles', [CELL_SIZE//1.5, CELL_SIZE//1.5])

    def reset(self):
        self.offset = [0, 0]
        self.player = None
        self.particles = []
        self.enemies = []
        self.inputs = [False, False, False, False]
        self.screenshake = 0
        self.sparks = []
        self.effects = []
        self.circles = []

    def game_on(self): return self.e_handler.state == State.GAME_ON

    def load_map(self, map_name):
        self.player = Player(self, self.e_handler.starting_pos(), [CELL_SIZE, CELL_SIZE], 'player', True)
        self.tile_map.load_map(map_name)

        # -------- MAP DATA -------- #
        for pos in self.tile_map.tile_map:
            x = pos[0] * CELL_SIZE
            y = pos[1] * CELL_SIZE
            if x < self.edges[0]:
                self.edges[0] = x
            if x > self.edges[1]:
                self.edges[1] = x + CELL_SIZE
            if y < self.edges[2]:
                self.edges[2] = y
            if y > self.edges[3]:
                self.edges[3] = y + CELL_SIZE

class Event_Handler:
    def __init__(self, data) -> None:
        self.data = data
        self.level = 1
        self.level_timer = 0 
        self.text = ''
        self.state = State.GAME_ON
        self.level_run = false
        self.starting_positions = {
            0: [0, -10],
            1: [150, -10],
            2: [],
            3: [],
        }
        self.level_times = [200, 400, 500, 600]
        self.level_start_pos = [120, 240, 200, 240]
            
    def change_state(self, state):
        if self.state != state:
            self.state = state

    def starting_pos(self):
        return self.starting_positions[self.level]
    

class App:
    def __init__(self) -> None:
        pg.init()
        self.screen: pg.display = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.base_display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        self.dt: float = 0
        self.clock: pg.time = pg.time.Clock()
        
        self.data = Data(self)
        self.inputs = [False, False, False, False]
        self.left_clicked = False
        self.mouse_pos = [0, 0]

        self.inc = [0,0]
        
    def render(self):

        # ----- SETUP ----- #
        self.base_display.fill((20, 0, 16))

        # ---- UPDATE DATA ---- #
        self.data.left_clicked = self.left_clicked
        self.mouse_pos = pg.mouse.get_pos()
        self.data.mouse_pos = self.mouse_pos
        self.data.total_time += 1

        # ------- SCROLL OFFSET ------- #

        self.data.offset[0] += ( ( self.data.player.pos[0] - WIDTH // 2 )  - self.data.offset[0]) / 12
        self.data.offset[1] += ( ( self.data.player.pos[1] - HEIGHT // 2 )  - self.data.offset[1]) / 12
        if self.data.offset[0] < self.data.edges[0]:
            self.data.offset[0] = self.data.edges[0]
        if self.data.offset[0] + WIDTH > self.data.edges[1]:
            self.data.offset[0] = self.data.edges[1] - WIDTH
            
        if self.data.offset[1] < self.data.edges[2]:
            self.data.offset[1] = self.data.edges[2]
        if self.data.offset[1] + HEIGHT > self.data.edges[3]:
            self.data.offset[1] = self.data.edges[3] - HEIGHT

        # --------- BACKGROUND PARTICLES ---------- #


        # --------- MAIN RENDER ACTIONS ---------- #

        layers = self.data.tile_map.get_visible_tiles(self.data.offset)
        for n, layer in layers.items():
            for tile in layer:
                real_pos = [tile[0][0] * CELL_SIZE, tile[0][1] * CELL_SIZE]
                self.base_display.blit(
                    tile[4], 
                    (real_pos[0] - self.data.offset[0], real_pos[1] - self.data.offset[1])
                )
                if tile[2] == 'decor':
                    if tile[3] == Decor.LEFT_TORCH.value:
                        torch_sin = math.sin((tile[0][1] % 100 + 200) / 300 * self.data.total_time * 0.08)
                        #torch_sin = math.sin(1 * self.data.total_time * 0.06)
                        blit_center_add(
                                self.base_display, 
                                circle_surf(24 + (torch_sin + 3) * 8.5, 
                                            (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 4 + (torch_sin + 4) * 0.1)
                                            ), 
                                (real_pos[0] - self.data.offset[0] + 10, real_pos[1] - self.data.offset[1] + 4)
                            )
                        blit_center_add(
                                self.base_display,
                                circle_surf(10 + (torch_sin + 3) * 8.5, 
                                            (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 6 + (torch_sin + 4) * 0.2)
                                            ),
                                (real_pos[0] - self.data.offset[0] + 10, real_pos[1] - self.data.offset[1] + 4)
                            )
                        if random.randint(1, 6) == 1 and self.data.game_on():
                            self.data.particles.append(
                                    Particle(
                                            real_pos[0] + random.randrange(-3, 3) + 10,                         # x
                                            real_pos[1] + random.randrange(-3, 3) + 4,                          # y 
                                            'light',                                                            # type
                                            [random.uniform(-.14, .12), random.uniform(-.7, -.4)],              # motion
                                            0.02,                                                               # decay 
                                            3 + random.randint(0, 20) / 10,                                     # start_frame
                                            custom_color=(255, 255, 255)                                        # color
                                        )
                                )

                    elif tile[3] == Decor.RIGHT_TORCH.value:
                        torch_sin = math.sin((tile[0][1] % 100 + 200) / 300 * self.data.total_time * 0.08)

                        blit_center_add(
                            self.base_display,
                            circle_surf(24 + (torch_sin + 3) * 8.5,
                                        (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 4 + (torch_sin + 4) * 0.1)),
                            (real_pos[0] - self.data.offset[0] + 10,
                             real_pos[1] - self.data.offset[1] + 4)
                        )
                        blit_center_add(
                            self.base_display,
                            circle_surf(10 + (torch_sin + 3) * 8.5,
                                        (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 6 + (torch_sin + 4) * 0.2)),
                            (real_pos[0] - self.data.offset[0] + 10,
                             real_pos[1] - self.data.offset[1] + 4)
                        )
                        if random.randint(1, 6) == 1 and self.data.game_on():
                            self.data.particles.append(
                                    Particle(
                                            real_pos[0] + random.randrange(-3, 3) + 8,                         # x
                                            real_pos[1] + random.randrange(-3, 3) + 2,                          # y 
                                            'light',                                                            # type
                                            [random.uniform(-.14, .12), random.uniform(-.7, -.4)],                # motion
                                            0.02,                                                               # decay 
                                            3 + random.randint(0, 20) / 10,                                     # start_frame
                                            custom_color=(255, 255, 255)                                        # color
                                        )
                                )
                    else:
                        print('here')

        
        if self.data.game_on(): self.data.player.update(1/60)
        self.data.player.render(self.base_display, self.data.offset)

        # ------------------- RENDER PARTICLES -------------------- #

        # ---- PARTICLES
        for particle in self.data.particles.copy():
            alive = particle.update(0.3 * self.dt) if self.data.game_on() else True

            if particle.type == 'light':
                particle.draw(self.base_display, self.data.offset)
                blit_center_add(
                                self.base_display, 
                                    circle_surf(
                                            10, 
                                            (28, 6, 6)),
                                (particle.x - self.data.offset[0], particle.y - self.data.offset[1]))
            if particle.type == 'p':
                particle.draw(self.base_display, self.data.offset)
                blit_center_add(
                                self.base_display, 
                                    circle_surf(
                                            10, 
                                            (28, 26, 6)),
                                (particle.x - self.data.offset[0], particle.y - self.data.offset[1]))    
            if not alive:
                self.data.particles.remove(particle)

        # ------ ENEMY_PROJECTILES 
        # [pos, vel, frame, const]
        for proj in self.data.enemy_projectiles.copy():
            proj[0][0] += proj[1][0]
            proj[0][1] += proj[1][1]
            image = projectile_images['e_projectile'][proj[2]]
            img_rect = image.get_rect(center=(proj[0][0] - self.data.offset[0], proj[0][1] - self.data.offset[1]))
            self.base_display.blit(image, img_rect)
            proj_sin = math.sin((proj[3] % 100 + 100) / 200 * self.data.total_time * 0.4)
            blit_center_add(
                self.base_display,
                circle_surf(
                    10 + (proj_sin + 3) * 2,
                    (28, 6, 6)),
                (proj[0][0] - self.data.offset[0], proj[0][1] - self.data.offset[1]))

        # ------ CIRCLES 
        # [pos, speed, radius, width, decay, speed_decay, color ] 
        for circle in self.data.circles.copy():
            pg.draw.circle(self.base_display, circle[6], 
                           (circle[0][0] - self.data.offset[0], circle[0][1] - self.data.offset[1]), int(circle[2]), int(circle[3]))
            circle[2] += circle[1]
            circle[3] *= circle[4]
            circle[2] -= circle[5]
            if circle[3] < 1:
                self.data.circles.remove(circle)

        if self.left_clicked:
            self.test_func()

        # ------ SPARKS 
        # [ pos, angle, speed, width, decay, speed_decay, length, length_decay, color ]
        for spark in self.data.sparks.copy():
            spark[0][0] += math.cos(spark[1]) * spark[2]
            spark[0][1] += math.sin(spark[1]) * spark[2]
            spark[3] -= spark[4] # sub width by decay 
            spark[2] *= spark[5] # decrase speed by speed decay 
            spark[6] *= spark[7] # decrease lenght by mult of lngth decay 

            if spark[3] <= 0:
                self.data.sparks.remove(spark)
                continue
            points = [
                (spark[0][0] + math.cos(spark[1]) * spark[6], spark[0][1] + math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] + math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] + math.pi / 2) * spark[3]),
                (spark[0][0] - math.cos(spark[1]) * spark[6], spark[0][1] - math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] - math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] - math.pi / 2) * spark[3]),
            ]
            points = [(p[0] - self.data.offset[0], p[1] - self.data.offset[1]) for p in points]
            pg.draw.polygon(self.base_display, (247, 237, 186), points)

        # ---------------------- LEVEL MECHANICS -------------------- #

        if self.data.e_handler.state == State.GAME_ON:
            if self.data.e_handler.level == 0:
                if self.data.e_handler.level_run:
                    pass
                else:
                    if self.data.player.pos[0] > self.data.e_handler.level_start_pos[self.data.e_handler.level]:
                        self.data.e_handler.level = true
            elif self.data.e_handler.level == 1:
                if self.data.e_handler.level_run:
                    if self.data.e_handler.level_timer == 0:
                        self.data.screenshake = 8
                        for i in range(14):
                            self.data.enemy_projectiles.append([ [WIDTH + self.data.offset[0] , (i * 22) + self.data.offset[1]], [-1.8, 0], 0, random.randrange(1, 6)])

                            for j in range(3):
                                ang = math.pi + random.uniform(-math.pi/8, math.pi/8)
                                # [ pos, angle, speed, width, decay, speed_decay, length, length_decay, color ]
                                spark = [[WIDTH + self.data.offset[0], (i * 22) + self.data.offset[1]],
                                         ang, 
                                         random.randrange(8, 11),
                                         random.randrange(2, 4), 
                                         0.12, 
                                         0.9,
                                         random.randrange(10, 12),
                                         0.97, 
                                         (20, 6, 6)
                                         ]
                                self.data.sparks.append(spark)
                    self.data.e_handler.level_timer += 1
                    if self.data.e_handler.level_timer < self.data.e_handler.level_times[self.data.e_handler.level]:
                        timer_text = text_surface(
                            f'Timer: {self.data.e_handler.level_timer} / {self.data.e_handler.level_times[self.data.e_handler.level]}', 10, false, WHITE)
                        self.base_display.blit(timer_text, [10, 10])
                        if self.data.e_handler.level_timer / self.data.e_handler.level_times[self.data.e_handler.level] < .16:
                            tutorial_text = text_surface(
                                f'Survive Until Timer runs out', 10, false, WHITE)
                            self.base_display.blit(tutorial_text, [(WIDTH//2)-tutorial_text.get_width()//2, HEIGHT//2])
                        else:
                            pass
                    else:
                        pass
                else:
                    if self.data.player.pos[0] > self.data.e_handler.level_start_pos[self.data.e_handler.level]:
                        self.data.e_handler.level_run = true 
            elif self.dsta.e_handler.level == 2:
                if self.data.e_handler.level_run:
                    pass
                else:
                    pass
        elif self.data.e_handler.state == State.PAUSE:
            pass
        elif self.data.e_handler.state == State.START_MENU:
            pass
        elif self.data.e_handler.state == State.FORCED_PAUSE:
            pass

        # ------- DISPLAY SCREENS ------- # 
        screenshake_offset = [0, 0]
        if self.data.screenshake > 0:
            self.data.screenshake -= 1
            screenshake_offset[0] = random.randrange(-8, 8)
            screenshake_offset[1] = random.randrange(-8, 8)

        disp_x = screenshake_offset[0] 
        disp_y = screenshake_offset[1] 
        
        self.screen.blit(pg.transform.scale(self.base_display, self.screen.get_size()), (disp_x, disp_y))

        pg.display.flip()
        pg.display.update()

    def add_dungeon_projectile(self):
        pass

    def test_func(self):
        #self.data.circles.append([ [self.data.player.pos[0], self.data.player.pos[1]], 1, 2, 5, .9, .1, (247, 237, 186)])
        ang = math.atan2((self.mouse_pos[1]//2) - (self.data.player.center()[1] - self.data.offset[1]), (self.mouse_pos[0]//2) - (self.data.player.center()[0] - self.data.offset[0]) )
        spark = [self.data.player.center(), ang, random.randrange(8, 11),
                 random.randrange(3, 5), 0.2, 0.9,
                 random.randrange(10, 12), 0.97, (20, 6, 6)]
        self.data.sparks.append(spark)
        

    def update(self):
        self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps()}')
        self.dt = self.clock.tick(FPS)
        self.dt /= 1000

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_1:
                    pg.quit()
                    sys.exit()
                if e.key == pg.K_a:
                    self.data.inputs[0] = True
                if e.key == pg.K_d:
                    self.data.inputs[1] = True
                if e.key == pg.K_w:
                    self.data.inputs[2] = True
                    self.data.player.jump()
                if e.key == pg.K_s:
                    self.data.screenshake = 6

                if e.key == pg.K_p:
                    if self.data.e_handler.state == State.PAUSE:
                        self.data.e_handler.change_state(State.GAME_ON)
                    else:
                        self.data.e_handler.change_state(State.PAUSE)

            if e.type == pg.KEYUP:
                if e.key == pg.K_a:
                    self.data.inputs[0] = False
                if e.key == pg.K_d:
                    self.data.inputs[1] = False
                if e.key == pg.K_w:
                    self.data.inputs[2] = False

            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.left_clicked = True
                if e.button == 3:
                    self.right_clicked = True
            if e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.left_clicked = False
                if e.button == 3:
                    self.right_clicked = False

    def run(self):
        while True:
            self.check_inputs()
            self.render()
            self.update()


if __name__ == '__main__':
    app = App()
    app.run()
