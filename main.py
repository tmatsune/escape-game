import pygame as pg
import sys 
from enum import Enum
from data.settings import *
from data.asset_manager import Asset_Manager
from data.tilemap import Tile_Map 
from data.entities import * 
from data.particles import * 

false = False
true = True
inf = float('inf')
n_inf = float('-inf')
STAR_SCROLL = .2
class Decor(Enum):
    LEFT_TORCH = 0
    RIGHT_TORCH = 1

class Data:
    def __init__(self, app) -> None:
        self.app = app
        self.total_time = 0
        self.offset = [0, 0]
        self.player = None
        self.inputs = [False, False, False, False]
        self.left_clicked = false
        self.screenshake = 0
        self.enemies = []
        self.background_objects = []

        self.particles = []
        self.sparks = []
        self.effects = []
        self.circles = []
        self.circle_particles = []
        self.projectiles = []
        self.bullets = []
        self.background_particles = []

        self.edges = [inf, n_inf, inf, n_inf]  # x, -x, y, -y
        self.asset_manager = Asset_Manager()
        self.tile_map = Tile_Map(self)
        self.load_map(1)
        self.mouse_pos = [0, 0]

        load_particle_images('data/assets/images/particles')
        self.stars_images = load_stars_images('data/assets/images/anim/star')

        for i in range(20):
            # pos, frame, rate, 
            self.background_particles.append([ 
                [random.randrange(50, WIDTH), random.randrange(0, HEIGHT)], 
                random.randrange(0, 2), 
                random.uniform(.1, .2)
                ] )

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

    def load_map(self, map_name):
        self.player = Player(self, [180, 60], [CELL_SIZE, CELL_SIZE], 'player', True)
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

class App:
    def __init__(self) -> None:
        pg.init()
        self.screen: pg.display = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.base_display: pg.Surface = pg.Surface((WIDTH, HEIGHT))
        #self.base_display = self.display.copy()
        #self.display.set_colorkey((0, 0, 0))
        self.dt: float = 0
        self.clock: pg.time = pg.time.Clock()
        
        self.data = Data(self)
        self.inputs = [False, False, False, False]
        self.left_clicked = False
        self.mouse_pos = [0, 0]
        
    def render(self):

        # ----- SETUP ----- #
        self.base_display.fill((20, 0, 16))
        #self.display.fill((0, 0, 0))

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

        # # pos, frame, rate,
        '''
        for particle in self.data.background_particles.copy():
            self.base_display.blit(self.data.stars_images[int(particle[1])], (
                particle[0][0] - self.data.offset[0]*STAR_SCROLL, particle[0][1]-self.data.offset[1]*STAR_SCROLL))
            particle[1] += particle[2]
            if particle[1] > 3:
                particle[1] = 0
        '''

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
                        if random.randint(1, 6) == 1:
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
                        if random.randint(1, 6) == 1:
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


        self.data.player.update(1/60)
        self.data.player.render(self.base_display, self.data.offset)

        # -------------- RENDER PARTICLES -------------- #

        #if random.random() < .05:
            #self.data.particles.append(Particle(100 + random.randrange(-6, 6), 100 + random.randrange(-6, 6), 'light', [random.randint(0, 10) / 10 - 0.5, random.randint(0, 10) / 10 - 2], 0.1, 3 + random.randint(0, 20) / 10, custom_color=(255, 255, 255)))

        for particle in self.data.particles.copy():
            alive = particle.update(0.3 * self.dt)
            '''
            if particle.type == 'p':
                particle.draw(self.base_display, [0, 0])
                blit_center_add(
                    self.base_display,
                    circle_surf(
                        14 + particle.time_left * 2 * (math.sin(particle.random_constant * self.data.total_time * 0.1) + 3),
                        (36 + particle.time_left * 0.6, 12 + particle.time_left * 0.2, 12 + particle.time_left * 0.4)
                    ),
                    (particle.x - 0, particle.y - 0))            
            '''

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
            #n_img = swap_color(img[0], (255, 255, 255), (0, 0, 255))
            #self.base_display.blit(n_img, (100, 100))

        # --------- BLIT MASK --------- #


        # ------- DISPLAY SCREENS ------- # 
        screenshake_offset = [0, 0]
        if self.data.screenshake > 0:
            self.data.screenshake -= 1
            screenshake_offset[0] = random.random() * 9 - 4
            screenshake_offset[1] = random.random() * 9 - 4



        disp_x = screenshake_offset[0]
        disp_y = screenshake_offset[1]

        size = self.screen.get_size()
        size_x = size[0]
        size_y = size[1]
        zoom_size = (size_x, size_y)

        self.screen.blit(pg.transform.scale(self.base_display, zoom_size), (disp_x, disp_y))

        pg.display.flip()
        pg.display.update()

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
