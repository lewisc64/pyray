import pygame
import math

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def rotate(self, angle):
        x = self.x
        self.x = self.x * math.cos(-angle) - self.y * math.sin(-angle)
        self.y = x * math.sin(-angle) + self.y * math.cos(-angle)
    
    def get_angle(self):
        return math.atan2(self.y, self.x)
    
    def copy(self):
        return Vector(self.x, self.y)
    
    def __str__(self):
        return "({}, {})".format(self.x, self.y)
    
    def __eq__(self, v):
        return v.x == self.x and v.y == self.y
    
    def __add__(self, v):
        if type(v) is Vector:
            return Vector(self.x + v.x, self.y + v.y)
    
    def __sub__(self, v):
        if type(v) is Vector:
            return Vector(self.x - v.x, self.y - v.y)
    
    def __mul__(self, v):
        if type(v) is Vector:
            return Vector(self.x * v.x, self.y * v.y)

class Camera:
    def __init__(self, x, y, fov=90, hitbox_radius=0.2):
        self.pos = Vector(x, y)
        self.dir = Vector(-1, 0)
        self.plane = Vector(0, fov / 180)
        self.rotate(math.pi)
        self.speed = 0.08
        self.look_speed = 3 * (math.pi / 180)
        self.held_keys = []
        #self.controls = {"forward":pygame.K_w, "back":pygame.K_s, "left":pygame.K_a, "right":pygame.K_d, "look_left":pygame.K_LEFT, "look_right":pygame.K_RIGHT}
        self.controls = {"forward":pygame.K_UP, "back":pygame.K_DOWN, "left":None, "right":None, "look_left":pygame.K_LEFT, "look_right":pygame.K_RIGHT}
        self.hitbox_radius = hitbox_radius
        self.shift_y = 200
    
    def rotate(self, angle):
        self.dir.rotate(angle)
        self.plane.rotate(angle)
    
    def get_rect(self):
        return (self.pos.x - self.hitbox_radius,
                self.pos.y - self.hitbox_radius,
                self.hitbox_radius * 2,
                self.hitbox_radius * 2)
    
    def detect_keys(self, key, keydown):
        if keydown:
            if key not in self.held_keys:
                self.held_keys.append(key)
        else:
            while key in self.held_keys:
                self.held_keys.remove(key)
    
    def collide_rect(self, r1, r2):
        return r1[0] < r2[0] + r2[2] and r2[0] < r1[0] + r1[2] and r1[1] < r2[1] + r2[3] and r2[1] < r1[1] + r1[3]
    
    def in_wall(self, raycaster):
        for x in range(-int(self.pos.x), int(self.pos.x) + 2):
            for y in range(-int(self.pos.y), int(self.pos.y) + 2):
                if raycaster.grid[x][y] > 0 and self.collide_rect((x, y, 1, 1), (self.get_rect())):
                    return True
        return False
    
    def handle(self, raycaster, collisions=True):
        move_x = 0
        move_y = 0
        if self.controls["forward"] in self.held_keys:
            move_x += self.dir.x * self.speed
            move_y += self.dir.y * self.speed
        if self.controls["back"] in self.held_keys:
            move_x += -self.dir.x * self.speed
            move_y += -self.dir.y * self.speed
        if self.controls["left"] in self.held_keys:
            dir = self.dir.copy()
            dir.rotate(-math.pi / 2)
            move_x += dir.x * self.speed
            move_y += dir.y * self.speed
        if self.controls["right"] in self.held_keys:
            dir = self.dir.copy()
            dir.rotate(math.pi / 2)
            move_x += dir.x * self.speed
            move_y += dir.y * self.speed
        if self.controls["look_left"] in self.held_keys:
            self.rotate(-self.look_speed)
        if self.controls["look_right"] in self.held_keys:
            self.rotate(self.look_speed)
        if move_x != 0:
            self.pos.x += move_x
            if collisions and self.in_wall(raycaster):
                self.pos.x -= move_x
        if move_y != 0:
            self.pos.y += move_y
            if collisions and self.in_wall(raycaster):
                self.pos.y -= move_y
