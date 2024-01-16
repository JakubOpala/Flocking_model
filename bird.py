import numpy as np
import pygame 
import sys
import math
import random

class Bird:
    def __init__(self, x, y, vx, vy, theta, range, world_size, repulsive_force=10, collision_radius=30, matching_coeff = 0.3, cohesion_coeff = 0.3):
        self.x  = x
        self.y  = y
        self.vx = vx
        self.vy = vy
        self.direction = self.dir()
        self.theta = theta # in radians
        self.range = range
        self.neighbors = []
        self.repulsive_force = repulsive_force
        self.collision_radius = collision_radius
        self.matching_coeff = matching_coeff
        self.cohesion_coeff = cohesion_coeff
        self.world_size = world_size
        self.max_force = 1
        self.image = pygame.transform.scale(pygame.image.load('kremuwa.png'), (20, 30))

    def distance(self, bird2):
        dx = abs(self.x - bird2.x)
        dy = abs(self.y - bird2.y)

        # periodic boundary conditions
        dx = min(dx, self.world_size[0] - dx)
        dy = min(dy, self.world_size[1] - dy)

        wrapped_distance = np.sqrt(dx**2 + dy**2)
        return wrapped_distance

    def dir(self):
        return np.array([self.vx, self.vy]) / np.linalg.norm(np.array([self.vx, self.vy]))

    def move(self):
        #self.update_velocity()
        self.x = (self.x + self.vx) % self.world_size[0]
        self.y = (self.y + self.vy) % self.world_size[1]
        self.direction = self.dir()
        
    def draw(self, screen,hunt):
        
        direction_angle = math.atan2(self.direction[1], self.direction[0])

        if hunt:
            
            # Rotate the image
            rotated_image = pygame.transform.rotate(self.image, -direction_angle)

            rect = rotated_image.get_rect(center=(self.x, self.y))

            # Blit the rotated image onto the screen
            screen.blit(rotated_image, rect.topleft)
        else:
            arrow_points = [
                (0, -20),
                (5, 0),
                (-5, 0)
            ]

            rotated_arrow = []
            for point in arrow_points:
                rotated_x = point[0] * math.cos(direction_angle+math.pi/2) - point[1] * math.sin(direction_angle+math.pi/2)
                rotated_y = point[0] * math.sin(direction_angle+math.pi/2) + point[1] * math.cos(direction_angle+math.pi/2)
                rotated_arrow.append((self.x + rotated_x, self.y + rotated_y))

            pygame.draw.polygon(screen, (200,50,50), rotated_arrow)
        



    def bird_in_view_range(self, bird2):

        #relative_vector = np.array([self.x - bird2.x,self.y - bird2.y]) / np.linalg.norm(np.array([self.x - bird2.x,self.y - bird2.y]))
        relative_vector = np.array([bird2.x - self.x,bird2.y - self.y], dtype=float)
        mag = np.linalg.norm(relative_vector)

        if  mag == 0:
            return True
        
        relative_vector /= mag
        dist = self.distance(bird2)

        if dist < self.range:
            # Calculate the angle between the direction vector and the relative vector
            angle = math.acos(np.dot(self.direction, relative_vector))# / (dist + 1e-8))  
            # Check if the angle is within the field of view
            return angle <= self.theta / 2.0
        
        return False

    def get_neighbors(self, birds):

        self.neighbors = []
        for neighbor in birds:
            if self.bird_in_view_range(neighbor) and neighbor != self:
                self.neighbors.append(neighbor)

    def update_velocity(self):
        
        steering = np.zeros(2)

        if len(self.neighbors) > 0:
            avoidance = self.avoid_collisions() * self.repulsive_force
            alignment = self.velocity_matching()  * self.matching_coeff
            cohesion  = self.cohesion() * self.cohesion_coeff    
            steering += avoidance + alignment + cohesion
        
        #new_velocity = np.array([self.vx, self.vy]) + 0.2 * steering

        self.vx +=  steering[0]    #new_velocity[0]    
        self.vy +=  steering[1]    #new_velocity[1]  

        velocity = np.sqrt(self.vx**2+self.vy**2)

        self.vx /=  velocity/5   #new_velocity[0]    
        self.vy /=  velocity/5
        self.direction = self.dir()

    def avoid_collisions(self):

        avoidance_vector = np.zeros(2)

        for bird2 in self.neighbors:
            distance = self.distance(bird2)
            
            if distance < self.collision_radius:
                #relative_vector = np.array([bird2.x - self.x,bird2.y - self.y]) / np.linalg.norm(np.array([bird2.x - self.x,bird2.y - self.y]))
                # avoidance_vector +=  (1.0 / distance) * relative_vector
                avoidance_vector -= np.array([bird2.x - self.x,bird2.y - self.y]) 

        # Update velocity to avoid collisions
        #self.vx += -avoidance_vector[1]
        #self.vy += avoidance_vector[0]
        avoidance_vector = np.array([avoidance_vector[1]* random.choice([-1, 1]),avoidance_vector[0]* random.choice([-1, 1])])
        avoidance_vector = self.clamp_force(avoidance_vector)
        return avoidance_vector
    
    def clamp_force(self, force):
            
        magnitude = np.linalg.norm(force)

        if 0 < magnitude > self.max_force:
            force = force * (self.max_force/magnitude)

        return force

    def velocity_matching(self):

        velocity_match = np.zeros(2)

        for bird2 in self.neighbors:
            velocity_match[0] += bird2.vx #- self.vx
            velocity_match[1] += bird2.vy #- self.vy
        
        #velocity_match = self.matching_coeff * velocity_match / max(1,len(self.neighbors)) 
        #self.vx += velocity_match[0]
        #self.vy += velocity_match[1]
            
        velocity_match /= max(1, len(self.neighbors))
        velocity_match -= np.array([self.vx,self.vy])
        velocity_match = self.clamp_force(velocity_match)
        return velocity_match / 8
    
        # Blend the velocities to avoid sudden drops
        #self.vx = (1 - self.matching_coeff) * self.vx + self.matching_coeff * velocity_match[0]
        #self.vy = (1 - self.matching_coeff) * self.vy + self.matching_coeff * velocity_match[1]

    def cohesion(self):

        flock_center = np.zeros(2)

        for neighbor in self.neighbors:
            flock_center[0] += neighbor.x 
            flock_center[1] += neighbor.y 

        flock_center /= len(self.neighbors)
        x_dir = flock_center[0] - self.x
        y_dir = flock_center[1] - self.y

        #self.vx += x_dir * self.cohesion_coeff
        #self.vy += y_dir * self.cohesion_coeff
        return self.clamp_force(np.array([x_dir,y_dir])) / 100
        
