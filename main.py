import pygame
import os
import math
import random

#--- classes ---#
class Sprite():
	def __init__(self, path, direction, speed, pos, rotationSpeed):
		# sprite
		self.original = pygame.image.load("sprites/"+str(path)).convert_alpha()
		self.sprite = self.original
		
		# rect
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = speed
		self.rotationSpeed = rotationSpeed
		self.setRotation(direction-90)
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(pos)
		
		global renderList
		renderList.append(self)
	
	
	def tick(self):
		self.floatCenter[0] += self.movingIndex[0]
		self.floatCenter[1] += self.movingIndex[1]
		self.setRotation(self.getRotation()+self.rotationSpeed)
	
	
	def setPosition(self, pos):
		self.floatCenter = pos
	
	
	def setRotation(self, angle):
		self.rotation = angle
		self.sprite = pygame.transform.rotate(self.original, self.rotation)
		self.rect = self.sprite.get_rect()
	
	
	def getPosition(self):
		return self.floatCenter
	
	
	def getRotation(self):
		return self.rotation
	
	
	def render(self, display):
		self.rect.center = self.floatCenter
		display.blit(self.sprite, self.rect)
	
	
	def destroy(self):
		global renderList
		renderList.remove(self)


class Ship(Sprite):
	def __init__(self):
		# sprite
		self.original = pygame.image.load("sprites/ship.png").convert_alpha()
		self.sprite = self.original
		
		# rect
		global screen
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = 0
		self.rotationSpeed = 0
		self.setRotation(0)
		self.rad = math.radians((0)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(screen.get_rect().center)
		
		global renderList
		renderList.append(self)


class Bullet(Sprite):
	def __init__(self, direction, speed):
		# sprite
		self.original = pygame.image.load("sprites/bullet.png").convert_alpha()
		self.sprite = self.original
		
		# rect
		global screen
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = speed
		self.rotationSpeed = 0
		self.setRotation(direction-90)
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = [screen.get_rect().center[0]+self.movingIndex[0], screen.get_rect().center[1]+self.movingIndex[1]]
		
		global renderList
		global bulletsList
		renderList.append(self)
		bulletsList.append(self)
	
	
	def destroy(self):
		global renderList
		global bulletsList
		renderList.remove(self)
		bulletsList.remove(self)


class Asteroid(Sprite):
	def __init__(self, direction, speed, pos, rotationSpeed):
		# sprite
		self.original = pygame.image.load("sprites/asteroid.png").convert_alpha()
		self.sprite = self.original
		
		# rect
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = speed
		self.rotationSpeed = rotationSpeed
		self.setRotation(direction-90)
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(pos)
		
		global renderList
		global asteroidsList
		renderList.append(self)
		asteroidsList.append(self)
	
	
	def destroy(self):
		global renderList
		global asteroidsList
		renderList.remove(self)
		asteroidsList.remove(self)
#--- /classes ---#
#--- foctions ---#
def createAsteroid():
	commingFrom = random.randint(0, 3)
	direction = 0
	pos = [0, 0]
	if (commingFrom == 0):
		direction = random.randint(-180,-40)
		pos[0] = random.randint(0, screen.get_rect().width)
		pos[1] = -50
	elif (commingFrom == 1):
		direction = random.randint(20, 160)
		pos[0] = screen.get_rect().width+50
		pos[1] = random.randint(0, screen.get_rect().height)
	elif (commingFrom == 2):
		direction = random.randint(-70, 70)
		if (direction > 110):
			direction += 180
		pos[0] = random.randint(0, screen.get_rect().width)
		pos[1] = screen.get_rect().height+50
	else:
		direction = random.randint(-170, 20)
		pos[0] = -50
		pos[1] = random.randint(0, screen.get_rect().height)
	
	speed = random.randint(2, 4)
	rotationSpeed = random.randint(-5, 5)
	Asteroid(direction, speed, pos, rotationSpeed)
#--- /foctions ---#
#--- main ---#
FPS = 60

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("truc de l'espace")

random.seed()

# variables
renderList = list()
asteroidsList = list()
bulletsList = list()

clock = pygame.time.Clock()
running = True
bulletTimeout = 0
asteroidTimeout = 0

ship = Ship()

while (running):
	# events
	for event in pygame.event.get():
		if (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
			running = False
		if (event.type == pygame.MOUSEMOTION):
			mouse_pos = pygame.mouse.get_pos()
			ship_pos = ship.getPosition()
			ship.setRotation(math.degrees(math.atan2(ship_pos[0]-mouse_pos[0], ship_pos[1]-mouse_pos[1])))
	
	if (pygame.mouse.get_pressed()[0] == True and bulletTimeout == 0):
			Bullet(ship.getRotation(), 7)
			bulletTimeout = 12
	elif (bulletTimeout > 0):
		bulletTimeout -= 1
	
	if (asteroidTimeout == 0):
		createAsteroid()
		asteroidTimeout = 20
	else:
		asteroidTimeout -= 1
	
	# collision detection
	for bullet in bulletsList:
		val = bullet.rect.collidelist(asteroidsList)
		if (val >= 0):
			bullet.destroy()
			asteroidsList[val].destroy()
			
			
	
	# tick and render
	screen.fill((pygame.Color("black")))
	for sprite in renderList:
		sprite.tick()
		sprite.render(screen)
	pygame.display.flip()
	
	# loop timer
	clock.tick_busy_loop(FPS)
#--- /main ---#