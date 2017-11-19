import pygame

class Sprite:
    def __init__(self, x, y, image, draw_distance=-1, clip_distance=0.5, max_height=-1):
        self.x = x
        self.y = y
        self.image = image
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.clip_distance = clip_distance
        self.draw_distance = draw_distance
        self.off_camera = False
        self.max_height = max_height
    
    def draw(self, surface, x, y, height):
        if self.max_height != -1:
            height = min(height, self.max_height)
        width = int(self.width / self.height * height)
        x = x - width // 2
        y = y - height // 2
        if height < surface.get_height() * 4 and x + width > 0 and x < surface.get_width():
            scaled = pygame.transform.scale(self.image, (width, height))
            surface.blit(scaled, (x, y))

    def handle(self, raycaster, camera):
        dist = (self.x - camera.pos.x) ** 2 + (self.y - camera.pos.y) ** 2
        if dist > self.clip_distance ** 2 and (self.draw_distance == -1 or dist < self.draw_distance):
            self.map_x = int(self.x)
            self.map_y = int(self.y)
            raycaster.sprites.append(self)
