import pygame
import math
from .sprite import Sprite

class Raycaster:
    def __init__(self, surface, grid=None, objects=None, shading=True):
        if type(grid) is pygame.Surface: # Grid from image.
            grid = grid.convert_alpha()
            self.grid = []
            temp_objects = []
            for x in range(grid.get_width()):
                self.grid.append([])
                for y in range(grid.get_height()):
                    color = grid.get_at((x, y))
                    if color[3] == 0:
                        item = 0
                    else:
                        if color not in temp_objects:
                            temp_objects.append(color[:3])
                            item = len(temp_objects)
                        else:
                            item = temp_objects.index(color) + 1
                    self.grid[x].append(item)
            if objects is None:
                objects = temp_objects
            else:
                for i in range(len(objects), len(temp_objects)):
                    objects.append(temp_objects[i])
        else:
            self.grid = grid
        
        self.surface = surface
        self.surface_width = self.surface.get_width()
        self.surface_height = self.surface.get_height()
        self.aspect_ratio = self.surface_width / self.surface_height
        self.width = len(self.grid)
        self.height = len(self.grid[0])
        self.shading = shading
        self.shading_value = 0.5
        self.set_objects(objects)
        self.sprites = []
        self.column_width = 1
    
    def set_objects(self, objects):
        self.objects = objects[:]
        if self.shading:
            self.dark_objects = objects[:]
            for i, object in enumerate(self.dark_objects):
                if type(object) is tuple:
                    self.dark_objects[i] = tuple([x * self.shading_value for x in object])
                elif type(object) is pygame.Surface:
                    dark = pygame.Surface(object.get_size()).convert_alpha()
                    dark.fill((0,0,0,255*self.shading_value))
                    image = object.copy().convert_alpha()
                    image.blit(dark, (0, 0))
                    self.dark_objects[i] = image
    
    #def __distance(self, p1, p2):
    #    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
    
    def __get_height(self, dist):
        return int(self.surface_height / dist * self.aspect_ratio)
    
    def get_object_coords(self, object):
        out = []
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[x][y] != 0:
                    grid_object = self.objects[self.grid[x][y] - 1]
                    if grid_object == object:
                        out.append((x, y))
        return out
    
    def remove_object(self, object):
        coords = self.get_object_coords(object)
        for x, y in coords:
            self.grid[x][y] = 0
        return coords
    
    def object_to_sprite_list(self, object):
        sprites = []
        for x, y in self.remove_object(object):
            sprites.append(Sprite(x + 0.5, y + 0.5, object))
        return sprites
    
    def render(self, camera):
        
        object_buffer = []
        object_z_buffer = []
        
        for sprite in self.sprites:
            sprite_x = sprite.x - camera.pos.x
            sprite_y = sprite.y - camera.pos.y
            inv_det = 1 / (camera.plane.x * camera.dir.y - camera.dir.x * camera.plane.y)
            transform_x = inv_det * (camera.dir.y * sprite_x - camera.dir.x * sprite_y);
            transform_y = inv_det * (-camera.plane.y * sprite_x + camera.plane.x * sprite_y)
            if transform_y > 0:
                sprite.off_camera = False
                x = int(self.surface_width / 2 * (1 + transform_x / transform_y))
                object_buffer.append((sprite, x, self.surface_height // 2, self.__get_height(transform_y)))
                object_z_buffer.append(transform_y)
            else:
                sprite.off_camera = True
                
        for x in range(0, self.surface_width, self.column_width):
            camera_x = 2 * x / self.surface_width - 1
            ray_pos_x = camera.pos.x
            ray_pos_y = camera.pos.y
            ray_dir_x = camera.dir.x + camera.plane.x * camera_x
            ray_dir_y = camera.dir.y + camera.plane.y * camera_x
            map_x = int(ray_pos_x)
            map_y = int(ray_pos_y)
            if ray_dir_x != 0:
                delta_dist_x = math.sqrt(1 + ray_dir_y ** 2 / ray_dir_x ** 2)
            if ray_dir_y != 0:
                delta_dist_y = math.sqrt(1 + ray_dir_x ** 2 / ray_dir_y ** 2)
            if ray_dir_x < 0:
                step_x = -1
                side_dist_x = (ray_pos_x - map_x) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (map_x + 1 - ray_pos_x) * delta_dist_x
            if ray_dir_y < 0:
                step_y = -1
                side_dist_y = (ray_pos_y - map_y) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (map_y + 1 - ray_pos_y) * delta_dist_y
            dist = -1
            
            while True: # DDA
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    map_y += step_y
                    side = 1
                if self.grid[map_x][map_y] > 0:
                    
                    if side == 0:
                        dist = (map_x - ray_pos_x + (1 - step_x) / 2) / ray_dir_x
                    else:
                        dist = (map_y - ray_pos_y + (1 - step_y) / 2) / ray_dir_y
                    height = self.__get_height(dist)
                    if side == 1 and self.shading:
                        object = self.dark_objects[self.grid[map_x][map_y] - 1]
                    else:
                        object = self.objects[self.grid[map_x][map_y] - 1]
        
                    padding = (self.surface_height - height) // 2
                    if type(object) is tuple:
                        pygame.draw.line(self.surface, object, (x, padding), (x, self.surface_height - padding))
                    elif type(object) is pygame.Surface:
                        if side == 0:
                            wall_x = ray_pos_y + dist * ray_dir_y
                        else:
                            wall_x = ray_pos_x + dist * ray_dir_x
                        wall_x %= 1
                        texture_width = object.get_width()
                        texture_height = object.get_height()
                        texture_x = int(wall_x * texture_width)
                        if side == 0 and ray_dir_x > 0:
                            texture_x = texture_width - texture_x - 1
                        elif side == 1 and ray_dir_y < 0:
                            texture_x = texture_width - texture_x - 1
                            
                        subsurface = object.subsurface((texture_x, 0, 1, texture_height)) # "GIVE ME SUBSURFACE" - Central
                        object_buffer.append(((x, padding), pygame.transform.scale(subsurface, (self.column_width, height))))
                        object_z_buffer.append(dist)
                    break
                
        for object in object_buffer if len(self.sprites) == 0 else [x for object_z_buffer, x in sorted(zip(object_z_buffer,object_buffer), key=lambda x: x[0])][::-1]:
            try:
                if type(object[1]) is pygame.Surface:
                    self.surface.blit(object[1], object[0])
                else:
                    object[0].draw(self.surface, *object[1:])
            except pygame.error:
                pass
        self.sprites = []
