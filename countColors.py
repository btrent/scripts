from pygame.locals import *
import pygame
pygame.init()
f = file("colors.txt","w")
screen = pygame.display.set_mode((1, 1))
image = pygame.image.load("picture.png").convert()
height = image.get_height()
width = image.get_width()
colors = {}
for y in range(0,height):
    for x in range(0,width):
        pixel = image.get_at((x,y))
        color = "%02X%02X%02X"%(pixel[0],pixel[1],pixel[2])
        if colors.has_key(color):
            colors[color] = colors[color] + 1
        else:
            colors[color] = 1
for key in sorted(colors.iterkeys()):
	f.write("%s: %s\n"%(key,colors[key]))
f.close()
