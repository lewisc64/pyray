import pygame
import pyray

WIDTH = 512
HEIGHT = 384
FPS = 60

display = pygame.display.set_mode((WIDTH, HEIGHT), pyray.flags)
clock = pygame.time.Clock()

colors = [(255, 0, 0),
          (0, 255, 0)]

map = [[1,1,1,1,1,1,1],
       [1,0,0,0,0,0,1],
       [1,0,0,0,0,0,1],
       [1,0,0,2,0,0,1],
       [1,0,0,0,0,0,1],
       [1,0,0,0,0,0,1],
       [1,1,1,1,1,1,1],]

raycaster = pyray.Raycaster(display, map, colors)
camera = pyray.Camera(1.5, 1.5)

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
    
    display.fill((0, 0, 0))
    raycaster.render(camera)
    
    pygame.display.update()
    clock.tick(FPS)
