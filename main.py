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
MAX_ROUNDS = 4

class Decor(Enum):
    LEFT_TORCH = 0
    RIGHT_TORCH = 1
    BIG_TORCH = 2

class State(Enum):
    START_MENU = 0
    PAUSE = 1
    GAME_ON = 2 
    FORCED_PAUSE = 3
    TRANSITION = 4
    TUTORIAL = 5
    DEAD = 6
    WIN = 7 

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
        self.transition = [350, 1,8 ,'closing'] #pos, width  

        self.asset_manager = Asset_Manager()
        self.tile_map = Tile_Map(self)
        self.load_map(self.e_handler.level)
        self.count = [0,0]

        self.fonts = {
            'pixel_0':'data/assets/fonts/pixel_0.ttf',
            'pixel_1': 'data/assets/fonts/pixel_1.ttf',
            'pixel_2': 'data/assets/fonts/pixel_2.ttf',
        }

        load_particle_images('data/assets/images/particles')
        load_projectile_images('data/assets/images/projectiles', [CELL_SIZE//1.5, CELL_SIZE//1.5])
        self.heart_img = get_image('data/assets/images/ui/0.png', [CELL_SIZE, CELL_SIZE])

    def reset(self):
        self.player = None
        self.inputs = [False, False, False, False]
        self.screenshake = 0
        self.particles = []
        self.sparks = []
        self.circles = []
        self.circle_particles = []
        self.enemy_projectiles = []
        self.total_time = 0
        self.e_handler.reset()

        self.load_map(self.e_handler.level)

    def hard_reset(self):
        self.player = None
        self.inputs = [False, False, False, False]
        self.screenshake = 0
        self.particles = []
        self.sparks = []
        self.circles = []
        self.circle_particles = []
        self.enemy_projectiles = []
        self.total_time = 0
        self.e_handler.hard_reset()

        self.load_map(self.e_handler.level)

    def game_on(self): return self.e_handler.state == State.GAME_ON or self.e_handler.state == State.TUTORIAL

    def load_map(self, map_name):
        self.player = Player(self, self.e_handler.starting_pos(), [CELL_SIZE, CELL_SIZE], 'player', True)
        self.tile_map.load_map(map_name)
        self.edges = [inf, n_inf, inf, n_inf]

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
        self.level = 0
        self.level_timer = 0 
        self.text = ''
        self.state = State.TUTORIAL
        self.level_run = false
        self.spawn_rate = [25, 20, 15, 10]
        self.line_spawn_rate = [90, 85, 80, 75]
        self.starting_positions = {
            0: [80, -10],
            1: [80, -10],
            2: [80, -10],
            3: [80,-10],
        }
        self.level_times = [80, 100, 120, 140]
        self.level_start_pos = [120, 240, 200, 240]

    def reset(self): 
        self.level_timer = 0
        self.level_run = false
    
    def hard_reset(self):
        self.level_timer = 0
        self.level_run = false
        self.level = 0 
        self.state = State.TUTORIAL
    
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
                self.base_display.blit( tile[4], (real_pos[0] - self.data.offset[0], real_pos[1] - self.data.offset[1]) )

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
                                            real_pos[0] + random.randrange(-1, 1) + 12,                         # x
                                            real_pos[1] + random.randrange(-1, 1) + 4,                          # y 
                                            'light',                                                            # type
                                            [random.uniform(-.14, .12), random.uniform(-.7, -.4)],              # motion
                                            0.02,                                                               # decay 
                                            3 + random.randint(0, 20) / 10,                                     # start_frame
                                            custom_color=(255, 255, 255)                                        # color
                                        )
                                )

                    elif tile[3] == Decor.RIGHT_TORCH.value:
                        torch_sin = math.sin((tile[0][1] % 100 + 200) / 300 * self.data.total_time * 0.08)

                        blit_center_add( self.base_display, circle_surf(24 + (torch_sin + 3) * 8.5,  (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 4 + (torch_sin + 4) * 0.1)), (real_pos[0] - self.data.offset[0] + 10, real_pos[1] - self.data.offset[1] + 4))
                        blit_center_add( self.base_display, circle_surf(10 + (torch_sin + 3) * 8.5, (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 6 + (torch_sin + 4) * 0.2)),(real_pos[0] - self.data.offset[0] + 10, real_pos[1] - self.data.offset[1] + 4))
                        if random.randint(1, 6) == 1 and self.data.game_on():
                            self.data.particles.append(
                                    Particle(
                                            real_pos[0] + random.randrange(-1, 1) + 4,                         # x
                                            real_pos[1] + random.randrange(-1, 1) + 2,                          # y 
                                            'light',                                                            # type
                                            [random.uniform(-.14, .12), random.uniform(-.6, -.4)],                # motion
                                            0.02,                                                               # decay 
                                            3 + random.randint(0, 20) / 10,                                     # start_frame
                                            custom_color=(255, 255, 255)                                        # color
                                        )
                                )
                    elif tile[3] == Decor.BIG_TORCH.value:
                        torch_sin = math.sin((tile[0][1] % 100 + 200) / 300 * self.data.total_time * 0.08)
                        blit_center_add( self.base_display, circle_surf(24 + (torch_sin + 3) * 8.5,  (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 4 + (torch_sin + 4) * 0.1)), 
                                         ((real_pos[0] - self.data.offset[0]) + 11,  (real_pos[1] - self.data.offset[1]) + 7))
                        blit_center_add( self.base_display, circle_surf(10 + (torch_sin + 3) * 8.5, (28 + (torch_sin + 4) * 0.1, 6 + (torch_sin + 4) * 0.2, 6 + (torch_sin + 4) * 0.2)),
                                         ((real_pos[0] - self.data.offset[0]) + 13,  (real_pos[1] - self.data.offset[1]) + 10))

                        rand_num = random.randint(1, 8)
                        if rand_num == 1 and self.data.game_on():
                            self.data.particles.append( Particle( real_pos[0] + random.randrange(-1, 1) + 3, real_pos[1] + random.randrange(-1, 1) + 7, 'light', [random.uniform(-.14, .12), random.uniform(-.6, -.4)], 0.02, 3 + random.randint(0, 20) / 10, custom_color=(255, 255, 255)) )
                        if rand_num == 2 and self.data.game_on():
                            self.data.particles.append( Particle( real_pos[0] + random.randrange(-1, 1) + 22, real_pos[1] + random.randrange(-1, 1) + 7, 'light', [random.uniform(-.14, .12), random.uniform(-.6, -.4)], 0.02, 3 + random.randint(0, 20) / 10, custom_color=(255, 255, 255)) )

                        #if rand_num == 2 and self.data.game_on():
                            #self.data.particles.append( Particle( real_pos[0] + random.randrange(-1, 1) + 7, real_pos[1] + random.randrange(-1, 1) + 10, 'light', [random.uniform(-.14, .12), random.uniform(-.6, -.4)], 0.02, 3 + random.randint(0, 20) / 10, custom_color=(255, 255, 255)) )
                        #if rand_num == 4 and self.data.game_on():
                        #    self.data.particles.append( Particle( real_pos[0] + random.randrange(-1, 1) + 17, real_pos[1] + random.randrange(-1, 1) + 10, 'light', [random.uniform(-.14, .12), random.uniform(-.6, -.4)], 0.02, 3 + random.randint(0, 20) / 10, custom_color=(255, 255, 255)) )

                    else:
                        print('here')

        if self.data.game_on():
            self.data.player.update(1/60)
        self.data.player.render(self.base_display, self.data.offset)
        player_alive = self.data.player.lives > 0
        if not player_alive:
            self.data.e_handler.change_state(State.DEAD)

        # ------------ UI 
        for i in range(1, self.data.player.lives+1):
            self.base_display.blit(self.data.heart_img,
                                   (WIDTH - 16 - i * CELL_SIZE, 30))

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
        for i,proj in sorted(enumerate(self.data.enemy_projectiles), reverse=true):
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

            dist_from_player = distance(proj[0], self.data.player.pos)
            if dist_from_player > 300:
                self.data.enemy_projectiles.pop(i)
            
            if mask_collision(self.data.player.mask, self.data.player.pos, pg.mask.from_surface(image), proj[0]) \
                and self.data.player.force_scalar == 1 and (self.data.e_handler.state == State.GAME_ON or self.data.e_handler.state == State.TUTORIAL) \
                and self.data.player.state != 'hurt':
                self.data.screenshake = 8
                self.data.enemy_projectiles.pop(i)
                self.data.player.hit()

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


        # [ type, pos, vel, color, size, decay, dur ]
        for p in self.data.circle_particles.copy():

            if p[0] == 'blood' or p[0] == 'fire_ball':
                p[1][0] += p[2][0]
                if self.data.tile_map.tile_collide(p[1]):
                    p[1][0] -= p[2][0]
                    p[2][0] *= -0.7
                p[1][1] += p[2][1]
                if self.data.tile_map.tile_collide((p[1][0], p[1][1])):
                    p[1][1] -= p[2][1]
                    p[2][1] *= -0.7
                p[2][1] += .15  # gravity

            if p[0] == 'fire':
                p[1][0] += p[2][0]
                p[1][1] += p[2][1]

                if p[6] < 0.2: 
                    p[4] += p[5]

                if p[6] < 0.4: p[3] = (0, 128, 255)
                elif p[6] < 0.6: p[3] = (50, 150, 250)
                elif p[6] < 0.9: p[3] = (40, 240, 250)
                elif p[6] < 0.14: p[3] = (160, 246, 255)
                else: p[3] = (210, 250, 255)

                p[6] += p[5]

            if p[0] == 'fire_ball':
                particle = ['fire', p[1].copy(), [random.random() - .5, random.randrange(-4, -1)],
                            (10, 0, 0), random.randrange(3, 4), random.uniform(.12, .18), 0]
                self.data.circle_particles.append(particle)

            p[4] -= p[5]

            if p[4] < 1:
                self.data.circle_particles.remove(p)
            else:
                pg.draw.circle(self.base_display, p[3], (p[1][0] - self.data.offset[0], p[1][1] - self.data.offset[1]), p[4])

        # ---------------------- LEVEL MECHANICS -------------------- #

        if self.data.e_handler.state == State.GAME_ON:
            self.game_mechanics()
        elif self.data.e_handler.state == State.TUTORIAL:
            dashes_text = text_3d(f'DODGES: {self.data.player.dashes}', 10, false, (255, 70, 0), (255, 255, 255), [
                1, 0], font_path=self.data.fonts['pixel_2'], bold=false)
            self.base_display.blit(dashes_text, [
                WIDTH-dashes_text.get_width()-8, 6
            ])
            timer_text = text_3d(f'TIMER: {self.data.e_handler.level_timer} / {self.data.e_handler.level_times[self.data.e_handler.level]}', 10, false, (255, 70, 0), (255, 255, 255), [
                1, 0], font_path=self.data.fonts['pixel_2'], bold=false)
            self.base_display.blit(timer_text, [6,6])

            if self.data.e_handler.level_timer / self.data.e_handler.level_times[self.data.e_handler.level] < .16:
                wad_text = text_3d("USE ' W,A,D ' KEYS TO MOVE" , 10, false, (255, 70, 0), (255, 255,255), [1,0], font_path=self.data.fonts['pixel_1'], bold=false)
                self.base_display.blit(wad_text, [
                    SCREEN_CENTER[0]-(wad_text.get_width()//2), 
                    SCREEN_CENTER[1]-wad_text.get_height()
                    ])
                
            elif self.data.e_handler.level_timer / self.data.e_handler.level_times[self.data.e_handler.level] < .4:
                dodge_text = text_3d("USE ' J ' KEY TO GO THROUGH PROJECTILES" , 12, false, (255, 70, 0), (255, 255,255), [1,0], font_path=self.data.fonts['pixel_1'], bold=false)
                self.base_display.blit(dodge_text, [
                    SCREEN_CENTER[0]-(dodge_text.get_width()//2), 
                    SCREEN_CENTER[1]-dodge_text.get_height()
                    ])
            else:
                # -------------- ADD PROJECTILES ------------- #
                if random.randint(1, self.data.e_handler.spawn_rate[self.data.e_handler.level]) == 1:
                    self.add_dungeon_projectile()
                if self.data.e_handler.level_timer / self.data.e_handler.level_times[self.data.e_handler.level] < .6:
                    surv_text = text_3d("SURVIVE UNTIL TIMER RUNS OUT", 12, false, (255, 70, 0), (255, 255, 255), [
                                        1, 0], font_path=self.data.fonts['pixel_1'], bold=false)
                    self.base_display.blit(surv_text, [
                        SCREEN_CENTER[0]-(surv_text.get_width()//2),
                        SCREEN_CENTER[1]-surv_text.get_height()
                    ])

            if self.data.e_handler.level_timer / self.data.e_handler.level_times[self.data.e_handler.level] > 1:
                self.data.e_handler.change_state(State.TRANSITION)
            self.data.e_handler.level_timer += 1

        elif self.data.e_handler.state == State.PAUSE:
            pass
        elif self.data.e_handler.state == State.START_MENU:

            pg.draw.rect(self.base_display, BLACK, (0,0, WIDTH, HEIGHT))

            tutorial_text_0 = text_surface_1(f'ESCAPE', 28, false, (255, 70, 0), font_path=self.data.fonts['pixel_0'])
            tutorial_text_1 = text_surface_1(f'ESCAPE', 28, false, (255, 205, 0), font_path=self.data.fonts['pixel_0'])
            text_surf = pg.Surface((tutorial_text_0.get_width() + 4, tutorial_text_0.get_height()+10))
            text_surf.set_colorkey((0, 0, 0))
            text_surf.blit(tutorial_text_0, (0,0))
            text_surf.blit(tutorial_text_1, (0, 4))
            self.base_display.blit(text_surf, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()*2))

            pg.draw.rect(self.base_display, (0, 170, 255), (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height(), text_surf.get_width(), 20), 0, 4, 4, 4, 4)
            title_text_0 = text_surface_1(f'the dungeon', 16, false, WHITE, font_path=self.data.fonts['pixel_1'])
            title_text_1 = text_surface_1(f'ESCAPE', 28, false, (255, 205, 0), font_path=self.data.fonts['pixel_0'])
            self.base_display.blit(title_text_0, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()))

        elif self.data.e_handler.state == State.FORCED_PAUSE:
            pass
        elif self.data.e_handler.state == State.TRANSITION:
            player_center = self.data.player.center()
            pg.draw.circle(self.base_display, BLACK, (player_center[0] - self.data.offset[0],player_center[1] - self.data.offset[1]), int(self.data.transition[0]), self.data.transition[1])
            if self.data.transition[3] == 'closing':
                if self.data.transition[1] < self.data.transition[0]:
                    self.data.transition[1] += self.data.transition[2]
                    if self.data.transition[1] >= self.data.transition[0]:
                        self.data.e_handler.level += 1
                        if self.data.e_handler.level == MAX_ROUNDS: 
                            self.data.e_handler.change_state(State.WIN) 
                            return
                        self.data.reset()

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

                        self.data.transition[3] = 'opening'
            else:
                self.data.transition[1] -= self.data.transition[2]
                if self.data.transition[1] < 0:
                    self.data.transition = [350, 1, 4, 'closing']
                    self.data.e_handler.change_state(State.GAME_ON)
        elif self.data.e_handler.state == State.DEAD:

            tutorial_text_0 = text_surface_1(f'GAME OVER', 28, false, (255, 70, 0), font_path=self.data.fonts['pixel_0'])
            tutorial_text_1 = text_surface_1(f'GAME OVER', 28, false, (255, 205, 0), font_path=self.data.fonts['pixel_0'])
            tutorial_text_2 = text_surface_1(f'GAME OVER', 28, false, (255, 255, 255), font_path=self.data.fonts['pixel_0'])
            text_surf = pg.Surface((tutorial_text_0.get_width() + 4, tutorial_text_0.get_height()+10))
            text_surf.set_colorkey((0, 0, 0))
            text_surf.blit(tutorial_text_0, (0,0))
            text_surf.blit(tutorial_text_1, (0, 4))
            self.base_display.blit(text_surf, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()))

            reset_text = text_surface_1(f"press 'r' to reset game", 10, false, (255, 70, 0), font_path=self.data.fonts['pixel_0'])
            reset_text_1 = text_surface_1(f"press 'r' to reset game", 10, false, (255, 255, 255), font_path=self.data.fonts['pixel_0'])
            reset_text_flash = text_surface_1(f"press 'r' to reset game", 10, false, (255, 205, 0), font_path=self.data.fonts['pixel_0'])
            self.base_display.blit(reset_text, (SCREEN_CENTER[0]-reset_text.get_width()//2, SCREEN_CENTER[1]))
            self.base_display.blit(reset_text_1, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
            if math.sin(self.data.total_time) > 0:
                self.base_display.blit(reset_text_flash, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))

        elif self.data.e_handler.state == State.WIN:
            pg.draw.rect(self.base_display, BLACK, (0,0,WIDTH,HEIGHT))
            tutorial_text_0 = text_surface_1(f'YOU WIN', 28, false, (255, 70, 0), font_path=self.data.fonts['pixel_0'])
            tutorial_text_1 = text_surface_1(f'YOU WIN', 28, false, (255, 205, 0), font_path=self.data.fonts['pixel_0'])
            tutorial_text_2 = text_surface_1(f'YOU WIN', 28, false, (255, 255, 255), font_path=self.data.fonts['pixel_0'])
            text_surf = pg.Surface((tutorial_text_0.get_width() + 4, tutorial_text_0.get_height()+10))
            text_surf.set_colorkey((0, 0, 0))
            text_surf.blit(tutorial_text_0, (0,0))
            text_surf.blit(tutorial_text_1, (0, 4))
            if math.sin(self.data.total_time) > 0: text_surf.blit(tutorial_text_2, (0, 4))
            self.base_display.blit(text_surf, (SCREEN_CENTER[0]-text_surf.get_width()//2, SCREEN_CENTER[1]-text_surf.get_height()))

            reset_text = text_surface_1(f"press 'r' to reset game", 10, false, (255, 70, 0), font_path=self.data.fonts['pixel_0'])
            reset_text_1 = text_surface_1(f"press 'r' to reset game", 10, false, (255, 255, 255), font_path=self.data.fonts['pixel_0'])
            reset_text_flash = text_surface_1(f"press 'r' to reset game", 10, false, (255, 205, 0), font_path=self.data.fonts['pixel_0'])
            self.base_display.blit(reset_text, (SCREEN_CENTER[0]-reset_text.get_width()//2, SCREEN_CENTER[1]))
            self.base_display.blit(reset_text_1, (SCREEN_CENTER[0]-(reset_text.get_width()//2)+2, SCREEN_CENTER[1]))
            
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

    def rand_proj(self, case):
        if case == 'top':
            pos = [random.randrange(-10, WIDTH) + self.data.offset[0], self.data.offset[1]-8]
            ang = math.atan2(
                (self.data.player.pos[1] - self.data.offset[1] - (pos[1] - self.data.offset[1]) ), 
                (self.data.player.pos[0] - self.data.offset[0] - (pos[0] - self.data.offset[0]) ) 
                )
        elif case == 'bottom':
            pos = [random.randrange(-10, WIDTH) + self.data.offset[0], HEIGHT + self.data.offset[1]+8]
            ang = math.atan2(
                (self.data.player.pos[1] - self.data.offset[1] - (pos[1] - self.data.offset[1]) ), 
                (self.data.player.pos[0] - self.data.offset[0] - (pos[0] - self.data.offset[0]) ) 
                )
        elif case == 'left':
            pos = [self.data.offset[0]-8, random.randrange(-10, HEIGHT) - self.data.offset[1]]
            ang = math.atan2(
                (self.data.player.pos[1] - self.data.offset[1] - (pos[1] - self.data.offset[1]) ), 
                (self.data.player.pos[0] - self.data.offset[0] - (pos[0] - self.data.offset[0]) ) 
                )
        elif case == 'right':
            pos = [WIDTH+self.data.offset[0]+8, random.randrange(-10, HEIGHT) - self.data.offset[1]]
            ang = math.atan2(
                (self.data.player.pos[1] - self.data.offset[1] - (pos[1] - self.data.offset[1]) ), 
                (self.data.player.pos[0] - self.data.offset[0] - (pos[0] - self.data.offset[0]) ) 
                )
        return pos, ang

    def add_dungeon_projectile(self):
        rand_side = random.choice(['left', 'right', 'bottom', 'top'])
        rand_pos, ang = self.rand_proj(rand_side)
        offset = rand_rad_angle(8)
        self.data.enemy_projectiles.append([[rand_pos[0], rand_pos[1]], [math.cos(ang+offset)*2, math.sin(ang+offset)*2], 0, random.randrange(1, 6)])

        for j in range(3):
            # [ pos, angle, speed, width, decay, speed_decay, length, length_decay, color ]
            offset = rand_rad_angle(6)
            spark = [[rand_pos[0], rand_pos[1]],
                     ang + offset,
                     random.randrange(8, 11),
                     random.randrange(6, 8),
                     0.44,
                     0.92,
                     random.randrange(19, 22),
                     0.96,
                     (20, 6, 6)
                     ]
            self.data.sparks.append(spark)

    def game_mechanics(self):
        if self.data.e_handler.level_run:
            if self.data.e_handler.level_timer == 0:
                self.data.screenshake = 8
                self.random_line_attack()

            if self.data.e_handler.level_timer < self.data.e_handler.level_times[self.data.e_handler.level]:
                
                timer_text = text_3d(f'TIMER: {self.data.e_handler.level_timer} / {self.data.e_handler.level_times[self.data.e_handler.level]}', 12, false, (255, 70, 0), (255, 255, 255), [
                    1, 0], font_path=self.data.fonts['pixel_2'], bold=false)
                self.base_display.blit(timer_text, [ 10, 10])

                dashes_text = text_3d(f'DODGES: {self.data.player.dashes}', 12, false, (255, 70, 0), (255, 255, 255), [1, 0], font_path=self.data.fonts['pixel_2'], bold=false)
                self.base_display.blit(dashes_text, [
                    WIDTH-dashes_text.get_width()-10, 10
                    ])

                if self.data.e_handler.level_timer / self.data.e_handler.level_times[self.data.e_handler.level] < .16:
                    pass
                else:
                    # -------------- ADD PROJECTILES ------------- #
                    proj_spwn = random.randint(1, self.data.e_handler.spawn_rate[self.data.e_handler.level])
                    spwn = random.randint(1, self.data.e_handler.line_spawn_rate[self.data.e_handler.level])
                    if proj_spwn == 1: self.add_dungeon_projectile()
                    if spwn == 1: self.random_line_attack()
            else:
                self.data.e_handler.change_state(State.TRANSITION)
            self.data.e_handler.level_timer += 1

        else:
            if self.data.player.pos[0] > self.data.e_handler.level_start_pos[self.data.e_handler.level]:
                self.data.e_handler.level_run = true

    def random_line_attack(self):
        self.data.screenshake = 8
        line = random.randint(0, 3)
        if line == 0: self.right_line() 
        elif line == 1: self.left_line()
        elif line == 2: self.bottom_line()
        else: self.top_line()

    def right_line(self):
        for i in range(14):
            self.data.enemy_projectiles.append(
                [[WIDTH + self.data.offset[0], (i * 22) + self.data.offset[1]], [-1.8, 0], 0, random.randrange(1, 6)])
            for j in range(3):
                ang = math.pi + random.uniform(-math.pi/8, math.pi/8)
                spark = [[WIDTH + self.data.offset[0], (i * 22) + self.data.offset[1]], ang, random.randrange(
                    8, 11), random.randrange(2, 4), 0.12, 0.9, random.randrange(10, 12), 0.97, (20, 6, 6)]
                self.data.sparks.append(spark) 
    def left_line(self):
        for i in range(14):
            self.data.enemy_projectiles.append([[self.data.offset[0], (i * 22) + self.data.offset[1]], [1.8, 0], 0, random.randrange(1, 6)])
            for j in range(3):
                ang = 0 + random.uniform(-math.pi/8, math.pi/8)
                spark = [[self.data.offset[0], (i * 22) + self.data.offset[1]], ang, random.randrange(
                    8, 11), random.randrange(2, 4), 0.12, 0.9, random.randrange(10, 12), 0.97, (20, 6, 6)]
                self.data.sparks.append(spark)
    def top_line(self):
        for i in range(14):
            self.data.enemy_projectiles.append([[40+self.data.offset[0] +  (i * 22), self.data.offset[1]+10], [0, 1.8], 0, random.randrange(1, 6)])
            for j in range(3):
                ang = math.pi/2 + random.uniform(-math.pi/8, math.pi/8)
                spark = [[40+self.data.offset[0] + (i * 22) , self.data.offset[1]], ang, random.randrange(
                    8, 11), random.randrange(2, 4), 0.12, 0.9, random.randrange(10, 12), 0.97, (20, 6, 6)]
                self.data.sparks.append(spark)

    def bottom_line(self):
        for i in range(14):
            self.data.enemy_projectiles.append([[40+self.data.offset[0] +  (i * 22), self.data.offset[1]+WIDTH-10], [0, -1.8], 0, random.randrange(1, 6)])
            for j in range(3):
                ang = (3*math.pi/2) + random.uniform(-math.pi/8, math.pi/8)
                spark = [[40+self.data.offset[0] + (i * 22) , self.data.offset[1]+WIDTH], ang, random.randrange(
                    8, 11), random.randrange(2, 4), 0.12, 0.9, random.randrange(10, 12), 0.97, (20, 6, 6)]
                self.data.sparks.append(spark)

    def test_func(self):
        # angles: 0 -> right, math.pi/2, -> down , math.pi -> left, (2*math.pi)/2
         #ang = math.atan2((
         #self.mouse_pos[1]//2) - (self.data.player.center()[1] - self.data.offset[1]), 
         #(self.mouse_pos[0]//2) - (self.data.player.center()[0] - self.data.offset[0]) 
         #)
        self.add_dungeon_projectile()
        #angle = random.uniform(-3.14, 3.14)
        #speed = random.random() * 2 + 1
        #particle = ['fire_ball', self.data.player.center(), [math.cos(angle) * speed, math.sin(angle) * speed], (245, 237, 186), 4, .04, -.5]
        #self.data.circle_particles.append(particle)
        
        #ang = random.uniform(-math.pi, math.pi)
        #spark = [self.data.player.center(), ang, random.randrange(8, 11), random.randrange(2, 4), 0.12, 0.9, random.randrange(10, 12), 0.97, (20, 6, 6)]
        #self.data.sparks.append(spark)

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
                if e.key == pg.K_j:
                    self.data.player.dodge(3)
                if e.key == pg.K_r:
                    self.data.hard_reset()
                if e.key == pg.K_k:
                    self.data.player.lives = 0

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
