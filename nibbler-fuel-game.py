
import pgzrun
from random import randint, choice
from os import listdir
from os.path import isfile
import pygame


WIDTH = 1024
HEIGHT = 768

score = 0

# *** player ***

player = Actor("nibbler_idle", anchor= ['center', 'bottom']) # center, bottom serait mieux ? ou bottom, middle ?
player.pos = [WIDTH/2, HEIGHT]

# *** food ***
food_time = 0
food_list = []
foodname = []
for food_file in listdir(r'images/all-food'):
    if isfile(r'images/all-food/' + food_file):
        foodname.append(food_file)

food_speed = [0, 240] # 0 en x car ne va ni vers la gauche(-n) ni droite(n positif). En y nombre positif car va vers le bas. Si négatif, va vers le haut

# *** darkmatter poop ***

poop = Actor("darkmatter", anchor= ['center', 'bottom'])

poop.pos = (player.pos[0] -100, player.pos[1])  # WIDTH/2 -30, HEIGHT-5


# *** ok food collision with player ***


#*** beer collision with player ***


# *** functions ***

def draw(): 
    global food # mis la variable globale, car error de call before assignement de food

    # si je veux fullscreen sans pouvoir en sortir :    screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    screen.clear()
    screen.fill((1, 7, 46))
    screen.draw.text(f"F11 : Fullscreen\nESC : Exit Fullscreen", (10, 15), color=(255,255,255), fontsize=15)
    screen.draw.text(str(score), (WIDTH/2, images.planet_express.get_height()), color=(255,255,255), fontsize=40)

    player.draw()
    for food in food_list: 
        food.draw()
    
    if player.colliderect(food): # erreur ici car pas collidepoint mais colliderect !
        poop.draw()

def random_pos():
    image_width = 64 # food sprite size
    image_heigth = 64
    modifier = max(image_width, image_heigth) / 2
    x = randint(modifier, WIDTH - 200) # pas WIDTH- modifier car ici on veut que le food s'arrête aussi WIDTH-200 comme le player, pour qu'il puisse manger tout, et que ça n'aparaisse pas là où Bender apparaîtra
    y = 0
    return [x, y]

def update(dt):

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

    global food_time, food, score

    food_time -= dt # dt = changement du temps
    if food_time <= 0.0:
        food = Actor('all-food/' + choice(foodname), anchor= ['center', 'top']) # à mettre dans update
        food.pos = random_pos()
        food_list.append(food)
        food_time = randint(1,3)
    pos= food.pos


# *** collision with player and/or bottom screen ***
    mvt_x = food_speed[0] * dt
    mvt_y = food_speed[1] * dt

    for food in food_list :
        food.pos = [food.pos[0] + mvt_x, food.pos[1] + mvt_y]

        if player.colliderect(food): 
            food_list.remove(food)
            score += 100
# *** darkmatter generating ***
            set_player_eat_then_poop()
            

        elif food.pos[1] >= HEIGHT -10:
            food_list.remove(food)
            # pas de break car dans le casse-brique, touche une brique à la foi, ici, plusieurs food peuvent collide


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
     if key == keys.F11:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
     elif key == keys.ESCAPE:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT))

def set_player_eat_then_poop():
    player.image = 'nibbler_yay'
    clock.schedule_interval(set_player_normal, 1)
    

def set_player_normal():
    player.image = 'nibbler_idle'





pgzrun.go()