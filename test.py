import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
running = True

while (running):
	for event in pygame.event.get():
		if (event.type == pygame.KEYDOWN):
			print(str(event.unicode)+" : "+str(event.key))
		if (event.type == pygame.QUIT):
			running = False