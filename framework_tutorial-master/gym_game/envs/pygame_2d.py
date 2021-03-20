import pygame
import math

screen_width = 1500
screen_height = 800
check_point = ((1100, 690), (1100, 85), (520, 270), (800, 520), (650, 690))
btfo_purple = (146, 15, 95, 255)
grass_green = (85, 162, 69, 255)
road_grey = (100, 106, 97, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)


class Car:
    def __init__(self, car_file, map_file, pos):
        self.surface = pygame.image.load(car_file)
        self.map = pygame.image.load(map_file)
        self.surface = pygame.transform.scale(self.surface, (100, 100))
        self.rotate_surface = self.surface
        self.pos = pos
        self.angle = 0
        self.speed = 10
        self.center = [self.pos[0] + 50, self.pos[1] + 50]
        self.btfo_radars = []
        self.btfo_radars_for_draw = []
        self.roadedge_radars = []
        self.roadedge_radars_for_draw = []
        self.is_alive = True
        self.is_on_grass = False
        self.current_check = 0
        self.prev_distance = 0
        self.cur_distance = 0
        self.goal = False
        self.check_flag = False
        self.distance = 0
        self.time_spent = 0
        for d in range(-90, 120, 45):
            self.check_btfo_radar(d)
            self.check_roadedge_radar(d)

        for d in range(-90, 120, 45):
            self.check_btfo_radar_for_draw(d)
            self.check_roadedge_radar_for_draw(d)

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)

    def draw_collision(self, screen):
        for i in range(4):
            x = int(self.four_points[i][0])
            y = int(self.four_points[i][1])
            pygame.draw.circle(screen, btfo_purple, (x, y), 5)

    def draw_btfo_radar(self, screen):
        for r in self.btfo_radars_for_draw:
            pos, dist = r
            pygame.draw.line(screen, red, self.center, pos, 1)
            pygame.draw.circle(screen, red, pos, 5)
    
    def draw_roadedge_radar(self, screen):
        for r in self.roadedge_radars_for_draw:
            pos, dist = r
            pygame.draw.line(screen, blue, self.center, pos, 1)
            pygame.draw.circle(screen, blue, pos, 5)

    def check_collision(self, colour):
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

    def check_btfo_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        while not self.map.get_at((x, y)) == btfo_purple and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.btfo_radars.append([(x, y), dist])

    def check_roadedge_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        colour = grass_green
        try:
            if self.map.get_at((x, y)) == grass_green:
                colour = road_grey
        except IndexError: # catch the error
            pass
        try:
            while not self.map.get_at((x, y)) == colour and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.roadedge_radars.append([(x, y), dist])

    def check_btfo_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        while not self.map.get_at((x, y)) == btfo_purple and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.btfo_radars_for_draw.append([(x, y), dist])
    
    def check_roadedge_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        radar_on_grass = 0
        try:
            if self.map.get_at((x, y)) == grass_green:
                radar_on_grass = 1
        except IndexError: # catch the error
            pass
        colour = road_grey
        if radar_on_grass == 0:
            colour = grass_green
        try:
            while not self.map.get_at((x, y)) == colour and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.roadedge_radars_for_draw.append([(x, y), dist])

    def check_checkpoint(self):
        p = check_point[self.current_check]
        self.prev_distance = self.cur_distance
        dist = get_distance(p, self.center)
        if dist < 70:
            self.current_check += 1
            self.prev_distance = 9999
            self.check_flag = True
            self.time_spent = 0
            if self.current_check >= len(check_point):
                self.current_check = 0
                self.goal = True
            else:
                self.goal = False
        self.cur_distance = dist

    def update(self):
        #check position
        self.rotate_surface = rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 1:
            self.pos[0] = 1
        elif self.pos[0] > screen_width - 1:
            self.pos[0] = screen_width - 1

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        # if self.pos[1] < 1:
        #     self.pos[1] = 1
        # elif self.pos[1] > screen_height - 1:
        #     self.pos[1] = screen_height - 1

        # caculate 4 collision points
        self.center = [int(self.pos[0]) + 50, int(self.pos[1]) + 50]
        len = 40
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

class PyGame2D:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 30)
        self.car = Car('car.png', 'map.png', [700, 650])
        self.game_speed = 60
        self.mode = 0

    def action(self, action):
        #print("action: ",action)
        if action == 0:
            self.car.angle += 10
        elif action == 1:
            self.car.angle += 5
        elif action == 2:
            pass
        elif action == 3:
            self.car.angle -= 5
        elif action == 4:
            self.car.angle -= 10
        self.car.update()

        self.car.check_is_on_grass()
        self.car.speed = 12
        if self.car.is_on_grass:
            self.car.speed = 5

        self.car.check_collision(btfo_purple)
        self.car.check_checkpoint()

        self.car.btfo_radars.clear()
        self.car.roadedge_radars.clear()
        for d in range(-90, 120, 45):
            self.car.check_btfo_radar(d)
            self.car.check_roadedge_radar(d)

    def evaluate(self):
        reward = 0
        # if self.car.is_on_grass:
        #     reward -= 3

        if self.car.check_flag:
            self.car.check_flag = False
            reward += (1500 * ((0.7) * (self.car.current_check + 1)) - self.car.time_spent * 10)
        
        if not self.car.is_alive:
            #reward = -10000 + self.car.distance
            reward -= (self.car.cur_distance / 2) * (self.car.time_spent / 10)

        elif self.car.goal:
            reward = (10000 - self.car.time_spent * 10)
        return reward

    def is_done(self):
        if not self.car.is_alive or self.car.goal:
            self.car.current_check = 0
            self.car.distance = 0
            return True
        return False

    def observe(self):
        # return state
        btfo_radars = self.car.btfo_radars
        roadedge_radars = self.car.roadedge_radars
        ret = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, r in enumerate(btfo_radars + roadedge_radars):
            ret[i] = int(r[1] / 30)

        return tuple(ret)

    def view(self):
        # draw game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.mode += 1
                    self.mode = self.mode % 3

        self.screen.blit(self.car.map, (0, 0))


        if self.mode == 1:
            self.screen.fill((0, 0, 0))

        self.car.btfo_radars_for_draw.clear()
        self.car.roadedge_radars_for_draw.clear()
        for d in range(-90, 120, 45):
            self.car.check_btfo_radar_for_draw(d)
            self.car.check_roadedge_radar_for_draw(d)

        pygame.draw.circle(self.screen, (255, 255, 0), check_point[self.car.current_check], 70, 1)
        # for i, cp in enumerate(check_point): <-- for seeing all checkpoints
        #     pygame.draw.circle(self.screen, (255, 255, 0), check_point[i], 70, 1)
        self.car.draw_collision(self.screen)
        self.car.draw_btfo_radar(self.screen)
        self.car.draw_roadedge_radar(self.screen)
        self.car.draw(self.screen)
        text = self.font.render("Press 'm' to change view mode", True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        self.clock.tick(self.game_speed)

def get_distance(p1, p2):
	return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
