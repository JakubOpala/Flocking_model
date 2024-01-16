import pygame
from pygame.transform import scale
import qiskit
import os
import time
import numpy as np
import math
from PIL import Image
import easygui
from button import Button
from bird import Bird
from slider import Slider
from predator import Predator
from sympy import Abs
import random

pygame.init()


WIDTH, HEIGHT = 600,600
SIDE_MARGIN, LOWER_MARGIN = 200, 100
WIN = pygame.display.set_mode((WIDTH+SIDE_MARGIN, HEIGHT+LOWER_MARGIN))
pygame.display.set_caption("GAME")

#initializing window
#win_pos_x = 500 #screen_info.current_w / 2 - WIDTH / 2
#win_pos_y = 500 #screen_info.current_h / 2 - HEIGHT / 2
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (win_pos_x,win_pos_y)
os.environ['SDL_VIDEO_CENTERED'] = '1'

WHITE = (255, 255, 255)
GREEN = (160, 180, 100)
BLACK = (0,0,0)
FPS = 60    


# BUTTONS ==========================================================================================

button_list = []

#start_button = Button(WIDTH + (SIDE_MARGIN - 150) // 2, HEIGHT - 120, 150, 50, "START", 1)
#load_button = Button(WIDTH + (SIDE_MARGIN - 150) // 2, HEIGHT - 60, 150, 50, "RUN", 1)

start_button = Button(100, HEIGHT + 20, 150, 50, "START", 1)
release_button = Button(300, HEIGHT + 20, 150, 50, "RELEASE", 1)

# Add buttons to the list
button_list.extend([start_button, release_button])#], load_button])

# SLIDERS ==========================================================================================

slider_list = []

nbirds_slider   = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 60, 150, 1, 200, 50, 'N_BIRDS')
cohesion_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 120, 150, -5, 100, 10, 'COHESION')
avoidance_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 180, 150, -5, 100, 2, 'AVOIDANCE')
vel_matching_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 240, 150, -5, 100, 8, 'MATCHING')
theta_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 300, 150, 0, 2.31*math.pi, math.pi , 'THETA')
col_radius_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 360, 150, 0, 100, 35, 'COLISION_RADIUS')
vmin_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 420, 150, 0, 5, 1, 'VMIN')
vmax_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 480, 150, 0, 5, 1, 'VMAX')



slider_list.extend([nbirds_slider,cohesion_slider,avoidance_slider,vel_matching_slider,theta_slider,col_radius_slider,vmin_slider,vmax_slider])

# BIRDS ==========================================================================================

'''
bird_list = []

# Create 100 bird instances with random positions and velocities
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    vx = random.uniform(1, 2) * random.choice([-1, 1]) 
    vy = random.uniform(1, 2) * random.choice([-1, 1])
    theta = 0.5 * math.pi #random.uniform(0, 2 * math.pi)  # Random angle between 0 and 2*pi

    bird = Bird(x, y, vx, vy, theta, 20, [WIDTH,HEIGHT])
    bird_list.append(bird)

'''


def generate_birds(n_birds, coherence, avoidance, velocity_matching, r, theta, min_v, max_v, collision_radius):

    bird_list = []

    for _ in range(n_birds):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        vx = random.uniform(min_v, max_v) * random.choice([-1, 1]) 
        vy = random.uniform(min_v, max_v) * random.choice([-1, 1])
        #theta = 0.5 * math.pi #random.uniform(0, 2 * math.pi)  # Random angle between 0 and 2*pi

        bird = Bird(x, y, vx, vy, theta, r, [WIDTH,HEIGHT], avoidance, collision_radius, velocity_matching, coherence)
        bird_list.append(bird)
            
    return bird_list

# MAIN LOOP ========================================================================================

def main():
    #hero = pygame.Rect(x_cord, y_cord, hero_width, hero_height)
    bird_list = []
    clock = pygame.time.Clock()
    time = 10
    run = True
    sliding = False
    hunt = False

    n_birds, cohesion, avoidance, vel_matching = 100, 1, 1, 1
    r, theta, vmin, vmax, collision_radius = 50, math.pi / 2, 1, 3, 30


    while run:
        clock.tick(FPS)
        time = time + 1 #% FPS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for slider in slider_list:
                    if slider.handle_rect.collidepoint(event.pos):
                        sliding = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                sliding = False

            if event.type == pygame.MOUSEMOTION and sliding:
                for slider in slider_list:
                    if slider.handle_rect.collidepoint(event.pos):
                        slider.handle_rect.x = max(slider.rect.x, min(event.pos[0] -10, slider.rect.right - slider.handle_rect.width))
                        slider.update_value()

                        #del slider_list[6:8]
                        #vmin_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 420, 150, 0, vmax, vmin, 'VMIN')
                        #vmax_slider = Slider(WIDTH + (SIDE_MARGIN - 150) // 2, 480, 150, vmin, 5, vmax, 'VMAX')
                        #slider_list.extend([vmin_slider, vmax_slider])

            if button_list[0].check_click(event):
                bird_list = generate_birds(n_birds, cohesion, avoidance, vel_matching, r, theta, vmin, vmax, collision_radius)
            
            

            if button_list[1].check_click(event):
                if not hunt:
                    predator = Predator([WIDTH,HEIGHT])
                    button_list[1].text = 'PEACE'
                    hunt = True
                else:
                    hunt = False
                    button_list[1].text = 'RELEASE'

        
        
        #GET VALUES FROM SLIDERS:
        n_birds = int(slider_list[0].value)
        cohesion = slider_list[1].value
        avoidance = slider_list[2].value
        vel_matching = slider_list[3].value
        theta = slider_list[4].value
        collision_radius = slider_list[5].value
        vmin = min(slider_list[7].value,slider_list[6].value)
        vmax = max(slider_list[7].value,slider_list[6].value)
        

        

        #RESET SCREEN
        WIN.fill(BLACK)

        

        #birds draw and movement
        if len(bird_list) > 0:
            
            for bird in bird_list:
                bird.draw(WIN,hunt)
                bird.get_neighbors(bird_list)
                bird.update_velocity()
        
            for bird in bird_list:
                bird.move()

        keys_pressed = pygame.key.get_pressed()

        if hunt:

            predator.move(keys_pressed)
            predator.draw(WIN)
            bird_list = predator.eat(bird_list)


        # MARGINS
        pygame.draw.rect(WIN, (150, 150, 150), (WIDTH, 0, SIDE_MARGIN, HEIGHT + LOWER_MARGIN))
        pygame.draw.rect(WIN, (150, 150, 150), (0, HEIGHT, WIDTH, LOWER_MARGIN))

        for button in button_list:
            button.draw(WIN)

        for slider in slider_list:
            slider.draw(WIN)

        pygame.display.update()

        
    pygame.quit()

if __name__ == "__main__":
    main()