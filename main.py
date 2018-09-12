import pygame
import os
import math

#--- classes ---#
class Sprite():
	def __init__(self, path, pos=(0, 0)):
		self.original = pygame.image.load("sprites/"+str(path)).convert_alpha()
		self.sprite = self.original
		
		self.rect = self.sprite.get_rect(pos)
		
		self.rotation = 0
		
		global renderList
		renderList.append(self)
	
	
	def tick(self):
		pass
	
	
	def setPos(self, x=None, y=None):
		if (x is not None):
			self.rect.x = x
		if (y is not None):
			self.rect.y = y
	
	
	def setRotation(self, angle):
		self.rotation = angle
		center = self.rect.center
		self.sprite = pygame.transform.rotate(self.original, self.rotation)
		self.rect = self.sprite.get_rect()
		self.rect.center = center
	
	
	def getRotation(self):
		return self.rotation
	
	
	def getRect(self):
		return self.rect
	
	
	def getCenter(self):
		return self.rect.center
	
	
	def render(self, display):
		display.blit(self.sprite, self.rect)


class Ship(Sprite):
	def __init__(self):
		self.original = pygame.image.load("sprites/ship.png").convert_alpha()
		self.sprite = self.original
		
		global screen
		self.rect = self.sprite.get_rect(center = screen.get_rect().center)
		
		self.rotation = 0
		
		global renderList
		renderList.append(self)


class Bullet(Sprite):
	def __init__(self, direction):
		self.original = pygame.image.load("sprites/bullet.png").convert_alpha()
		self.sprite = self.original
		
		global screen
		self.rect = self.sprite.get_rect(center = screen.get_rect().center)
		self.realPos = [self.rect.x, self.rect.y]
		
		self.rotation = 0
		self.setRotation(direction-90)
		rad = math.radians((-direction)-90)
		self.movingIndex = (10*math.cos(rad), 10*math.sin(rad))
		
		self.realPos = [self.rect.x+self.movingIndex[0], self.rect.y+self.movingIndex[1]]
		
		global renderList
		renderList.append(self)
	
	
	def tick(self):
		self.realPos[0] += self.movingIndex[0]
		self.realPos[1] += self.movingIndex[1]
		self.rect.x, self.rect.y = self.realPos
#--- /classes ---#
#--- main ---#
FPS = 60

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("truc de l'espace")

# variables
renderList = list()
clock = pygame.time.Clock()
running = True

ship = Ship()

while (running):
	# events
	for event in pygame.event.get():
		if (event.type == pygame.QUIT):
			running = False
		if (event.type == pygame.MOUSEMOTION):
			mouse_pos = pygame.mouse.get_pos()
			ship_pos = ship.getCenter()
			ship.setRotation(math.degrees(math.atan2(ship_pos[0]-mouse_pos[0], ship_pos[1]-mouse_pos[1])))
		if (event.type == pygame.MOUSEBUTTONDOWN):
			if (event.button == 1):
				Bullet(ship.getRotation())
			
	
	# render
	screen.fill((pygame.Color("black")))
	for sprite in renderList:
		sprite.tick()
		sprite.render(screen)
	pygame.display.flip()
	
	# loop timer
	clock.tick_busy_loop(FPS)
#--- /main ---#