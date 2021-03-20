import pygame
import os
import math
import sys
import random
import neat

screen_width = 1500
screen_height = 800
generation = 0

car_speed = 12
grass_speed = 8

btfo_purple = (146, 15, 95, 255)
grass_green = (85, 162, 69, 255)
road_grey = (100, 106, 97, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

class Car:
    def __init__(self):
        self.surface = pygame.image.load("car.png")
        self.map = pygame.image.load("map.png")
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.pos = [700, 650]
        self.angle = 0
        self.speed = 10
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.btfo_radars = []
        self.roadedge_radars = []
        self.btfo_radars_for_draw = []
        self.roadedge_radars_for_draw = []
        self.four_points = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.is_alive = True
        self.is_on_grass = False
        self.goal = False
        self.distance = 0
        self.time_spent = 0

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)
        self.draw_radars(screen)

    def draw_radars(self, screen):
        for r in self.btfo_radars:
            pos, dist = r
            print("dist: ", dist)
            pygame.draw.line(screen, green, self.center, pos, 1)
            pygame.draw.circle(screen, green, pos, 5)
        for r in self.roadedge_radars:
            pos, dist = r
            print("dist: ", dist)
            pygame.draw.line(screen, blue, self.center, pos, 1)
            pygame.draw.circle(screen, blue, pos, 5)

    def check_collision(self, map, colour):
        self.is_alive = True
        for p in self.four_points:
            if self.map.get_at((int(p[0]), int(p[1]))) == colour:
                self.is_alive = False
                break

    def check_is_on_grass(self):
        self.is_on_grass = False
        points_on_grass = 0
        for p in self.four_points:
            if self.map.get_at((int(p[0]), int(p[1]))) == grass_green:
                points_on_grass += 1
        if points_on_grass >= 2:
            self.is_on_grass = True
    
    def check_btfo_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not map.get_at((x, y)) == btfo_purple and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.btfo_radars.append([(x, y), dist])
    
    def check_roadedge_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        colour = grass_green
        try:
            if map.get_at((x, y)) == grass_green:
                colour = road_grey
        except IndexError: # catch the error
            pass
        try:
            while not map.get_at((x, y)) == colour and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y       = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.roadedge_radars.append([(x, y), dist])

    def update(self, map):
        #check speed
        self.check_is_on_grass()
        self.speed = car_speed
        if self.is_on_grass:
            self.speed = grass_speed

        #check position
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        # if self.pos[0] < 20:
        #     self.pos[0] = 20
        # elif self.pos[0] > screen_width - 120:
        #     self.pos[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        # if self.pos[1] < 20:
        #     self.pos[1] = 20
        # elif self.pos[1] > screen_height - 120:
        #     self.pos[1] = screen_height - 120

        # caculate 4 collision points
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        len = 40
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(map, btfo_purple)
        self.btfo_radars.clear()
        self.roadedge_radars.clear()
        for d in range(-90, 120, 45):
            self.check_btfo_radar(d, map)
            self.check_roadedge_radar(d, map)

    def get_data(self):
        btfo_radars = self.btfo_radars
        roadedge_radars = self.roadedge_radars
        ret = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, r in enumerate(btfo_radars + roadedge_radars):
            ret[i] = int(r[1] / 30)
        return ret

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        return self.distance / 50.0

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

def run_car(genomes, config):

    # Init NEAT
    nets = []
    cars = []

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        # Init my cars
        cars.append(Car())

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)
    map = pygame.image.load('map.png')


    # Main loop
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Input my data and get result from network
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            action = output.index(max(output))
            if action == 0:
                car.angle += 10
            elif action == 1:
                car.angle += 5
            elif action == 2:
                pass
            elif action == 3:
                car.angle -= 5
            elif action == 4:
                car.angle -= 10

        # Update car and fitness
        remain_cars = 0
        for i, car in enumerate(cars):
            if car.get_alive():
                remain_cars += 1
                car.update(map)
                genomes[i][1].fitness += car.get_reward()

        car.check_is_on_grass()
        car.speed = 12
        if car.is_on_grass:
            car.speed = 5

        # check
        if remain_cars == 0:
            break

        # Drawing
        screen.blit(map, (0, 0))
        for car in cars:
            if car.get_alive():
                car.draw(screen)

        text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        screen.blit(text, text_rect)

        text = font.render("remain cars : " + str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)

if __name__ == "__main__":
    # Set configuration file
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Create core evolution algorithm class
    p = neat.Population(config)

    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    p.run(run_car, 1000)
