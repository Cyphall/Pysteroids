import pygame
import os
import math
import random
import ctypes
import json
import time

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
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(pos)
		self.setRotation(direction-90)
		
		global renderList
		renderList.append(self)
	
	
	def tick(self):
		self.floatCenter[0] += self.movingIndex[0]
		self.floatCenter[1] += self.movingIndex[1]
		self.setRotation(self.getRotation()+self.rotationSpeed)
		self.rect.center = self.floatCenter
	
	
	def setPosition(self, pos):
		self.floatCenter = pos
	
	
	def setRotation(self, angle):
		self.rotation = angle
		self.sprite = pygame.transform.rotate(self.original, self.rotation)
		self.rect = self.sprite.get_rect()
		self.rect.center = self.floatCenter
	
	
	def getPosition(self):
		return self.floatCenter
	
	
	def getRotation(self):
		return self.rotation
	
	
	def render(self, display):
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
		self.rad = math.radians((0)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(screen.get_rect().center)
		self.weapon = Weapon("minigun")
		self.invulnerability = True
		self.isRendered = True
		self.invulnerabilityTimeout = 90
		self.setRotation(0)
		
		global renderList
		renderList.append(self)
	
	
	def move(self, direction):
		if (direction == "up"):
			self.floatCenter[1] -= 1.5
		elif (direction == "down"):
			self.floatCenter[1] += 1.5
		elif (direction == "left"):
			self.floatCenter[0] -= 1.5
		else:
			self.floatCenter[0] += 1.5
		self.updateDirection()
	
	
	def tick(self):
		self.floatCenter[0] += self.movingIndex[0]
		self.floatCenter[1] += self.movingIndex[1]
		self.setRotation(self.getRotation()+self.rotationSpeed)
		self.rect.center = self.floatCenter
		
		if (pygame.key.get_pressed()[119] == True or pygame.key.get_pressed()[273] == True):
			self.move("up")
		if (pygame.key.get_pressed()[115] == True or pygame.key.get_pressed()[274] == True):
			self.move("down")
		if (pygame.key.get_pressed()[97] == True or pygame.key.get_pressed()[276] == True):
			self.move("left")
		if (pygame.key.get_pressed()[100] == True or pygame.key.get_pressed()[275] == True):
			self.move("right")
		
		if (pygame.mouse.get_pressed()[0] == True):
			self.weapon.tick(True, self.getRotation())
		else:
			self.weapon.tick(False, None)
		
		
		if (pygame.key.get_pressed()[49]):
			self.weapon = Weapon("minigun")
		if (pygame.key.get_pressed()[50]):
			self.weapon = Weapon("energyBall")
		if (pygame.key.get_pressed()[51]):
			self.weapon = Weapon("sniper")
		if (pygame.key.get_pressed()[52]):
			self.weapon = Weapon("shotgun")
		
		if (self.invulnerabilityTimeout > 0):
			self.invulnerabilityTimeout -= 1
			if (self.invulnerabilityTimeout == 0):
				self.isRendered = True
				self.invulnerability = False
			else:
				if (self.invulnerabilityTimeout % 10 >= 5):
					self.isRendered = True
				else:
					self.isRendered = False
	
	
	def updateDirection(self):
		self.setRotation(getAngleFromPositions(self.getPosition(), pygame.mouse.get_pos()))
	
	
	def hit(self):
		if (self.invulnerability == True):
			return False
		self.destroy()
		return True
	
	
	def render(self, display):
		if (self.isRendered == True):
			display.blit(self.sprite, self.rect)
	
	
	def destroy(self):
		createExplosion(20, self.floatCenter, 80)
		global renderList
		global ship
		renderList.remove(self)
		ship = None


class Bullet(Sprite):
	def __init__(self, direction, speed, bulletSprite, removeOnImpact):
		# sprite
		self.original = pygame.image.load("sprites/"+str(bulletSprite)+".png").convert_alpha()
		self.sprite = self.original
		
		# rect
		global screen
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = speed
		self.rotationSpeed = 0
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		global ship
		self.floatCenter = [ship.floatCenter[0]+self.movingIndex[0], ship.floatCenter[1]+self.movingIndex[1]]
		self.lifetime = 0
		self.removeOnImpact = removeOnImpact
		self.setRotation(direction-90)
		
		global renderList
		global bulletsList
		renderList.append(self)
		bulletsList.append(self)
	
	
	def tick(self):
		self.floatCenter[0] += self.movingIndex[0]
		self.floatCenter[1] += self.movingIndex[1]
		self.setRotation(self.getRotation()+self.rotationSpeed)
		self.rect.center = self.floatCenter
		self.lifetime += 1
		if (self.lifetime > 150):
			self.destroy()
	
	
	def hit(self):
		if (self.removeOnImpact == True):
			self.destroy()
	
	
	def destroy(self):
		global renderList
		global bulletsList
		renderList.remove(self)
		bulletsList.remove(self)


class Asteroid(Sprite):
	def __init__(self, direction, speed, pos, rotationSpeed, size):
		# sprite
		self.original = pygame.image.load("sprites/asteroid"+str(size)+".png").convert_alpha()
		self.sprite = self.original
		
		# rect
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = speed
		self.rotationSpeed = rotationSpeed
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(pos)
		self.lifetime = 0
		self.size = size
		self.setRotation(direction-90)
		
		global renderList
		global asteroidsList
		renderList.append(self)
		asteroidsList.append(self)
	
	
	def tick(self):
		self.floatCenter[0] += self.movingIndex[0]
		self.floatCenter[1] += self.movingIndex[1]
		self.setRotation(self.getRotation()+self.rotationSpeed)
		self.rect.center = self.floatCenter
		self.lifetime += 1
		if (self.lifetime > 500):
			self.destroy(False)
			
	
	
	def destroy(self, division):
		global renderList
		global asteroidsList
		
		if (division == True):
			if (self.size > 1):
				Asteroid(self.rotation-90, self.speed, self.floatCenter, random.randint(-4, 4), self.size-1)
				Asteroid(self.rotation+90, self.speed, self.floatCenter, random.randint(-4, 4), self.size-1)
			createExplosion(12, self.floatCenter, 40)
		
		renderList.remove(self)
		asteroidsList.remove(self)


class Particle(Sprite):
	def __init__(self, direction, speed, pos, rotationSpeed, lifetime):
		# sprite
		self.original = pygame.image.load("sprites/particle.png").convert_alpha()
		self.sprite = self.original
		
		# rect
		self.rect = self.sprite.get_rect()
		
		# variables
		self.speed = speed
		self.rotationSpeed = rotationSpeed
		self.rad = math.radians((-direction)-90)
		self.movingIndex = (self.speed*math.cos(self.rad), self.speed*math.sin(self.rad))
		self.floatCenter = list(pos)
		self.life = 0
		self.lifetime = lifetime
		self.setRotation(direction-90)
		
		global renderList
		renderList.append(self)
	
	
	def tick(self):
		self.floatCenter[0] += self.movingIndex[0]
		self.floatCenter[1] += self.movingIndex[1]
		self.setRotation(self.getRotation()+self.rotationSpeed)
		self.rect.center = self.floatCenter
		self.life += 1
		if (self.life > self.lifetime):
			self.destroy(False)
			
	
	def destroy(self, division):
		global renderList
		renderList.remove(self)


class Weapon():
	def __init__(self, weaponType):
		with open("weapons.json", "r") as stats:
			self.stats = json.load(stats)[weaponType]
		self.timeout = self.stats["fireRate"]
		changeWeapon(weaponType)
	
	
	def tick(self, firing, direction):
		if (firing == False):
			if (self.timeout > 0):
				self.timeout -= 1
		else:
			if (self.timeout == 0):
				if (self.stats["multiShoot"] is not None):
					for i in range(self.stats["multiShoot"]["bulletsPerShoot"]):
						Bullet(direction+(self.stats["multiShoot"]["bulletsAngle"][i]), self.stats["speed"], self.stats["bulletSprite"], self.stats["removeOnImpact"])
				else:
					Bullet(direction, self.stats["speed"], self.stats["bulletSprite"], self.stats["removeOnImpact"])
				self.timeout = self.stats["fireRate"]
			else:
				self.timeout -= 1


class GUIWeapon():
	def __init__(self, name, pos):
		self.name = name
		self.unselectedSprite = pygame.image.load("sprites/GUI sprites/"+self.name+".png").convert_alpha()
		self.selectedSprite = pygame.image.load("sprites/GUI sprites/"+self.name+"Selected.png").convert_alpha()
		self.selected = False
		self.rect = self.selectedSprite.get_rect(left = pos, top = 5)
		
		global GUIWeaponsList
		GUIWeaponsList.append(self)
	
	
	def select(self):
		self.selected = True
	
	
	def unselect(self):
		self.selected = False
	
	
	def getID(self):
		return self.name
	
	
	def render(self, display):
		if (self.selected):
			display.blit(self.selectedSprite, self.rect)
		else:
			display.blit(self.unselectedSprite, self.rect)
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
	rotationSpeed = random.randint(-3, 3)
	sizeChooser = random.randint(1, 100)
	if (sizeChooser > 75):
		size = 3
	elif (sizeChooser > 65):
		size = 1
	else:
		size = 2
	Asteroid(direction, speed, pos, rotationSpeed, size)


def createExplosion(particleAmount, pos, lifetime):
	for i in range(particleAmount):
		Particle(random.randint(-180, 180), random.randint(1, 2), pos, 0, lifetime)


def getAngleFromPositions(point1, point2):
	return math.degrees(math.atan2(point1[0]-point2[0], point1[1]-point2[1]))


def changeWeapon(weaponID):
	for GUIWeapon in GUIWeaponsList:
		if (GUIWeapon.getID() == weaponID):
			GUIWeapon.select()
		else:
			GUIWeapon.unselect()
#--- /foctions ---#
#--- main ---#
FPS = 60

ctypes.windll.user32.SetProcessDPIAware()
os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("truc de l'espace")

random.seed()

# variables
renderList = list()
asteroidsList = list()
bulletsList = list()
GUIWeaponsList = list()

clock = pygame.time.Clock()
running = True
bulletTimeout = 0
asteroidTimeout = 0
count = 0
shipRespawnTimeout = 0

last = 0
current = 0

with open("weapons.json", "r") as stats:
	GUIWeaponID = json.load(stats)
GUIWeaponPos = 5
for k, _ in GUIWeaponID.items():
	GUIWeapon(k, GUIWeaponPos)
	GUIWeaponPos += 44

ship = Ship()

while (running):
	# events
	for event in pygame.event.get():
		if (event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
			running = False
		if (event.type == pygame.MOUSEMOTION):
			if (ship is not None):
				ship.updateDirection()
	
	if (asteroidTimeout == 0):
		createAsteroid()
		asteroidTimeout = 10
	else:
		asteroidTimeout -= 1
	
	# collision detection
	for bullet in bulletsList:
		laserHitIndex = bullet.rect.collidelist(asteroidsList)
		if (laserHitIndex >= 0):
			bullet.hit()
			asteroidsList[laserHitIndex].destroy(True)
	
	if (ship is not None):
		shipHitIndex = ship.rect.collidelist(asteroidsList)
		if (shipHitIndex >= 0):
			if (ship.hit()):
				asteroidsList[shipHitIndex].destroy(True)
				shipRespawnTimeout = 100
	else:
		shipRespawnTimeout -= 1
		if (shipRespawnTimeout == 0):
			ship = Ship()
			ship.updateDirection()
	
	
	# tick and render
	screen.fill((pygame.Color("black")))
	for sprite in renderList:
		sprite.tick()
		sprite.render(screen)
	[GUIWeapon.render(screen) for GUIWeapon in GUIWeaponsList]
	
	# screen refresh
	pygame.display.flip()
	
	# loop timer
	clock.tick_busy_loop(FPS)
pygame.quit()
#--- /main ---#