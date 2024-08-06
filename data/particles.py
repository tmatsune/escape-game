import pygame as pg 
import random, os
from .utils import * 

global colokey_e
colorkey_e = (0, 0, 0)
global particle_images
particle_images = {}

def circle_surf(size, color):
    surf = pg.Surface((size * 2 + 2, size * 2 + 2))
    pg.draw.circle(surf, color, (size + 1, size + 1), size)
    return surf

def blit_center(target_surf, surf, loc):
    target_surf.blit(surf, (loc[0] - surf.get_width() // 2, loc[1] - surf.get_height() // 2))

def blit_center_add(target_surf, surf, loc):
    target_surf.blit(surf, (loc[0] - surf.get_width() // 2, loc[1] - surf.get_height() // 2), special_flags=pg.BLEND_RGBA_ADD)

def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3

def load_particle_images(path):
    global particle_images, colorkey_e
    file_list = os.listdir(path)
    for folder in file_list:
        #try:
        img_list = os.listdir(path + '/' + folder)
        img_list = particle_file_sort(img_list)
        images = []
        for img in img_list:
            image = pg.image.load(path + '/' + folder + '/' + img).convert()
            w = image.get_width()
            h = image.get_height()
            image = pg.transform.scale(image, (w * 1.5, h * 1.5))
            images.append(image)
        for img in images:
            img.set_colorkey(colorkey_e)
            
        particle_images[folder] = images.copy()
        #except:
        #    pass

def load_stars_images(path):
    star_images = []
    file_list = os.listdir(path)
    for folder in file_list:
        img_list = os.listdir(path + '/' + folder)
        images = []
        for img in img_list:
            image = pg.image.load(path + '/' + folder + '/' + img).convert()
            w = image.get_width()
            h = image.get_height()
            image = pg.transform.scale(image, (w // 3, h // 3))
            images.append(image)
        star_images += images
    return star_images

class Particle(object):
    def __init__(self,x,y,particle_type,motion,decay_rate,start_frame,custom_color=None, physics=False):
        self.x = x
        self.y = y
        self.type = particle_type
        self.motion = motion.copy()
        self.color = custom_color
        self.frame = start_frame
        self.physics = physics
        self.orig_motion = self.motion
        self.temp_motion = [0, 0]
        self.decay_rate = decay_rate
        self.time_left = len(particle_images[self.type]) + 1 - self.frame
        self.render = True
        self.random_constant = random.randint(20, 30) / 30

    def draw(self,surface, scroll):
        global particle_images
        if self.render:
            if self.frame > len(particle_images[self.type]):
                self.frame = len(particle_images[self.type])
            if self.color == None:
                blit_center(surface,particle_images[self.type][int(self.frame)],(self.x-scroll[0],self.y-scroll[1]))
            else:
                new_surf = swap_color(particle_images[self.type][int(self.frame)], (255,255,255), self.color)
                blit_center(surface, new_surf, (self.x-scroll[0],self.y-scroll[1]))

    def update(self, dt):
        self.frame += self.decay_rate 
        self.time_left = len(particle_images[self.type]) + 1 - self.frame
        running = True
        self.render = True
        if self.frame >= len(particle_images[self.type]):
            self.render = False
            if self.frame >= len(particle_images[self.type]) + 1:
                running = False
            running = False
        if not self.physics:
            self.x += (self.temp_motion[0] + self.motion[0]) 
            self.y += (self.temp_motion[1] + self.motion[1])
        self.temp_motion = [0, 0]
        return running
    




'''
class Particle:
    def __init__(self, pos, particle_type, vel, decay, frame, color=None, glow_color=None) -> None:
        self.pos = pos.copy() 
        self.type = particle_type
        self.vel = vel 
        self.decay = decay 
        self.frame = frame 
        self.color = color 
        self.random_constant = random.randint(20, 30) / 30

    def render(self, surf, offset):
        global particle_images
        if self.render:
            if self.frame > len(particle_images[self.type]):
                self.frame = len(particle_images[self.type])
            if self.color == None:
                blit_center(surf,particle_images[self.type][int(self.frame)],(self.pos[0]-offset[0],self.pos[1]-offset[1]))
            else:
                new_surf = swap_color(particle_images[self.type][int(self.frame)],(255,255,255),self.color)
                blit_center(surf,  new_surf, (self.pos[0]-offset[0],self.pos[1]-offset[1]))

    def update(self, dt):
        self.frame += self.decay_rate * dt
        self.time_left = len(particle_images[self.type]) + 1 - self.frame

        done = false

        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

        if self.frame >= len(particle_images[self.type]):
            done = true 

        return done 
'''

# other useful functions

def swap_color(img,old_c,new_c):
    global colorkey_e
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    surf.set_colorkey(colorkey_e)
    return surf

def shaded_block(width, height):
        fog_surf = pg.Surface((180, 180))
        pg.draw.rect(fog_surf, (8, 3, 2), (0, 0, 180, 180))
        fog_surf.set_alpha(150)
        fog_surf.set_colorkey((0, 0, 0))
        return fog_surf
'''
def background_effect_test():
    particle[0][1] += particle[1][1]
    fog_surf = pg.Surface((particle[2][0], particle[2][1]))
    pg.draw.rect(fog_surf, particle[3], (0, 0, particle[2][0], particle[2][1]))
    fog_surf.set_alpha(190)
    fog_surf.set_colorkey((0, 0, 0))
    self.base_display.blit(fog_surf, (particle[0][0] % WIDTH, particle[0][1]))
    particle[2][1] -= particle[4]
    if particle[2][1] <= 0:
    self.data.background_particles.remove(particle)
'''