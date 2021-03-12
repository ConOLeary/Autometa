import pygame
import math

grass_disincentive = 1000

screen_width = 1500
screen_height = 800
check_point = ((1200, 660), (1250, 120), (190, 200), (1030, 270), (250, 475), (650, 690))
purple = (146, 15, 95, 255)
green = (85, 162, 69, 255)
grey = (100, 106, 97, 255)
radar_green = (0, 255, 0)
radar_blue = (0, 0, 255)
radar_red = (255, 0, 0)


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
        self.radars = []
        self.radars_for_draw = []
        self.grass_radars = []
        self.grass_radars_for_draw = []
        self.anti_grass_radars = []
        self.anti_grass_radars_for_draw = []
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
            self.check_radar(d)
            if(self.is_on_grass):
                self.check_anti_grass_radar(d)
            else:
                self.check_grass_radar(d)

        for d in range(-90, 120, 45):
            self.check_radar_for_draw(d)
            if(self.is_on_grass):
                self.check_anti_grass_radar_for_draw(d)
            else:
                self.check_grass_radar_for_draw(d)

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)

    def draw_collision(self, screen):
        for i in range(4):
            x = int(self.four_points[i][0])
            y = int(self.four_points[i][1])
            pygame.draw.circle(screen, purple, (x, y), 5)

    def draw_radar(self, screen):
        for r in self.radars_for_draw:
            pos, dist = r
            pygame.draw.line(screen, radar_green, self.center, pos, 1)
            pygame.draw.circle(screen, radar_green, pos, 5)
    
    def draw_grass_radar(self, screen):
        for r in self.grass_radars_for_draw:
            pos, dist = r
            pygame.draw.line(screen, radar_blue, self.center, pos, 1)
            pygame.draw.circle(screen, radar_blue, pos, 5)

    def draw_anti_grass_radar(self, screen):
        for r in self.anti_grass_radars_for_draw:
            pos, dist = r
            pygame.draw.line(screen, radar_red, self.center, pos, 1)
            pygame.draw.circle(screen, radar_red, pos, 5)

    def check_collision(self, colour):
        self.is_alive = True
        for p in self.four_points:
            if self.map.get_at((int(p[0]), int(p[1]))) == colour:
                self.is_alive = False
                break
    
    def check_grass(self, colour):
        self.is_on_grass = False
        for p in self.four_points:
            if self.map.get_at((int(p[0]), int(p[1]))) == colour:
                self.is_on_grass = True
                break

    def check_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not self.map.get_at((x, y)) == purple and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def check_grass_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        try:
            while not self.map.get_at((x, y)) == green and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.grass_radars.append([(x, y), dist])
    
    def check_anti_grass_radar(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        try:
            while not self.map.get_at((x, y)) == grey and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.anti_grass_radars.append([(x, y), dist])

    def check_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        while not self.map.get_at((x, y)) == purple and len < 300:
            len = len + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars_for_draw.append([(x, y), dist])
    
    def check_grass_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        try:
            while not self.map.get_at((x, y)) == green and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.grass_radars_for_draw.append([(x, y), dist])
    
    def check_anti_grass_radar_for_draw(self, degree):
        len = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        try:
            while not self.map.get_at((x, y)) == grey and len < 300:
                len = len + 1
                x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len)
                y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len)
        except IndexError: # catch the error
            pass
        
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.anti_grass_radars_for_draw.append([(x, y), dist])

    def check_checkpoint(self):
        p = check_point[self.current_check]
        self.prev_distance = self.cur_distance
        dist = get_distance(p, self.center)
        if dist < 70:
            self.current_check += 1
            self.prev_distance = 9999
            self.check_flag = True
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
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > screen_width - 120:
            self.pos[0] = screen_width - 120

        self.distance += self.speed
        self.time_spent += 1
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > screen_height - 120:
            self.pos[1] = screen_height - 120

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
        # if action == 0:
        #     self.car.speed += 2
        if action == 1:
            self.car.angle += 5
        elif action == 2:
            self.car.angle -= 5
        self.car.update()

        self.car.check_grass(green)
        self.car.speed = 12
        if self.car.is_on_grass:
            self.car.speed = 5

        
        self.car.check_collision(purple)
        self.car.check_checkpoint()

        self.car.radars.clear()
        self.car.grass_radars.clear()
        for d in range(-90, 120, 45):
            self.car.check_radar(d)
            if(self.car.is_on_grass):
                self.car.check_anti_grass_radar(d)
            else:
                self.car.check_grass_radar(d)

    def evaluate(self):
        reward = 0
        
        if self.car.is_on_grass:
            reward = -grass_disincentive

        if self.car.check_flag:
            self.car.check_flag = False
            reward = 2000 - self.car.time_spent
            self.car.time_spent = 0
        
        if not self.car.is_alive:
            reward = -10000 + self.car.distance

        elif self.car.goal:
            reward = 10000
        return reward

    def is_done(self):
        if not self.car.is_alive or self.car.goal:
            self.car.current_check = 0
            self.car.distance = 0
            return True
        return False

    def observe(self):
        # return state
        radars = self.car.radars
        grass_radars = self.car.grass_radars
        anti_grass_radars = self.car.anti_grass_radars
        ret = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i, r in enumerate(radars + grass_radars + anti_grass_radars):
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

        self.car.radars_for_draw.clear()
        self.car.grass_radars_for_draw.clear()
        self.car.anti_grass_radars_for_draw.clear()
        for d in range(-90, 120, 45):
            self.car.check_radar_for_draw(d)
            self.car.check_grass_radar_for_draw(d)
            self.car.check_anti_grass_radar_for_draw(d)

        pygame.draw.circle(self.screen, (255, 255, 0), check_point[self.car.current_check], 70, 1)
        self.car.draw_collision(self.screen)
        self.car.draw_radar(self.screen)
        self.car.draw_grass_radar(self.screen)
        self.car.draw_anti_grass_radar(self.screen)
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
