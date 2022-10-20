import pgzrun
from random import randint, choice
from os import listdir
from os.path import isfile
import pygame


WIDTH = 1440
HEIGHT = 900


game_over = False
score = 0
# pour les différents scores, p-e que je devrais faire des sous-dossiers, et faire un dirlist.
pause = False
fullscreen = True

background = Actor("space_planet_left")


# *** player ***

player = Actor("nibbler_idle", anchor= ['center', 'bottom']) # center, bottom serait mieux ? ou bottom, middle ?
player.pos = [WIDTH/2, HEIGHT]

# *** food ***
food_time = 0
food_list = []
foodnames = [] # les fichiers
for food_file in listdir(r'images/all_food'):
    if isfile(r'images/all_food/' + food_file):
        foodnames.append(food_file)

food_speed = [0, 240] # 0 en x car ne va ni vers la gauche(-n) ni droite(n positif). En y nombre positif car va vers le bas. Si négatif, va vers le haut

#*** Fotran Beer = Enemy ***
enemy_time = 0
enemy_list = []
enemy_speed = [0, 240]


# *** Enemy Action ***
enemy_action = Actor("bender_idle", anchor=['center', 'bottom'])
enemy_action.pos = [WIDTH -66, HEIGHT]
enemy_action_visible = False

# *** darkmatter poop ***

poop = Actor("darkmatter", anchor= ['center', 'bottom'])
poop_visible = False


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
    screen.draw.text(str(score), (WIDTH/2, images.planet_express.get_height()), color=(255,255,255), gcolor="green", fontsize=40)
    
    if poop_visible:
        poop.draw()
    # si je veux qu'il apparaisse derrière le player, il faut qu'il soit draw avant le player. Car dans le draw, les derniers élements superposent les précédents


    player.draw()

    for food in food_list: 
        food.draw()
    
    for enemy in enemy_list:
        enemy.draw()

    # *** bender appear (ennemy_action)***
    if enemy_action_visible:
        enemy_action.draw()

    
    # *** game pause ***
    if pause == True :
         screen.draw.text("Game Paused", center=(WIDTH/2, HEIGHT/2), color="cyan", gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=100, fontname="ocraext")

    # *** Scoring draw ***
    # *** global score ***
    if player.colliderect(food): 
        screen.draw.text("100", center=(player.pos[0], HEIGHT/2), color="white",gcolor="yellow", fontsize= 20)

    # *** hurt score *** error, surerpose le score global !!!
    for enemy in enemy_list:
        if player.colliderect(enemy):
            screen.draw.text("-200", (WIDTH/2, (player.pos[1]-20)), color="white",gcolor="red", fontsize= 18)
            break # car il collide qu'un à la fois

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


def food_update(dt):
    global food_time, food, score

    food_time -= dt # dt = changement du temps
    if food_time <= 0.0:
        food = Actor('all_food/' + choice(foodnames), anchor= ['center', 'top']) # à mettre dans update
        food.pos = random_pos()
        food_list.append(food)
        food_time = randint(1,3)
    pos= food.pos


    # *** collision with player and/or bottom screen ***
    mvt_x = food_speed[0] * dt
    mvt_y = food_speed[1] * dt

    # *** ok food collision with player ***

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

def enemy_update(dt):
    global enemy_time, enemy, score

    enemy_time -= dt 
    if enemy_time <= 0.0:
        enemy = Actor("fortran_beer", anchor=['center', 'top'])
        enemy.pos = random_pos_enemy()

        enemy_list.append(enemy)
        enemy_time = randint(5,10)
        pos = enemy.pos

      # *** enemy collision with player ***
    mvt_x = enemy_speed[0] * dt
    mvt_y = enemy_speed[1] * dt

    for enemy in enemy_list :
        enemy.pos = [enemy.pos[0] + mvt_x, enemy.pos[1] + mvt_y]        
        if player.colliderect(enemy):
            enemy_list.remove(enemy)
            score -= 200
            set_enemy_action_animate()
        if enemy.pos[1] >= HEIGHT -10:
            enemy_list.remove(enemy)


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
    clock.schedule_interval(set_enemy_action_normal, 1)
    enemy_action_visible = True
    enemy_action.pos = (WIDTH-66, HEIGHT)

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

    

pgzrun.go()