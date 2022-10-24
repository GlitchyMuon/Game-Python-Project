from queue import LifoQueue
import pgzrun
from pgzhelper import *
from random import randint, choice
from os import listdir
from os.path import isfile
import pygame
#from pgzero.actor import Actor



WIDTH = 1440
HEIGHT = 900
ROTATION_SPEED = 80
WHITE = 255, 255, 255
BOX = Rect((15, 100, 200, 50))


game_over = False
score = 0
# pour les différents scores, p-e que je devrais faire des sous-dossiers, et faire un dirlist.
malus = 300
combo = 0
food_value_score_visible = False
enemy_value_score_visible = False
pause = False
fullscreen = True


background = Actor("space_planet_left")


# *** player ***
class Player(Actor):
    def __init__(self):
        super().__init__("nibbler_idle", anchor= ['center', 'bottom'])
        self.pos = [WIDTH/2, HEIGHT]
        self.life = 1800

player = Player()

# *** food ***
food_time = 0
food_list = []
foodnames = [] # les fichiers
for food_file in listdir(r'images/all_food'):
    if isfile(r'images/all_food/' + food_file):
        foodnames.append(food_file)

food_speed = [0, 240] # 0 en x car ne va ni vers la gauche(-n) ni droite(n positif). En y nombre positif car va vers le bas. Si négatif, va vers le haut

#*** Enemy = Fotran Beer ***
enemy_time = randint(10, 15) # temps avant le premier
enemy_list = []
enemy_speed = [0, 240]


# *** Enemy Action = Bender ***
enemy_action = Actor("bender_idle", anchor=['center', 'bottom'])
enemy_action.pos = [WIDTH -66, HEIGHT]
enemy_action_visible = False

# *** Enemy trigger = wrench ***
enemy_action_trigger = Actor("wrench_resized")
enemy_action_trigger_visible = False
enemy_action_trigger_maxspeed = 350
enemy_action_trigger_speed = [-enemy_action_trigger_maxspeed, 0]
enemy_action_trigger_time = 0


# *** darkmatter poop ***

poop = Actor("darkmatter_rotated", anchor= ['center', 'bottom'])
poop_visible = False

class Ship : # ou Ship(Actor)
    def __init__(self):
        self.sprite=Actor('planet_express', anchor= ['right', 'top'])   #super().__init__('planet_express', anchor= ['right', 'top'])
        self.sprite.scale = 0.33    # pas besoin de mettre 'sprite.' si méthode héritage
        self.sprite.pos = (WIDTH, 0)
        self.direction = [-1, 0]
        self.speed = 10
        self.boostspeed = 30
        self.boostspeed_timer = 0
        self.move_timer = 0
        self.burstflamesprite = Actor('small_burst', anchor=['left','top'])
        self.burstflamesprite.pos = (self.sprite.pos[0], 0)
    
    
    def move(self, dt):
        if self.move_timer > 0 :
            self.move_timer -= dt

            x = self.sprite.pos[0] + self.speed * self.direction[0] * dt
            y = self.sprite.pos[1] + self.speed * self.direction[1] * dt
            self.sprite.pos = [x , y]
            

    def draw(self):
        self.sprite.draw()
        
    def decelerate(self):
        self.speed /= 2
        self.boostspeed /= 2
        

ship = Ship() #crée l'instance


# *** functions ***

def draw(): # ce qui est dans le draw, ne doit que draw. On peut mettre des if (pas gérer de collision, ni update)
    global food # mis la variable globale, car error de call before assignement de food

    # si je veux fullscreen sans pouvoir en sortir :    screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    
    #    if game_over:
        #screen.clear()
        #screen.draw.text('Game Over', (350,270), color=(255,255,255), fontsize=30)
        #screen.draw.text('Score: ' + str(round(score)), (350,330), color=(255,255,255), fontsize=30)
    #else:

    # fullscreen dans le draw absolument 
    if fullscreen:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT))

    screen.clear() # à mettre dans le if game_over
    # screen.fill((1, 7, 46)) si pas de background
    background.draw()
    screen.draw.text(f"F11 : Fullscreen\nESC : Exit Fullscreen\nPause : Spacebar", (10, 15), color=(255,255,255), fontsize=15)
    screen.draw.rect(BOX, WHITE)
    screen.draw.textbox(str(score), (15, 100, 200, 50), color=(255,255,255), gcolor="green")
    
    if poop_visible:
        poop.draw()
    # si je veux qu'il apparaisse derrière le player, il faut qu'il soit draw avant le player. Car dans le draw, les derniers élements superposent les précédents


    player.draw()
    ship.draw()
   # player.life.draw()

    for food in food_list: 
        food.draw()
    
    for enemy in enemy_list:
        enemy.draw()

    # *** bender appear (ennemy_action)***
    if enemy_action_visible:
        enemy_action.draw()
        enemy_action_trigger.draw()

    # *** game pause ***
    if pause == True :
        screen.draw.text("Game Paused", center=(WIDTH/2, HEIGHT/2), color="cyan", gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=100, fontname="ocraext")

    # *** Scoring draw ***
    # *** global score ***
    if food_value_score_visible: 
        screen.draw.text("100", center=((player.pos[0]+30), (player.pos[1]-player.height-10)), color="white",gcolor="yellow", fontsize= 35)

    # *** hurt score *** 
    if enemy_value_score_visible:
        screen.draw.text("-200", center=((player.pos[0]+30), (player.pos[1]-player.height-10)), color="white", gcolor="red", fontsize= 35)

def random_pos():
    image_width = 64 # food sprite size
    image_heigth = 64
    modifier = max(image_width, image_heigth) // 2
    x = randint(modifier, WIDTH - 200) # pas WIDTH- modifier car ici on veut que le food s'arrête aussi WIDTH-200 comme le player, pour qu'il puisse manger tout, et que ça n'aparaisse pas là où Bender apparaîtra
    y = 0
    return [x, y]


def random_pos_enemy():
    image_width = 105 # beer sprite size
    image_heigth = 105
    modifier = max(image_width, image_heigth) // 2
    x = randint(modifier, WIDTH - 200)
    y = 0
    return [x, y]


def food_update(dt):  #delta time = (la différence de temps) le temps qui s'est passé depuis la précédente update (1/60e de seconde)
    global food_time, food, score, food_value_score_visible, enemy_value_score_visible, combo

    food_time -= dt # dt = changement du temps
    if food_time <= 0.0: # quand le sablier est vide ou en dessous de 0
        food = Actor('all_food/' + choice(foodnames), anchor= ['center', 'top']) # à mettre dans update
        food.pos = random_pos()
        food_list.append(food)
        food_time = randint(1,3)
        pos= food.pos

    # *** collision with player and/or bottom screen ***
    mvt_x = food_speed[0] * dt #* 1/60e de sec
    mvt_y = food_speed[1] * dt

    # *** ok food collision with player ***

    for food in food_list :
        food.pos = [food.pos[0] + mvt_x, food.pos[1] + mvt_y]

        if player.colliderect(food): 
            food_list.remove(food)
            sounds.munch.play()
            score += 100
            food_value_score_visible = True
            clock.schedule_interval(set_food_value_score, 0.7)
            ship.move_timer = 1
            combo += 1
            # if combo % 3 == 0 :   règle si par incrémentation de 3
            # sinon que des if elif
                

    # *** darkmatter generating ***
            set_player_eat_then_poop()

        elif food.pos[1] >= HEIGHT -10:
            food_list.remove(food)
            # pas de break car dans le casse-brique, touche une brique à la foi, ici, plusieurs food peuvent collide


def enemy_update(dt):
    global enemy_time, enemy, score, enemy_value_score_visible, enemy_action_trigger_visible, enemy_action_trigger_speed, malus

    enemy_time -= dt 
    if enemy_time <= 0.0:
        enemy = Actor("fortran_beer", anchor=['center', 'top'])
        enemy.pos = random_pos_enemy()
        enemy_list.append(enemy)
        enemy_time = randint(5,10) #ne fonctionne pas, apparait direct !
        pos = enemy.pos

      # *** enemy collision with player ***
    mvt_x = enemy_speed[0] * dt
    mvt_y = enemy_speed[1] * dt

    for enemy in enemy_list :
        enemy.pos = [enemy.pos[0] + mvt_x, enemy.pos[1] + mvt_y]        
        if player.colliderect(enemy):
            enemy_list.remove(enemy)
            sounds.glug_glug_glug.play()
            score -= malus
            set_enemy_action_animate()
            enemy_value_score_visible = True
            clock.schedule_interval(set_enemy_value_score, 0.7)
            enemy_action_trigger_visible = True
            enemy_action_trigger_speed = [-enemy_action_trigger_maxspeed,0]
            enemy_action_trigger.pos = [WIDTH -66, HEIGHT-player.height]
        if enemy.pos[1] >= HEIGHT -10:
            enemy_list.remove(enemy)

def enemy_action_trigger_update(dt):
    global enemy_action_trigger, enemy_action_trigger_speed, enemy_action_trigger_visible, enemy_action_trigger_time, ROTATION_SPEED

    mvt_x = enemy_action_trigger_speed[0] * dt
    mvt_y = enemy_action_trigger_speed[1] * dt
    enemy_action_trigger.angle += ROTATION_SPEED * dt

    enemy_action_trigger.pos = [enemy_action_trigger.pos[0] + mvt_x, enemy_action_trigger.pos[1] + mvt_y]
    if player.colliderect(enemy_action_trigger):
        #enemy_action_trigger_visible = False
        sounds.slap_umph.play()
        enemy_action_trigger_speed = [0,enemy_action_trigger_maxspeed]
        


def update(dt):
    # quand j'aurais défini les conditions de game over :
    # global score, game_over
    # if game_over:
    #   return

    if pause :
        return

    if dt > 0.5 :
        return

    pos = player.pos
    if pos[0] > WIDTH -5:
        pos[0] = WIDTH -5
    elif pos[0] < 5:
        pos[0] = 5
        
    if pos[1] > WIDTH -5:
        pos[1] = WIDTH -5
    elif pos[1] < 5:
        pos[1] = 5
    
    pos = player.pos

    food_update(dt)
    enemy_update(dt)
    if enemy_action_trigger_visible == True:
        enemy_action_trigger_update(dt)
    ship.move(dt)

def on_mouse_move(pos): 
    if pos[0] > 50 and pos[0] < WIDTH - 200 : #largeur et hauteur sprite = 296
        x = pos[0]
    elif pos[0] <= 50:
        x = 50
    else :
        x = WIDTH - 200 # calcul : 50 est la moitié du sprite player. 130 est la taille approximatif du sprite de Bender/ennemy. 50 + 130 + 20 de marges = 200

    y = player.pos[1]
    player.pos = [x, y]


def on_key_down(key):
    global pause, fullscreen

    if key == keys.F11:
        fullscreen = not fullscreen
       
    elif key == keys.ESCAPE:
        exit()

    elif key == keys.SPACE:
        pause = not pause
        

def set_enemy_action_animate():
    global enemy_action_visible
    enemy_action.image = 'bender_yay'
    enemy_action.image = 'bender_action'
    clock.schedule_interval(set_enemy_action_normal, 0.7)
    enemy_action_visible = True
    enemy_action.pos = (WIDTH-66, HEIGHT)
    clock.schedule_interval(set_enemy_action_invisible, 1) 


def set_enemy_action_normal():
    enemy_action.image = 'bender_idle'
    

def set_player_eat_then_poop():
    global poop_visible
    player.image = 'nibbler_yay'
    clock.schedule_interval(set_player_normal, 1)
    poop_visible = True
    poop.pos = (player.pos[0] -100, player.pos[1])  # WIDTH/2 -30, HEIGHT-5


def set_player_normal():
    player.image = 'nibbler_idle'


def set_food_value_score():
    global food_value_score_visible
    food_value_score_visible = False


def set_enemy_value_score():
    global enemy_value_score_visible
    enemy_value_score_visible = False

def set_enemy_action_invisible():
    global enemy_action_visible
    enemy_action_visible = False
    # là il disparait trop abruptement : amélioration -> le déplacer hors de l'écran et le faire remove.


    

pgzrun.go()