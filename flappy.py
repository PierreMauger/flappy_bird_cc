#!/usr/bin/env python3

import pygame
import random
import math
import os
import time
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

BACKGROUND = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

BIRDS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/", "bird1.png"))),
         pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/", "bird2.png"))),
         pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/", "bird3.png")))]

BASE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/", "base.png")))

PIPE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/", "pipe.png")))

STAT_FONT = pygame.font.SysFont("comicsansms", 30)

class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.bottom = 0
        self.top = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE, False, True)
        self.PIPE_BOTTOM = PIPE
        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x = self.x - self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if (t_point or b_point):
            return True
        return False

class Base:
    VEL = 5
    WIDTH = BASE.get_width()
    IMG = BASE

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
    
    def move(self):
        self.x1 = self.x1 - self.VEL
        self.x2 = self.x2 - self.VEL

        if ((self.x1 + self.WIDTH) < 0):
            self.x1 = self.x2 + self.WIDTH
        if ((self.x2 + self.WIDTH) < 0):
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

class Bird:
    IMGS = BIRDS
    MAX_ROTATION = 35
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
    
    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count = self.tick_count + 1
        d = self.velocity * self.tick_count + 0.5 * 3 * self.tick_count**2

        if (d >= 16):
            d = ((d / abs(d)) * 16)
        if (d <= 0):
            d = d - 2

        self.y = self.y + d
        if (d < 0 or self.y < self.height + 50):
            if (self.tilt < self.MAX_ROTATION):
                self.tilt = self.MAX_ROTATION
        else:
            if (self.tilt > -45):
                self.tilt = self.tilt - self.ROT_VEL

        if (self.y > 685):
            self.y = 685
            self.tilt = 0

    def draw(self, win):
        self.img_count += 1

        if (self.img_count < self.ANIMATION_TIME):
            self.img = self.IMGS[0]
        elif (self.img_count < self.ANIMATION_TIME * 2):
            self.img = self.IMGS[1]
        elif (self.img_count < self.ANIMATION_TIME * 3):
            self.img = self.IMGS[2]
        elif (self.img_count < self.ANIMATION_TIME * 4):
            self.img = self.IMGS[1]
        elif (self.img_count < self.ANIMATION_TIME * 4 + 1):
            self.img = self.IMGS[0]
            self.img_count = 0

        if (self.tilt <= -80):
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

def draw_window(win, bird, base, pipes, score):
    win.blit(BACKGROUND, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    bird.draw(win)
    base.draw(win)
    pygame.display.update()

def main():
    run = True
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0

    while (run):
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
        
        pipe_ind = 0
        bird.move()
        add_pipe = False
        rem = []

        for pipe in pipes:
            if (pipe.collide(bird)):
                main()
            if (not (pipe.passed) and (pipe.x < bird.x)):
                pipe.passed = True
                add_pipe = True
                score += 1
            if (pipe.x + pipe.PIPE_TOP.get_width() < 0):
                rem.append(pipe)
            pipe.move()

        if (add_pipe):
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        base.move()
        draw_window(win, bird, base, pipes, score)

if __name__ == "__main__":
    main()