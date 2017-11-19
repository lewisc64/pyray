import pygame
import pyray

WIDTH = 512
HEIGHT = 384
FPS = 60

display = pygame.display.set_mode((WIDTH, HEIGHT), pyray.flags)
clock = pygame.time.Clock()

sprite_textures = {"light":pygame.image.load("wolf3d/greenlight.png"),
                   "barrel":pygame.image.load("wolf3d/barrel.png"),
                   "pillar":pygame.image.load("wolf3d/pillar.png")}

textures = [pygame.image.load("wolf3d/redbrick.png"),
            pygame.image.load("wolf3d/eagle.png"),
            pygame.image.load("wolf3d/purplestone.png"),
            pygame.image.load("wolf3d/greystone.png"),
            pygame.image.load("wolf3d/bluestone.png"),
            pygame.image.load("wolf3d/mossy.png"),
            pygame.image.load("wolf3d/wood.png"),
            pygame.image.load("wolf3d/colorstone.png"),
            sprite_textures["light"],
            sprite_textures["barrel"],
            sprite_textures["pillar"]]

raycaster = pyray.Raycaster(display, pygame.image.load("map.png"), textures)
camera = pyray.Camera(3.5, 2.5)

sprites = []
for texture in sprite_textures.values():
    sprites.extend(raycaster.object_to_sprite_list(texture))

while True:
    
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif e.type == pygame.KEYDOWN:
            camera.detect_keys(e.key, True)
        elif e.type == pygame.KEYUP:
            camera.detect_keys(e.key, False)
    
    camera.handle(raycaster)
    
    for sprite in sprites:
        sprite.handle(raycaster, camera)
    
    pygame.draw.rect(display, (56, 56, 56), (0, 0, WIDTH, HEIGHT // 2)) # Ceiling
    pygame.draw.rect(display, (112, 112, 112), (0, HEIGHT // 2, WIDTH, HEIGHT // 2)) # Floor
    raycaster.render(camera)
    
    pygame.display.update()
    clock.tick(FPS)
