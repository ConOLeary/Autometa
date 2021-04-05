import pygame
import os
import math
import sys
import random
import neat
import CheckPointer
import seaborn
import matplotlib.pyplot as plt
import numpy as np; np.random.seed(0)
from PIL import Image, ImageEnhance


screen_width = 1500
screen_height = 800
generation = 0
max_gen_time = 30000
max_heatmap_time = 5000
max_gen_laps = 1
max_heatmap_laps = 1
gen_start_time = 0
checkpoint_diameter = 80

car_speed = 12
grass_speed = 8

btfo_purple = (146, 15, 95, 255)
grass_green = (85, 162, 69, 255)
road_grey = (100, 106, 97, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

class Map:
    def __init__(self, map_no, cars):
        self.cars = cars
        self.img = pygame.image.load("../map"+str(map_no)+".png")
        self.checkpoints = [[0, 0]]
        self.checkpoints_growth = [0] # Lengths the diameters of checkpoints should deviate from standard
        self.starting_pos = [0, 0]
        self.starting_angl = 0
        if map_no == "1":
            self.checkpoints = [[1100, 690], [1100, 85], [520, 270], [800, 520], [650, 690]]
            self.starting_pos = [700, 650]
            self.starting_angl = 0
        if map_no == "2":
            self.checkpoints = [[180, 705], [1330, 400], [200, 175], [90, 470]]
            self.checkpoints_growth = [0, 65, 80, 0]
            self.starting_pos = [700, 650]
            self.starting_angl = -90
        

class Car:
    def __init__(self, map_no, starting_angle):
        self.surface = pygame.image.load("../car.png")
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.pos = [0, 0]
        if map_no == '1':
            self.pos = [700, 650]
        elif map_no == '2':
            self.pos = [50, 550]
        self.angle = starting_angle
        self.speed = 10
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.btfo_radars = []
        self.roadedge_radars = []
        self.btfo_radars_for_draw = []
        self.roadedge_radars_for_draw = []
        self.four_points = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.is_alive = True
        self.is_on_grass = False
        self.is_in_cp = False
        self.current_check = 0
        self.total_checks = 0
        self.prev_distance = 0
        self.cur_distance = 0
        self.goal = False
        self.goal = False
        self.laps_done = 0
        self.distance = 0
        self.time_spent = 0

    def get_distance(self, p1, p2):
	    return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)
        self.draw_radars(screen)

    def draw_radars(self, screen):
        for r in self.btfo_radars:
            pos, dist = r
            pygame.draw.line(screen, green, self.center, pos, 1)
            pygame.draw.circle(screen, green, pos, 5)
        for r in self.roadedge_radars:
            pos, dist = r
            pygame.draw.line(screen, blue, self.center, pos, 1)
            pygame.draw.circle(screen, blue, pos, 5)

    def check_collision(self, map, colour):
        self.is_alive = True
        for p in self.four_points:
            try:
                if map.img.get_at((int(p[0]), int(p[1]))) == colour:
                    self.is_alive = False
                    break
            except IndexError:
                pass

    def check_is_on_grass(self, map):
        self.is_on_grass = False
        points_on_grass = 0
        for p in self.four_points:
            try:
                if map.img.get_at((int(p[0]), int(p[1]))) == grass_green:
                    points_on_grass += 1
            except IndexError:
                pass
        if points_on_grass >= 2:
            self.is_on_grass = True
    
    def check_checkpoint(self, map):
        p = map.checkpoints[self.current_check]
        self.prev_distance = self.cur_distance
        dist = self.get_distance(p, self.center)
        if dist < checkpoint_diameter + map.checkpoints_growth[self.current_check]:
            if not self.is_in_cp:
                self.current_check += 1
                self.total_checks += 1
                self.current_check %= len(map.checkpoints)
                if self.current_check == map.checkpoints:
                    self.laps_done += 1
                    if self.laps_done > current_max_lap:
                        current_max_lap = self.laps_done
                self.prev_distance = 9999
                self.time_spent = 0
                self.is_in_cp = True
        else:
            self.is_in_cp = False
        self.cur_distance = dist

    def check_btfo_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        try:
            while not map.img.get_at((x, y)) == btfo_purple and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.btfo_radars.append([(x, y), dist])
    
    def check_roadedge_radar(self, degree, map):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        colour = grass_green
        try:
            if map.img.get_at((x, y)) == grass_green:
                colour = road_grey
        except IndexError: # catch the error
            pass
        try:
            while not map.img.get_at((x, y)) == colour and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.roadedge_radars.append([(x, y), dist])

    def update(self, map):
        #check speed
        self.check_is_on_grass(map)
        self.speed = car_speed
        if self.is_on_grass:
            self.speed = grass_speed

        #check position
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed

        # caculate 4 collision points
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        len = 40
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(map, btfo_purple)
        self.check_checkpoint(map)
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
        #print("(", self.distance, " / 1000.0) * (", self.total_checks, " * ", self.total_checks, " * 1000 / ", get_generation_duration(), " * 0.1)")
        #return (self.distance / 1000.0) * (self.total_checks * self.total_checks * 1000 / get_generation_duration() * 0.1)
        return self.total_checks * self.total_checks / get_generation_duration()

    def rot_center(self, image, angle):
        orig_rect = image.get_rect()
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

def get_generation_duration():
    time = current_time - gen_start_time
    if time == 0:
        return 1
    return time

def make_decisions(cars, nets):
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

def run_car(genomes, config):
    # Init NEAT
    nets = []
    cars = []
    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        starting_pos = [0, 0]
        starting_angle = 0
        # Init my cars
        if str(map_no) == "1":
            # starting_pos = map.starting_pos # I don't know if I will ever understand why this line of code does not work
            starting_pos = [700, 650]
            starting_angle = 0
        if str(map_no) == "2":
            starting_pos = [50, 550]
            starting_angle = -90
        cars.append(Car(map_no, starting_angle))
    map = Map(map_no, cars)

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)

    # Main loop
    global current_max_lap
    global generation
    global current_time
    global gen_start_time
    current_time = pygame.time.get_ticks()
    gen_start_time = pygame.time.get_ticks()
    generation += 1
    current_max_lap = 0
    
    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        make_decisions(map.cars, nets)

        # Update car and fitness
        remain_cars = 0
        for i, car in enumerate(map.cars):
            if car.get_alive():
                remain_cars += 1
                car.update(map)
                genomes[i][1].fitness += car.get_reward()

        # check
        if remain_cars == 0 or get_generation_duration() > max_gen_time or current_max_lap >= max_gen_laps:
            break

        # Drawing
        screen.blit(map.img, (0, 0))
        for i, cp in enumerate(map.checkpoints): #<-- for seeing all checkpoints
            pygame.draw.circle(screen, (255, 255, 0), map.checkpoints[i], checkpoint_diameter + map.checkpoints_growth[i], 1)
        for car in map.cars:
            if car.get_alive():
                car.draw(screen)

        text = generation_font.render("Generation: " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        screen.blit(text, text_rect)

        text = font.render("Remaining Cars: " + str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)

def gen_heatmap(genomes, config):
    # Init NEAT
    nets = []
    cars = []

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        # Init my cars
        if str(map_no) == "1":
            # starting_pos = map.starting_pos # I don't know if I will ever understand why this line of code does not work
            starting_pos = [700, 650]
            starting_angle = 0
        if str(map_no) == "2":
            starting_pos = [50, 550]
            starting_angle = -90
        cars.append(Car(map_no, starting_angle))
    map = Map(map_no, cars)

    seaborn.set_theme()
    heatmap_data = np.zeros((800, 1500))

    # Init my game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)

    # Main loop
    global current_max_lap
    global current_time
    global gen_start_time
    current_time = pygame.time.get_ticks()
    gen_start_time = pygame.time.get_ticks()
    current_max_lap = 0
    while True:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        make_decisions(cars, nets)
        
        # Update car and fitness
        remain_cars = 0
        for i, car in enumerate(map.cars):
            if car.get_alive():
                remain_cars += 1
                car.update(map)

        # check
        if remain_cars == 0 or get_generation_duration() > max_gen_time or current_max_lap >= max_gen_laps:
            ax = seaborn.heatmap(heatmap_data, vmin=0, vmax=1, cbar=False, yticklabels=False, xticklabels=False, square=True, cmap="rocket")
            plt.savefig('foo3.png', pad_inches = 0, bbox_inches = 'tight')
            img1 = Image.open('../map1.png')
            img2 = Image.open('foo3.png')
            img2.putalpha(ImageEnhance.Brightness(img2.split()[3]).enhance(0.8))

            #scaling
            basewidth = 496
            wpercent = (basewidth / float(img1.size[0]))
            hsize = int((float(img1.size[1]) * float(wpercent)))
            img1 = img1.resize((basewidth, hsize), Image.ANTIALIAS)
            baseheight = 264
            hpercent = (baseheight / float(img1.size[1]))
            wsize = int((float(img1.size[0]) * float(hpercent)))
            img1 = img1.resize((wsize, baseheight), Image.ANTIALIAS)


            img1 = Image.composite(img2, img1, img2)
            img1 = img1.convert("RGB")
            img1.save('out2.png')
            #plt.show()
            break

        # Drawing
        screen.blit(map.img, (0, 0))
        for car in map.cars:
            if car.get_alive():
                car.draw(screen)
                # print("car.pos[0]: "+str(car.pos[0]))
                # print("car.pos[1]: "+str(car.pos[1]))
                y = round(car.center[1])
                x = round(car.center[0])
                heatmap_data[y, x] += 0.4
                heatmap_data[y-1, x] += 0.2
                heatmap_data[y+1, x] += 0.2
                heatmap_data[y, x-1] += 0.2
                heatmap_data[y, x+1] += 0.2
                heatmap_data[y-1, x+1] += 0.2
                heatmap_data[y-1, x-1] += 0.2
                heatmap_data[y+1, x+1] += 0.2
                heatmap_data[y+1, x-1] += 0.2
                print("heatmap_data[round("+str(y)+"), round("+str(x)+")]: "+str(heatmap_data[y, x]))

        text = generation_font.render("Generating Heatmap ..", True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        screen.blit(text, text_rect)

        text = font.render("Remaining Cars: " + str(remain_cars), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)

if __name__ == "__main__":
    
    print('\n########## Argument List:', str(sys.argv), ' ##########')

    # Set configuration file
    config_path = "./config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    cp_agent = CheckPointer.Checkpointer(generation_interval=1, time_interval_seconds=300)

    do_heatmap = 0
    global map_no
    map_no = 1
    p = neat.Population(config, None)
    # Create core evolution algorithm class
    if len(sys.argv) > 1:
        if sys.argv[1] == '1' or sys.argv[1] == '2':
            map_no = sys.argv[1]
            print("> "+sys.argv[1]+" IS a valid map number.")
        else:
            print("> "+sys.argv[1]+" is NOT a valid map number.")
            exit()
        if len(sys.argv) > 2:
            print("> Trying to access ais/"+sys.argv[2])
            try:
                p = cp_agent.restore_checkpoint("ais/"+sys.argv[2])
                print("> File accessed.")
            except FileNotFoundError:
                print("> No such file exists.")
                exit()
    if len(sys.argv) == 4:
        if sys.argv[3] == "-h":
            print("> Do a heatmap fella")
            do_heatmap = 1
    else:
        print("> Doing training")

    p.add_reporter(cp_agent)
    # Add reporter for fancy statistical result
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    if do_heatmap == 0:
        p.run(run_car, 1000)
    elif do_heatmap == 1:
        p.run(gen_heatmap, 1)