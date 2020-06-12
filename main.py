import pygame
from lib.creatures import Plant, Herbivore, Carnivore
from lib.world import World
import sys
import time 

if __name__ == '__main__':
    pygame.init()  

    WIDTH   = 800
    HEIGHT  = 800

    SCREEN_SIZE = (WIDTH, HEIGHT)

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    pixels_per_sec = 10

    world = World(SCREEN_SIZE)

    gen_h = True
    gen_c = True

    # Add Creatures
    for i in range(50):
        world.add_creture(Plant(world))
        time.sleep(0.01)

    for i in range(15):
        world.add_creture(Herbivore(world, gender=gen_h))
        time.sleep(0.01)
        world.add_creture(Carnivore(world, gender=gen_c))
        time.sleep(0.01)
        gen_c = not gen_c
        gen_h = not gen_h

    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # main loop
        screen.fill((0,150,20))
        time_elapsed = clock.tick(70)
        time_elapsed = time_elapsed/1000

        world.process(time_elapsed)
        world.render(screen)

        pygame.display.update()