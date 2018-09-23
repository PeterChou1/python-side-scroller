import pygame
from pygame.locals import *
import random
import time
import math
import os

pygame.init()

#Font of the text in the game
myfont = pygame.font.SysFont("monospace", 15)
midfont = pygame.font.SysFont("monospace", 24)
bigfont = pygame.font.SysFont("monospace", 30)

#screen stuff
(width, height) = (640, 480)
half_width=width/2
half_height=height/2
screen = pygame.display.set_mode((width, height))
background = pygame.Surface((width, height)).convert()
background_colour = (255,255,255)
background.fill(background_colour)


#get all useful images
bullet_img = pygame.image.load('blackbox.png').convert()

char_img = pygame.image.load('mao_ze_dong.png').convert()
char_img.set_colorkey((255,255,255))

trump_img = pygame.image.load('trump.png').convert()
trump_img.set_colorkey((255,255,255))

washington_img = pygame.image.load('george_washington.png').convert()
washington_img.set_colorkey((255,255,255))

obama_img = pygame.image.load('obama.png').convert()
obama_img.set_colorkey((255,255,255))

hand_img = pygame.image.load('hand.png').convert()
hand_img.set_colorkey((255,255,255))

background_box = pygame.Surface((20, 20)).convert()
background_box.fill((255,255,255))
background_box.set_alpha(0)
#uncommented bottom line to test for platform collision
#background_box = pygame.image.load('box.png').convert()

grenade_img = pygame.image.load('grenade.png').convert()
grenade_img.set_colorkey((255,255,255))

# sound effect
ak_47 = pygame.mixer.Sound('AK_47_CS.ogg')
ak_47.set_volume(0.7)
grenade_sound=pygame.mixer.Sound('Grenade_Explosion.ogg')
grenade_sound.set_volume(0.7)
reload_sound=pygame.mixer.Sound('Reload_Sound_Effect.ogg')


# entities is the sprite group that consist of all the platforms, npc, players, and bullets #does not include background
#or constant entities
entities = pygame.sprite.Group()
# background entities contain all background images
background_entities = pygame.sprite.Group()
# entities that are not effected by camera movement
constant_entities = pygame.sprite.Group()
# player accessary entitiy (entity that contains all accessary that the player carries such as guns)
player_accessary = pygame.sprite.Group()




# below contains all class pertaining to the platform of the game
class make_platforms(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.y = y
        self.x = x
        self.img = img
        self.rect = Rect(x, y, 20, 20)

#exit blocks are blocks that player collide with to move on
class make_exitblock(pygame.sprite.Sprite):
    def __init__(self, x, y, img, exitcommand):
        pygame.sprite.Sprite.__init__(self)
        self.y = y
        self.x = x
        self.img = img
        self.rect = Rect(x, y, 20, 20)
        self.exitcommand = exitcommand #exit commands executes whenever the player hits the block

#the make_object class creates a basic object in the game to be displayed
class make_object(pygame.sprite.Sprite):
    def __init__(self, x, y, img):
        pygame.sprite.Sprite.__init__(self)
        self.y = y
        self.x = x
        self.img = img
        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y)

#All user interface classes
#health bar class
class health_bar(pygame.sprite.Sprite):
    def __init__(self, x, y, health_bar_x,health_bar_y):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.health_x=health_bar_x
        self.health_y=health_bar_y
        self.img=pygame.Surface((health_bar_x,health_bar_y))
        self.img.fill((0,255,255))#place holder replace with something else later
        self.rect=self.img.get_rect()
    def update_healthbar(self,health_bar_x):
        if health_bar_x>=0:
            self.img = pygame.Surface((health_bar_x, self.health_y))
            self.img.fill((0, 255, 255))
            self.rect=self.img.get_rect()
        else:
            self.img = pygame.Surface((0, self.health_y))
            self.img.fill((0, 255, 255))
            self.rect = self.img.get_rect()

#reload class
class reload_bar(pygame.sprite.Sprite):
    def __init__(self, x, y, ammo_count):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.img = myfont.render('Ammo count:'+str(ammo_count),True,(0,0,0))
    def update_reload_bar(self, updated_ammo):
        if updated_ammo==0:
            self.img = myfont.render('Ammo count: reloading...', True, (0, 0, 0))
        else:
            self.img = myfont.render('Ammo count:' + str(updated_ammo), True, (0, 0, 0))
#grenade count class
class grenade_count(pygame.sprite.Sprite):
    def __init__(self, x, y, number_of_grenade):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.img = myfont.render('Grenade count:'+str(number_of_grenade),True,(0,0,0))
    def update_grenade_bar(self, updated_grenade):
        if updated_grenade == 0:
            self.img = myfont.render('Grenades deserve better than a grenade spammer like you..', True, (0, 0, 0))
        else:
            self.img = myfont.render('Grenade count:' + str(updated_grenade), True, (0, 0, 0))
#score class
class score_bar(pygame.sprite.Sprite):
    def __init__(self, x, y, score):
        pygame.sprite.Sprite.__init__(self)
        self.x=x
        self.y=y
        self.img = myfont.render('{0:s} : {1:0>8d}'.format("score: ", score), True, (0, 0, 0))
    def update_score_bar(self, updated_score):
        self.img = myfont.render('{0:s} : {1:0>8d}'.format("score: ", updated_score), True, (0, 0, 0))


#camera class
#credit for creating the camera class user sloth from stackoverflow.com

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func #camera function is a function that updates all camera position
        self.state = Rect(0, 0, width, height)
    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l + half_width, -t + half_height

    l = min(0, l)  # stop scrolling at the left edge
    l = max(-(camera.width - width), l)  # stop scrolling at the right edge
    t = max(-(camera.height - height), t)  # stop scrolling at the bottom
    t = min(0, t)  # stop scrolling at the top

    return Rect(l, t, w, h)

# below contains all classes pertaining to characters (npc, and main_char)
#base character class
class character(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, image):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.img=image
        self.rect = image.get_rect()  # hitbox parameter for collision purposes
        self.rect.topleft = (x, y)
        self.speed=speed
        #default speed is a copy of speed for reseting the speed
        self.default_speed = speed
        self.angle=angle
        # 0 degree angle represent going upwards 180 goes down 270 goes left and 90 goes right
        if 0 <= self.angle <= math.radians(180):
            # self.face tells which way the character is facing
            self.face = 'right'
        if math.radians(181) <= self.angle <= math.radians(360):
            self.face = 'left'
        #check face checks if character dir has switch
        self.check_face = self.face
        self.on_ground=False#test for jump condition
    def move(self):
        if self.on_ground==False:#drag  and gravity only apply in the air
            (self.angle, self.speed) = addVectors(self.angle, self.speed, math.pi, gravity)
            self.speed *= drag
        if 0 <= self.angle <= math.radians(180):
            self.face = 'right'
        if math.radians(180) < self.angle <= math.radians(360):
            self.face = 'left'
        if self.face  == self.check_face:
            pass
        else:
            self.img = pygame.transform.flip(self.img, True, False)
            self.check_face = self.face
        self.x +=math.sin(self.angle) *self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.rect.left=self.x#moves rect
        self.rect.top=self.y

    def collision(self):
        for e in entities:
            if isinstance(e, make_platforms):
                if self.rect.colliderect(e.rect):
                    img_x = (self.img.get_width())
                    img_y = (self.img.get_height())
                    half_img_y = (self.img.get_height() / 2)
                    half_img_x = (self.img.get_width() / 2)
                    self.on_ground = False
                    if self.rect.center[1] - half_img_y < e.rect.center[1] < self.rect.center[
                        1] + half_img_y:  # change later to image height divide by 2
                        # x collision
                        if self.rect.midright[0] - e.rect.midright[0] < 0:
                            # right collision
                            # self.x is topleft so we need to minus image width
                            self.x = e.rect.midleft[0] - (self.rect.midright[0] - e.rect.midleft[0]) - img_x
                            self.angle = math.radians(360) - self.angle
                            self.rect.topleft = (self.x, self.y)
                            # self.speed *= elasticity ##for later use if needed
                        elif 0 < self.rect.midleft[0] - e.rect.midleft[0]:
                            # left collision
                            self.x = e.rect.midright[0] + (e.rect.midright[0] - self.rect.midleft[0]) + img_x
                            self.angle = math.radians(360) - self.angle
                            self.rect.topleft = (self.x, self.y)
                            # self.speed *= elasticity
                    if self.rect.center[0] - half_img_x < e.rect.center[0] < self.rect.center[
                        0] + half_img_x:  # change later to image width divide by 2
                        # y collision
                        if self.rect.midbottom[1] - e.rect.midbottom[1] < 0:
                            # print('up collision')
                            # up collision
                            if 0 <= self.angle <= math.radians(180):
                                self.angle = math.radians(90)
                            if math.radians(181) <= self.angle <= math.radians(360):
                                self.angle = math.radians(270)
                            self.y = e.y - (img_y - 1)
                            self.speed = self.default_speed
                            self.rect.topleft = (self.x, self.y)
                            self.on_ground = True
                        elif 0 < self.rect.midbottom[1] - e.rect.midbottom[1]:  # change later
                            # down collision
                            #self.y = e.rect.midbottom[1] + (e.rect.midbottom[1] - self.rect.midtop[1])
                            #more realistic simulation but also quite glitchy
                            self.y = e.rect.midbottom[1]
                            self.angle = math.radians(180) - self.angle
                            self.rect.topleft = (self.x, self.y)
                            # self.speed *= elasticity

#subclass of character
#npc class
class npc_char(character):
    def __init__(self, health, x, y, angle, speed, image, main_char, damage):
        character.__init__(self, x, y, angle, speed, image)
        self.health = health
        self.follow = main_char
        self.damage = damage
    def update(self):
        #if npc health is lower than zero delete it
        if self.health<=0:
            entities.remove(self)
            self.follow.score += 150
        #if npc goes out of map delete it
        if (self.x > total_level_width) or (self.x < 0) or (self.y > total_level_height) or (self.y < 0):
            entities.remove(self)
        #handles if npc is hit with a bullet
        if self.on_ground==True:
            if self.x - self.follow.x > 0:
                self.angle = math.radians(270)
            elif self.x - self.follow.x < 0:
                self.angle = math.radians(90)
            if self.follow.y < self.y:
                if self.follow.x > self.x:
                    self.angle = math.radians(45)
                elif self.follow.x < self.x:
                    self.angle = math.radians(315)
                else:
                    self.angle = 0
                self.on_ground = False
        if self.rect.colliderect(self.follow.rect):
            self.follow.health-=self.damage
        self.move()
        self.collision()

###gives npc class random attributes
def npc_give_random_attribute(number_of_npc, main_char, damage, speed, health, total_level_width, total_level_height):
    for npc in range(number_of_npc):
        x = random.randint(20, total_level_width)  # place_holder
        y = random.randint(20, total_level_height)
        angle = random.sample(set([math.radians(90), math.radians(270)]), 1)[0]  # give random direction
        zom_damage = random.randint(0, damage)
        zom_speed = random.randint(0, speed)
        zom_health = random.randint(0, health)
        #depending on damage select different appearances
        if zom_damage<10:
            zom_img = obama_img
        elif 50>zom_damage>10:
            zom_img = washington_img
        elif zom_damage>50:
            zom_img = trump_img
        else:
            zom_img = obama_img
        npc = npc_char(zom_health, x, y, angle, zom_speed, zom_img, main_char, zom_damage)
        npc.speed = random.randint(1, 10)  # gives npc random speed
        entities.add(npc)
# this class is resposible for spawning zombies periodically
class zom_rounds(object):
    def __init__(self, round_time):
        self.round_time = round_time
        self.default_round_time = round_time
        self.zom_health = 100
        self.zom_damage = 5
        self.zom_speed = 5
        self.zom_number = 10
        self.rounds = 0
    def update(self):
        self.round_time-=1
        round_number_text = myfont.render("Round: " + str(self.rounds), True, (0, 0, 0))
        screen.blit(round_number_text, (10, 120))
        if self.round_time == 0:
            self.round_time = self.default_round_time
            npc_give_random_attribute(self.zom_number, main_char, self.zom_damage, self.zom_speed, self.zom_health,
                                      total_level_width, 25)
            #whever there is a new round the zombies get progressively harder to kill
            self.rounds += 1 # adds new round number
            self.zom_health += 10 #gives zombie better health
            self.zom_damage += 5  #better damage
            self.zom_speed += 0 #faster speed
            self.zom_number += 2 #more zombie spawn after each round


#the class for the gun of the player
class gun_hand(pygame.sprite.Sprite):
    def __init__(self, x , y, main_char, hand=hand_img):
        pygame.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y

        self.master_img = hand
        self.img = hand

        self.rect = self.img.get_rect()
        self.rect.center = (x, y)

        self.body = main_char
        self.angle = 0

    def update(self):
        self.angle = -(math.degrees(find_mouse_angle(self)))
        self.img = pygame.transform.rotate(self.master_img, self.angle)
        self.rect = self.img.get_rect()
        self.rect.center=(self.body.rect.center[0],self.body.rect.center[1])


#main character class
class main_character(character):
    def __init__(self, ammo, reload_time, x, y, angle, speed,  moniter, grenade_count=200, image=char_img, status='alive', health=100, firing_speed=4):
        character.__init__(self, x, y, angle, speed, image)
        self.moniter = moniter

        self.health = health
        self.status = status

        self.ammo = ammo
        self.default_ammo = ammo

        self.grenade_count = grenade_count

        self.reload_time = reload_time
        self.default_reload_time = reload_time

        self.firing_speed = firing_speed# the speed of character bullets

        self.score = 0
        self.change_map = False #parameter used when changing maps
                                #protects character from being deleted

    def npc_collision(self):
        for e in entities:  # npc_collision
            if isinstance(e,npc_char):
                if self.rect.colliderect(e.rect) == True:
                    self.on_ground = False
                    (self.angle, self.speed) = addVectors(self.angle, self.speed, e.angle, e.speed)
                    self.x += math.sin(self.angle) * self.speed
                    self.y -= math.cos(self.angle) * self.speed
                    self.rect.left = self.x  # moves the rect
                    self.rect.top = self.y
                    self.speed *= drag

    def update(self):
        if self.health <= 0: #if char health reaches 0 moniter becomes dead screen
            entities.remove(self)

            if moniter == 'howtoplay':
                self.moniter = 'tutorialdeadscreen'

            if moniter == 'start':
                self.moniter = 'deadscreen'

        if self.change_map == False:

            if (self.x > total_level_width) or (self.x < 0) or (self.y > total_level_height) or (self.y < 0):
                entities.remove(self)

                if moniter == 'howtoplay':
                    self.moniter = 'tutorialdeadscreen'

                if moniter == 'start':
                    self.moniter = 'deadscreen'
        else:
            self.change_map = False

        key_press = pygame.key.get_pressed()
        if key_press[K_r]:#sets ammo to zero to trigger reload sequence reload button
            self.ammo = 0
        if self.on_ground == True:
            if key_press[K_LEFT] or key_press[K_a]:
                self.angle = math.radians(270)
                self.move()

            if key_press[K_RIGHT] or key_press[K_d]:
                self.angle = math.radians(90)
                self.move()

            if key_press[K_UP] or key_press[K_w]:
                self.on_ground = False
                self.angle = 0

        #handles jumping
        if self.on_ground == False:
            self.move()
            if self.angle == 0:
                if key_press[K_LEFT] or key_press[K_a]:
                    self.angle = math.radians(315)

                elif key_press[K_RIGHT] or key_press[K_d]:
                    self.angle = math.radians(45)

            if self.angle != 0:
                absdiff = abs(math.radians(180) - abs(self.angle))
                if key_press[K_LEFT] or key_press[K_a]:
                    self.angle = math.radians(180) + absdiff

                elif key_press[K_RIGHT] or key_press[K_d]:
                    self.angle = math.radians(180) - absdiff
        self.score+=1 #adds score
        self.collision() #handles platform collision
        self.npc_collision() #handles npc collision
        self.fire_projectile() #handles firing bullets
        self.generade_throw() #handles throwing grenades


    def fire_projectile(self):  #handles bullet firing
        if self.reload_time == 0:
            self.ammo = self.default_ammo
            self.reload_time = self.default_reload_time 
        elif self.ammo > 0:
            if pygame.mouse.get_pressed() == (1, 0, 0):
                pygame.mixer.Sound.play(ak_47)
                player_bullet = projectile(self.rect.center[0], self.rect.center[1], self.firing_speed, bullet_img)
                player_bullet.angle = find_mouse_angle(self)
                entities.add(player_bullet)
                self.ammo -= 1

        else:
            pygame.mixer.Sound.play(reload_sound) 
            self.reload_time -= 1#if ammo not = to 0 then start reload count down
    def generade_throw(self):
        if self.grenade_count>0:
            if pygame.mouse.get_pressed() == (0, 0, 1):
                player_gernade = grenade(self.rect.center[0],self.rect.center[1],self.firing_speed,
                                         bullet_img, grenade_img, 60) #self.default_reload_time)#temp solution fix later
                player_gernade.angle = find_mouse_angle(self)
                self.grenade_count -= 1
                entities.add(player_gernade)




########################################### all projectile and weapon class
class projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, img):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.master_img = img
        self.img = img
        self.rect = self.img.get_rect()  # hitbox parameter for collision purposes
        self.rect.topleft = (x, y)
        self.speed = speed
        self.angle = None

    def bullet_move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.rect.left = self.x  # moves the hit box rect
        self.rect.top = self.y

    def update(self):
        if (self.x > total_level_width) or (self.x < 0) or (self.y > total_level_height) or (self.y < 0):
            entities.remove(self)

        for e in entities:  # if bullet collides with collision entities
            if isinstance(e, npc_char) or isinstance(e, make_platforms):
                if self.rect.colliderect(e):
                    if isinstance(e, npc_char):
                        e.health -= 10
                        (e.angle, e.speed) = addVectors(self.angle, self.speed, e.angle, e.speed)
                    entities.remove(self)
                    #entities.remove(e)

            else:
                self.bullet_move()
# generade projectile subclass of projectile class
class grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, frag_image, grenade_image, timer):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y

        self.speed = speed

        self.frag_img = frag_image
        self.img = grenade_image
        self.master_img =grenade_image

        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y)

        self.timer = timer

    def generade_move(self):
        (self.angle, self.speed) = addVectors(self.angle, self.speed, math.pi, gravity)
        self.speed *= drag
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed
        self.rect.left = self.x  # moves rect
        self.rect.top = self.y
        self.generade_collision()

    def update(self):
        self.img = pygame.transform.rotate(self.master_img, -math.degrees(self.angle))
        self.rect = self.img.get_rect()
        self.rect.center = (self.rect.center[0], self.rect.center[1])

        if (self.x > total_level_width) or (self.x < 0) or (self.y > total_level_height) or (self.y < 0):
            entities.remove(self)

        if self.timer == 0:#if timer=0 explode
            for frag_angle in range(0 , 360, 20):
                pygame.mixer.Sound.play(grenade_sound)
                fragments = projectile(self.x, self.y, self.speed, self.frag_img)
                fragments.angle = frag_angle
                entities.add(fragments)
            entities.remove(self)

        else:
            self.generade_move()
            self.timer-=1
    def generade_collision(self):
        #grenade collision similar to character collision only the object
        #will not stop when hitting the ground
        for e in entities:
            if isinstance(e, make_platforms):
                if self.rect.colliderect(e.rect):
                    img_x = (self.img.get_width())
                    img_y = (self.img.get_height())
                    half_img_y = (self.img.get_height() / 2)
                    half_img_x = (self.img.get_width() / 2)
                    if self.rect.center[1] - half_img_y < e.rect.center[1] < self.rect.center[
                        1] + half_img_y:  # change later to image height divide by 2
                        # x collision
                        if self.rect.midright[0] - e.rect.midright[0] < 0:
                            # right collision
                            self.x = e.rect.midleft[0] - (self.rect.midright[0] - e.rect.midleft[0]) - img_x
                            self.angle = math.radians(360) - self.angle
                            self.rect.topleft = (self.x, self.y)

                            self.speed *= elasticity
                        elif 0 < self.rect.midleft[0] - e.rect.midleft[0]:
                            # left collision
                            self.x = e.rect.midright[0] + (e.rect.midright[0] - self.rect.midleft[0]) + img_x
                            self.angle = math.radians(360) - self.angle
                            self.rect.topleft = (self.x, self.y)
                            self.speed *= elasticity

                    if self.rect.center[0] - half_img_x < e.rect.center[0] < self.rect.center[
                        0] + half_img_x:
                        # y collision
                        if self.rect.midbottom[1] - e.rect.midbottom[1] < 0:
                            #up collision
                            self.y = e.rect.midtop[1] - (self.rect.midbottom[1] - e.rect.midtop[1]) - img_y
                            self.angle = math.radians(180) - self.angle
                            self.rect.topleft = (self.x, self.y)
                            self.speed *= elasticity

                        elif 0 < self.rect.midbottom[1] - e.rect.midbottom[1]:  # change later
                            # down collision
                            self.y = e.rect.midbottom[1] + (e.rect.midbottom[1] - self.rect.midtop[1])
                            self.angle = math.radians(180) - self.angle
                            self.rect.topleft = (self.x, self.y)
                            self.speed *= elasticity



#misc func

def log_highscore(main_char):# handles score logging
    log = open("highscore log.txt", "r+")
    newlog = open("highscore log2.txt", "w+")
    highscores = log.readlines()
    score_counter = 0
    for score in highscores:  # highscore
        score = score.split("\\")
        if main_char.score > int(score[0]):
            score_passed = score[0]
            score_counter += 1
    log.close()
    if score_counter > 0:
        deleteLine = True
        for score in highscores:
            if deleteLine == True:
                deleteLine = False
            else:
                score = score.split("\\")
                if score[0] == score_passed:
                    if score_counter == 10:
                        newlog.write(score[0]+"\n")
                        newlog.write(str(main_char.score))
                    else:
                        newlog.write(score[0])
                        newlog.write(str(main_char.score) + "\n")
                else:
                    newlog.write(score[0])
        newlog.close()
        log = open("highscore log.txt", "w+")
        newlog = open("highscore log2.txt", "r+")
        new_highscores = newlog.readlines()
        for newscores in new_highscores:
            newscores = newscores.split("!!")
            log.write(str(newscores[0]))
    log.close()
    newlog.close()

def addVectors(angle1, length1, angle2, length2):
    x  = math.sin(angle1) * length1 + math.sin(angle2) * length2
    y  = math.cos(angle1) * length1 + math.cos(angle2) * length2
    length = math.hypot(x, y)
    angle = 0.5 * math.pi - math.atan2(y, x)
    return (angle, length)

def find_mouse_angle(target): #finds the mouse angle relative to the y axis
    x = pygame.mouse.get_pos()[0]
    y = pygame.mouse.get_pos()[1]
    target_x=target.rect.center[0]-abs(camera.state.topleft[0])
    target_y=target.rect.center[1]-abs(camera.state.topleft[1])
    try:
        angle = math.atan(abs(x - target_x) / abs(target_y - y))  # gets first quadrant angle
    except ZeroDivisionError:##this prevents tan(90) leading to errors
        angle = math.radians(90)

    if x > target_x:
        if y < target_y:  # quadrant 1
            pass
        elif y > target_y:  # quadrant 4
            angle = math.radians(180) - angle

    elif x < target_x:
        if  y < target_y:  # quadrant 2
            angle = math.radians(360) - angle
        elif  y > target_y:  # quadrant 3
            angle = math.radians(180) + angle

    elif int(x)==int(target_x):#if  angle is exactly 0 or 180 degrees
        if y < target_y:  # quadrant 1
            angle=0
        elif y > target_y:  # quadrant 4
            angle = math.radians(180)

    elif int(y)==int(target_y):#if  angle is exactly 90 or 270 degrees
        if x > target_x:
            angle=math.radians(90)
        if x < target_x:
            angle = math.radians(270)
    return(angle)



#####screen def func

def menu():# function that handles bliting menu screen
    #load images
    img = pygame.image.load("greybox.png").convert()
    img2 = pygame.image.load("start.png").convert()
    img3 = pygame.image.load("how to play.png").convert()
    img4 = pygame.image.load("Highscores2.png").convert()
    img5 = pygame.image.load('background.png').convert()
    #blit onto screen
    screen.blit(img5, (0, 0))
    screen.blit(img, (200,140))
    screen.blit(img2,(220,150))
    screen.blit(img3,(220,210))
    screen.blit(img4,(220,270))

def highscore(): # function that handles bliting highscore screen
    #loads highscore background
    img = pygame.image.load('highscore_menu.png').convert()
    img2 = pygame.image.load("backtomenu.png").convert()
    #blit onto screen
    screen.blit(background,(0,0))
    screen.blit(img,(0,0))
    screen.blit(img2,(0,440))

def load_highscore():# function that loads highscore information onto highscore screen
    highscore = open('highscore log.txt', 'r+')
    x = 50
    y = 400
    scores = highscore.readlines()
    score_counter = 10
    for score in scores:
        score = score.split('\n')
        onscreen_score = myfont.render(str(score_counter) + ': ' + str(score[0])+' points', True, (0, 0, 0))
        screen.blit(onscreen_score, (x, y))
        y -= 30
        score_counter -= 1
    highscore.close()

def deadscreen(): # function that loads dead screens when character dies
    #loads images
    img = pygame.image.load("deadscreen.png").convert()
    img2 = pygame.image.load( "backtomenu.png").convert()
    #finds out if score is higher than the 10 highscore in highscore log
    highscore = open("highscore log.txt", "r+")
    scores = highscore.readline()
    if main_char.score > int(scores):
        if main_char.moniter =='deadscreen':
            deadtext = bigfont.render('New Highscore Good Job!!', True, (255, 255,  255))

        elif main_char.moniter =='tutorialdeadscreen':
            deadtext = myfont.render('You beat your highscore in the tutorial!', True, (255, 255, 255))

    else:
        if main_char.moniter == 'deadscreen':
            deadtext = bigfont.render('You Suck!!', True, (255, 255, 255))

        elif main_char.moniter == 'tutorialdeadscreen':
            deadtext = myfont.render('You some how figured out how to die in the tutorial', True,
                                      (255, 255, 255))

    scoretext = midfont.render('Your score is ' + str(main_char.score) + " points", True, (255, 255,  255))
    log_highscore(main_char)
    screen.blit(background, (0,0))
    screen.blit(img, (0,0))
    screen.blit(img2, (0,440))
    screen.blit(deadtext, (100,100))
    screen.blit(scoretext, (100, 150))

def construct_howtoplay():#function that constructs the tutorial
    #first make background images
    howtoplay = make_object(0, 0, pygame.image.load("how to play_background.png").convert())
    background_entities.add(howtoplay)
    backtomenu = make_object(0,440,pygame.image.load("backtomenu.png").convert())
    constant_entities.add(backtomenu)
    # constructs the tutorial
    tutorial = ['PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                              PPPPPPPPPPPPPPPP    P',
                'P                                                  P',
                'P                                                  P',
                'P                                                  P',
                'P                                                 EP',
                'P                                                  P',
                'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP'
                ]
    x = 0
    y = 0

    def exitcommand(): #when player hits the exitblock this function will execute assigning an command to exit block
        moniter = 'menu'
        entities.empty()
        background_entities.empty()
        constant_entities.empty()
        player_accessary.empty()
        construct = 'construct_main_structure_init'
        return moniter, construct

    for row in tutorial:
        for col in row:
            if col == "P":
                col = make_platforms(x, y, background_box)
                entities.add(col)
            if col == "E":
                col = make_exitblock(x, y, background_box, exitcommand)
                entities.add(col)
            x += 20
        y += 20
        x = 0

    total_level_height = len(tutorial) * 20
    total_level_width = len(tutorial[0]) * 20

    # camera
    camera = Camera(complex_camera, total_level_width, total_level_height)

    # setup charcteristic for main character<-----------------------------------
    main_char = main_character(200, 120, 100, 100, math.radians(180), 8, 'howtoplay')
    entities.add(main_char)
    #set up the gun the player is holding
    main_hand = gun_hand(main_char.rect.center[0], main_char.rect.center[1],main_char)
    player_accessary.add(main_hand)

    #set up all user interface
    player_grenade_count = grenade_count(10, 80, main_char.grenade_count)
    constant_entities.add(player_grenade_count)
    player_health = health_bar(10, 10, main_char.health, 20)
    constant_entities.add(player_health)
    player_reload_bar = reload_bar(10, 40, main_char.ammo)
    constant_entities.add(player_reload_bar)
    player_score = score_bar(450, 15, main_char.score)
    constant_entities.add(player_score)

    return camera, player_grenade_count, player_score, player_health, player_reload_bar,\
           main_char, total_level_width, total_level_height
def construct_start():
    start = make_object(0, 0, pygame.image.load("start_map.png").convert())
    background_entities.add(start)
    backtomenu = make_object(0, 440, pygame.image.load("backtomenu.png").convert())
    constant_entities.add(backtomenu)

    if construct == 'construct_main_structure_init':# initial construction of start
        # setup charcteristic for main character<-----------------------------------
        main_char = main_character(200, 120, 100, 100, math.radians(180), 8, 'start')
        entities.add(main_char)

    if construct == 'construct_main_structure_while_playing': # reconstruct start if player exits secondary area
        for e in entities:
            if isinstance(e, main_character):
                main_char = e #reassign main character

    main_hand = gun_hand(main_char.rect.center[0], main_char.rect.center[1], main_char)
    player_accessary.add(main_hand)

    player_health = health_bar(10, 10, main_char.health, 20)
    constant_entities.add(player_health)

    player_reload_bar = reload_bar(10, 40, main_char.ammo)
    constant_entities.add(player_reload_bar)

    player_grenade_count = grenade_count(10, 80, main_char.grenade_count)
    constant_entities.add(player_grenade_count)

    player_score = score_bar(450, 15, main_char.score)
    constant_entities.add(player_score)
    # constructs the start
    game_map = ['PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                 PP                                                                                                                                   P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                          PPPPPPPPPPPPPPP                                                                                                                             P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                   PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP                                                                                                       P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                  PPPPPPPPPPP                                                                          PPPPPPPPPPP                                                                                    P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                                                                                                                                                                      P',
                'P                                                                                                           E             E                                                                                                                            P',
                'P                                                                                                                                                                                                                                                      P',
                'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
                'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP'
                ]

    x = 0
    y = 0
    #there are two exit command for hiting two different exitblock
    def exitcommand1():
        entities.empty()
        main_char.rect.x = 240
        main_char.rect.y = 380
        main_char.x = 240
        main_char.y = 380
        main_char.change_map = True
        entities.add(main_char)

        background_entities.empty()
        construct = 'construct_secondary_structure'
        moniter = 'start'
        return  moniter, construct
    def exitcommand2():
        entities.empty()
        main_char.rect.x = 2780
        main_char.rect.y = 380
        main_char.x = 2780
        main_char.y = 380
        main_char.change_map = True
        entities.add(main_char)

        background_entities.empty()
        construct = 'construct_secondary_structure'
        moniter = 'start'
        return moniter, construct
    exit_list = [exitcommand1, exitcommand2]
    exit_counter = 0
    for row in game_map:
        for col in row:
            if col == "P":
                col = make_platforms(x, y, background_box)
                entities.add(col)
            if col == "E":
                col = make_exitblock(x, y, background_box, exit_list[exit_counter])
                exit_counter += 1
                entities.add(col)
            x += 20
        y += 20
        x = 0
    total_level_height = len(game_map) * 20
    total_level_width = len(game_map[0]) * 20
    # sets up camera class
    camera = Camera(complex_camera, total_level_width, total_level_height)

    return camera, player_grenade_count, player_score, player_health, player_reload_bar,\
           main_char, total_level_width, total_level_height
def construct_shack():
    shack_img = make_object(0, 0, pygame.image.load("shack.png").convert())
    background_entities.add(shack_img)
    # constructs the start
    shack = ['PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
             'P                             P                                                                                           P                             P',
             'P                             P                                                                                           P                             P',
             'P                             P                                                                                           P                             P',
             'P                                                                                                                                                       P',
             'P                                                                                                                                                       P',
             'P                                                                                                                                                       P',
             'P                                                                                                                                                       P',
             'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP               PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP              PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
             'P                             P                                                                                           P                             P',
             'P                                                                                                                                                       P',
             'P                                                                                                                                                       P',
             'P                                                                                                                                                       P',
             'P                                                                                                                                                       P',
             'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP        PPPPPPPPPPPPPPPPPPPPP        PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP',
             'P                                                                PP                     PP                                                              P',
             'P                                                               P                         P                                                             P',
             'P                                                              P                           P                                                            P',
             'P                                                             P                             P                                                           P',
             'P                                                            P                               P                                                          P',
             'P         E                                                 P                                 P                                              E          P',
             'P                                                          P                                   P                                                        P',
             'P                                                         P                                     P                                                       P',
             'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP']
    x = 0
    y = 0
    def exitcommand1():
        entities.empty()
        main_char.rect.x = 2120#sets spawn point for npc after exiting shack
        main_char.rect.y = 420
        main_char.x = 2120
        main_char.y = 420
        main_char.change_map = True
        entities.add(main_char)
        background_entities.empty()
        constant_entities.empty()
        construct = 'construct_main_structure_while_playing'
        moniter = 'start'
        return moniter, construct
    def exitcommand2():
        entities.empty()
        main_char.rect.x = 2720  # sets spawn point for np
        main_char.rect.y = 420
        main_char.x = 2580
        main_char.y = 420
        main_char.change_map = True
        entities.add(main_char)
        background_entities.empty()
        constant_entities.empty()
        construct = 'construct_main_structure_while_playing'
        moniter = 'start'
        return moniter, construct

    exit_list = [exitcommand1, exitcommand2]
    exit_counter = 0
    for row in shack:
        for col in row:
            if col == "P":
                col = make_platforms(x, y, background_box)
                entities.add(col)
            if col == "E":
                col = make_exitblock(x, y, background_box, exit_list[exit_counter])
                exit_counter += 1
                entities.add(col)
            x += 20
        y += 20
        x = 0
    total_level_height = len(shack) * 20
    total_level_width = len(shack[0]) * 20

    # camera
    camera = Camera(complex_camera, total_level_width, total_level_height)
    # setup charcteristic for main character<-----------------------------------
    return camera, player_grenade_count, player_score, player_health, player_reload_bar,\
           main_char, total_level_width, total_level_height


#defines where the screen is currently at
moniter = "menu"
#air resistance
drag=0.999
#energy loss after hitting ground
elasticity = 0.90
#gravity effect
gravity=0.2

#framerate
framerate = pygame.time.Clock()
#game_loop parameter
game_open = True

#parameter for constructing levels
construct= 'construct_main_structure_init'

while game_open:
    framerate.tick(30)
    if moniter == ('howtoplay') or moniter == ('start'):
        if moniter =='howtoplay':
            if construct == 'construct_main_structure_init':
                camera, player_grenade_count, player_score, player_health, player_reload_bar, \
                main_char, total_level_width, total_level_height = construct_howtoplay()
        if moniter == 'start':
            if construct == 'construct_main_structure_init' or construct == 'construct_main_structure_while_playing':
                camera, player_grenade_count, player_score, player_health, player_reload_bar, \
                main_char, total_level_width, total_level_height = construct_start()
                if construct == 'construct_main_structure_init':
                    zombie_rounds = zom_rounds(300)
            if construct == 'construct_secondary_structure':
                camera, player_grenade_count, player_score, player_health, player_reload_bar, \
                main_char, total_level_width, total_level_height = construct_shack()
        construct=None
        moniter = main_char.moniter#this ensures that when the character dies the dead screen will appear

        for e in background_entities:
            screen.blit(e.img, camera.apply(e))

        for e in constant_entities:#move all constant entity with the camera
            screen.blit(e.img, (e.x, e.y))

        for e in entities:#moves all entities with camera
            screen.blit(e.img, camera.apply(e))
            if isinstance(e,make_exitblock):# exits the tutorial if player hits exitblock
                if e.rect.colliderect(main_char.rect):
                     moniter, construct = e.exitcommand()

        for e in player_accessary:#updates player_accessaries
            screen.blit(e.img, camera.apply(e))
        #update all entity
        entities.update()
        #update player gun
        player_accessary.update()

        #updates player user interface
        player_grenade_count.update_grenade_bar(main_char.grenade_count)
        player_health.update_healthbar(main_char.health)
        player_reload_bar.update_reload_bar(main_char.ammo)
        player_score.update_score_bar(main_char.score)

        #updates camera movement for character
        camera.update(main_char)

        if moniter == 'start':
            zombie_rounds.update()#update zombie rounds to spawn more zombie in start

    for ev in pygame.event.get():
        if ev.type == KEYDOWN:
            if ev.key == K_ESCAPE:
                game_open=False

        elif ev.type == pygame.QUIT:
            game_open=False

        if moniter == 'deadscreen' or moniter == 'tutorialdeadscreen':
            entities.empty()
            background_entities.empty()
            constant_entities.empty()
            player_accessary.empty()
            deadscreen()
            moniter = None # by setting the moniter to None value it prevents the screen from
                           # blitting the screen multiple times when only one is needed

        if moniter == 'highscore':
            highscore()
            load_highscore()
            moniter = None

        if moniter != 'menu':
            # back to menu
            if ev.type == MOUSEBUTTONDOWN:
                x = ev.pos[0]
                y = ev.pos[1]
                if 580 < x < 640 and 440 < y < 480:
                    #if player clicks backtomenu button empty all entities
                    entities.empty()
                    background_entities.empty()
                    constant_entities.empty()
                    player_accessary.empty()
                    # set construct to true to reconstruct the levels
                    construct = 'construct_main_structure_init'
                    moniter = "menu"
        elif moniter=='menu':
                #main menu
                menu()
                if ev.type == MOUSEBUTTONDOWN:
                    x=ev.pos[0]
                    y=ev.pos[1]
                    if 380>x>220:
                        if 200>y>150:# if player click start button
                            moniter = 'start'
                        elif 260>y>210:# if player click howtoplay button
                            moniter = "howtoplay"
                        elif 320>y>220:# if player click highscore button
                            moniter = "highscore"
    pygame.display.flip()
pygame.quit()
