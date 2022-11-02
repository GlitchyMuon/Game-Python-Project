import pgzrun
from pgzhelper import *
from random import randint, choice
from os import listdir
from os.path import isfile
import pygame
#from pgzero.builtins import Actor, animate, Rect, images, clock, sounds
#si j'importe tout ci-dessus : n'affiche plus de surlignage rouge mais le scale ne fonctionne plus sur le ship étrangement

# --------------------------- Variables -----------------------------

WIDTH = 1440
HEIGHT = 900
ROTATION_SPEED = 80
WHITE = 255, 255, 255
BOX = Rect((15, 100, 200, 50))


game_over = False
score = 0
# pour les différents scores, p-e que je devrais faire des sous-dossiers, et faire un dirlist.
malus = 300
malus_taken = False
food_eaten = 0
food_value_score_visible = False
enemy_value_score_visible = False
pause = False
fullscreen = True

# ************************** Menu Class *********************************

background = Actor("space_planet_left")
pause_img = Actor("hypnotoad_effect_filter_transparent_noborders")

class Menu():
    def __init__(self):
        self.background = Actor('space_planet_bottom')
        self.icon = Actor('nibbler_spaceship')
        self.icon.size= (500, 500)
        self.icon.pos = (WIDTH/2, HEIGHT/2)
        self.welcome_txt = "Welcome to Space Gobbler !"
        #self.welcome_txt.pos = (WIDTH/2, (self.icon.pos[1]-30))     pos is not recognized because str
        self.title_txt = "Press any key"
        self.author= "Made by GlitchyMuon"

    def draw(self):
        self.background.draw()
        self.icon.draw()
    
    #def update(self, dt):
    
        
menu = Menu()
menu_visible = True


# ************************** player ****************************************
class Player(Actor):
    def __init__(self):
        super().__init__("nibbler_idle", anchor= ['center', 'bottom'])
        self.pos = [WIDTH/2, HEIGHT]
        self.life = 1800

player = Player()

# ************************** player life actor *****************************
heart1 = Actor('heart_full')
heart1.scale = 1
heart1.pos = [30, 70] # or [70, 70] would be centered on textbox
heart2 = Actor('heart_full')
heart2.scale = 1
heart2.pos = [(heart1.pos[0]+41), heart1.pos[1]]
heart3 = Actor('heart_full')
heart3.scale = 1
heart3.pos = [(heart2.pos[0]+41), heart1.pos[1]]


# ************************** food ******************************************
food_time = 0
food_list = []
foodnames = [] # les fichiers
for food_file in listdir(r'images/all_food'):
    if isfile(r'images/all_food/' + food_file):
        foodnames.append(food_file)

food_speed = [0, 240] # 0 en x car ne va ni vers la gauche(-n) ni droite(n positif). En y nombre positif car va vers le bas. Si négatif, va vers le haut

#************************** Enemy = Fotran Beer ****************************
enemy_time = randint(10, 15) # temps avant le premier
enemy_list = []
enemy_speed = [0, 240]


# ************************** Enemy Action = Bender *************************
enemy_action = Actor("bender_idle", anchor=['center', 'bottom'])
enemy_action.pos = [WIDTH -66, HEIGHT]
enemy_action_visible = False

# ************************** Enemy trigger = wrench *************************
enemy_action_trigger = Actor("wrench_resized")
enemy_action_trigger_visible = False
enemy_action_trigger_maxspeed = 350
enemy_action_trigger_speed = [-enemy_action_trigger_maxspeed, 0]
enemy_action_trigger_time = 0


# ************************** Darkmatter = poop Class ******************************
poop_list = []
poop_visible = False

class Poop(Actor):
    def __init__(self):
        super().__init__("darkmatter_rotated", anchor= ['center', 'bottom'])
        
    def update(self, dt):
        self.move_towards(ship.sprite, 1020*dt) # *dt donne la vitesse dans ce cas-ci
        if ship.sprite.colliderect(self):
            #juste comme ça si on veut remove de la liste aprèsn un collide
            poop_list.remove(self)
            # si je veux shrink :
            #if self.scale >= 0 :
                #self.scale -= 2 *dt
        
poop = Poop()


# ************************** Ship Class *********************************************

class Ship : # ou Ship(Actor)
    def __init__(self):
        self.sprite=Actor('planet_express', anchor= ['right', 'center'])   #super().__init__('planet_express', anchor= ['right', 'center'])
        self.sprite.scale = 0.33    # pas besoin de mettre 'sprite.' si méthode héritage
        self.sprite.pos = (WIDTH, images.planet_express.get_height()*0.33-33)
        self.direction = [-1, 0]
        self.speed = 10
        self.boostspeed = 30
        self.boostspeed_timer = 0
        self.move_timer = 0
        self.burstflamesprite_dflt = Actor('xsmall_burst', anchor=['left','center'])
        self.burstflamesprite_dflt.scale = 0.50
        self.burstflamesprite_dflt.pos = (self.sprite.pos[0], self.sprite.pos[1])
        # code ci-dessous pas nécessair mnt que j'ai mis dans draw(self):
        """self.burstflamesprite_s = Actor('small_burst', anchor=['left','center'])
        self.burstflamesprite_s.scale = 0.50
        self.burstflamesprite_s.pos = (self.sprite.pos[0], self.sprite.pos[1])
        self.burstflamesprite_m = Actor('medium_burst', anchor=['left','center'])
        self.burstflamesprite_m.scale = 0.50
        self.burstflamesprite_m.pos = (self.sprite.pos[0], self.sprite.pos[1])
        self.burstflamesprite_l = Actor('large_burst', anchor=['left','center'])
        self.burstflamesprite_l.scale = 0.50
        self.burstflamesprite_l.pos = (self.sprite.pos[0], self.sprite.pos[1])
        self.burstflamesprite_xl = Actor('xlarge_burst', anchor=['left', 'center'])
        self.burstflamesprite_xl.scale = 0.50
        self.burstflamesprite_xl.pos = (self.sprite.pos[0], self.sprite.pos[1]) """
    
    def move(self, dt):
        if self.move_timer > 0 :
            self.move_timer -= dt

            x = self.sprite.pos[0] + self.speed * self.direction[0] * dt
            y = self.sprite.pos[1] + self.speed * self.direction[1] * dt
            self.sprite.pos = [x , y]
        self.burstflamesprite_dflt.pos = (self.sprite.pos[0], self.sprite.pos[1])
        
    def draw(self):
        global food_eaten
        self.sprite.draw()
        self.burstflamesprite_dflt.draw()

        # code not working !  
        if food_eaten == 3:
            self.burstflamesprite_dflt.image = 'small_burst'
        elif player.colliderect(enemy_action_trigger):
            self.burstflamesprite_dflt.image = 'xsmall_burst'
        if food_eaten == 5:
            self.burstflamesprite_dflt.image = 'medium_burst'
        elif player.colliderect(enemy_action_trigger) :
            self.burstflamesprite_dflt.image = 'small_burst'
        if food_eaten == 7 :
            self.burstflamesprite_dflt.image = 'large_burst'
        elif player.colliderect(enemy_action_trigger):
            self.burstflamesprite_dflt.image = 'medium_burst'
        if food_eaten == 10:
            self.burstflamesprite_dflt.image = 'xlarge_burst'
        elif player.colliderect(enemy_action_trigger):
            self.burstflamesprite_dflt.image = 'large_burst'
        
    def decelerate(self):
        self.speed *= 1
        self.boostspeed *= 1
        self.direction = [+1, 0] # à mettre dans le move ? et redéfinir toutes les conditions de déceleration
        

ship = Ship() #crée l'instance


# ---------------------------- Functions --------------------------------------------------

def draw_menu():
     #  if game_over:
        #screen.clear()
        #screen.draw.text('Game Over', (WIDTH/2, HEIGHT/2), color="red", gcolor="yellow", owidth=0.25, ocolor="grey", fontsize=100)
        #screen.draw.text('Score: ' + str(round(score)), (WIDTH/2, HEIGHT/2+10), color="gold", owidth=0.25, ocolor="grey", fontsize=50)
    #else:

    screen.clear()
    menu.draw()

    screen.draw.text(f"F11 : Fullscreen\nESC : Exit Fullscreen\nPause : Spacebar", (10, 15), color=(255,255,255), fontsize=16, fontname="retrogaming")

    screen.draw.text(menu.welcome_txt, center=(WIDTH/2, (HEIGHT/2-300)), color="cyan", gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=80, fontname="ocraext")

    screen.draw.text(menu.title_txt, center =(WIDTH/2, (HEIGHT-100)), color="purple", gcolor='blue', owidth=0.25, ocolor="grey", fontsize= 30, fontname ="1up")

    screen.draw.text(menu.author, (WIDTH-275, HEIGHT-30), color="seagreen", gcolor='lightcoral', owidth=0.25, ocolor= "darkslategray", fontsize= 20, fontname="retrogaming")

def draw_game(): # ce qui est dans le draw, ne doit que draw. On peut mettre des if (pas gérer de collision, ni update)
    global food # mis la variable globale, car error de call before assignement de food

    # si je veux fullscreen sans pouvoir en sortir :    screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    screen.clear() # à mettre dans le if game_over
    # screen.fill((1, 7, 46)) si pas de background
    background.draw()

    screen.draw.rect(BOX, WHITE)

    screen.draw.textbox(str(score), (15, 100, 200, 50), color=(255,255,255), gcolor="green")

    screen.draw.text("Quantity of food eaten : " + str(food_eaten), (20, 160), color=(255,255,255), gcolor="gold", fontsize= 40)
    
    for poop in poop_list :
        poop.draw()
    # si je veux qu'il apparaisse derrière le player, il faut qu'il soit draw avant le player. Car dans le draw, les derniers élements superposent les précédents

    player.draw()

    # ____________ Ship draw ____________
    ship.draw()
   

    # ____________ Player life hearts draw ____________

    if player.life == 1800 :
        heart3.image = 'heart_full'
    elif player.life < 1800 and player.life >= 1500 :
        heart3.image = 'heart_half'
    elif player.life < 1500:
        heart3.image = 'heart_empty'
    heart3.draw()

    if player.life >= 1200 :
        heart2.image = 'heart_full'
    elif player.life < 1200 and player.life >= 900:
        heart2.image = 'heart_half'
     
    elif player.life < 900:
        heart2.image = 'heart_empty'
    heart2.draw()

    if player.life == 600:
        heart1.image= 'heart_full'
    elif player.life < 600 and player.life >= 300 :
        heart1.image = 'heart_half'
    elif player.life < 300:
        heart1.image = 'heart_empty'
    heart1.draw()

    for food in food_list: 
        food.draw()
    
    for enemy in enemy_list:
        enemy.draw()

    # ____________ Bender Appear (ennemy_action)____________
    if enemy_action_visible:
        enemy_action.draw()
        enemy_action_trigger.draw()

    # ____________ Game Pause Screen ____________
    if pause == True :
        screen.draw.text("Game Paused", center=(WIDTH/2, (HEIGHT/2 -200)), color="cyan", gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=100, fontname="ocraext")
        pause_img.pos = [WIDTH/2, (HEIGHT/2 + 100)]
        pause_img.draw()


    # ____________ Above player score draw ____________
    
    if food_value_score_visible: 
        screen.draw.text("100", center=((player.pos[0]+30), (player.pos[1]-player.height-10)), color="white",gcolor="yellow", fontsize= 35)

    # ____________ hurt score ____________
    if enemy_value_score_visible:
        screen.draw.text("-200", center=((player.pos[0]+30), (player.pos[1]-player.height-10)), color="white", gcolor="red", fontsize= 35)
    
# ++++++++ General Draw ++++++++++

def draw():
    if fullscreen:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT))

    if menu_visible == True:
        draw_menu()
    #elif KeyboardEvent or pygame.MOUSEBUTTONDOWN == True:  # CHECK si fonctionne !
        # penser au game over !
    else :
        draw_game()



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
    global food_time, food, score, food_value_score_visible, enemy_value_score_visible, food_eaten, poop

    food_time -= dt # dt = changement du temps
    if food_time <= 0.0: # quand le sablier est vide ou en dessous de 0
        food = Actor('all_food/' + choice(foodnames), anchor= ['center', 'top']) # à mettre dans update
        food.pos = random_pos()
        food_list.append(food)
        food_time = randint(1,3)
        pos= food.pos

    # ____________ Collision with player and/or bottom screen ____________
    mvt_x = food_speed[0] * dt #* 1/60e de sec
    mvt_y = food_speed[1] * dt

    # ____________ Ok food collision with player ____________

    for food in food_list :
        food.pos = [food.pos[0] + mvt_x, food.pos[1] + mvt_y]

        if player.colliderect(food): 
            sounds.munch.play()
            food_list.remove(food)
            score += 100
            food_value_score_visible = True
            clock.schedule_interval(set_food_value_score, 0.8)
            ship.move_timer = 1
            food_eaten += 1
            # if combo % 3 == 0 :   règle si par incrémentation de 3
            # sinon que des if elif
            

    # ____________ Darkmatter/Poop generating ____________
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
            player.life -= malus
            set_enemy_action_animate()
            enemy_value_score_visible = True
            clock.schedule_interval(set_enemy_value_score, 0.8)
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
        set_player_hit_angry()
        enemy_action_trigger_speed = [0, enemy_action_trigger_maxspeed]
        enemy_action.move_back(-132)  #important de le mettre ici sinon il reste en dehors de l'écran !
        


def update_game(dt):
    global food_eaten, score, malus_taken
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

    # *** moving ship ***
    ship.move(dt)
    # Clock ci-dessous ne fonctionne pas !
    if player.colliderect(enemy_action_trigger):
        malus_taken = True
        # Should define a set_ship_move_normal() and a set_ship_decelerate() but in ship Class or not ?
        #def set_ship_decelarate():
        #ship.decelerate()
        #clock.schedule_interval(ship.move, 0.5)

    for poop in poop_list :
        poop.update(dt)


def update_menu(dt):
    #sounds.menu_music.play(-1)
    pass

# ++++++++ General Update here ++++++++

def update(dt):
    if menu_visible == True :
        update_menu(dt)
    else :
        update_game(dt)


def on_mouse_move(pos): 
    if pos[0] > 50 and pos[0] < WIDTH - 200 : #largeur et hauteur sprite = 296
        x = pos[0]
    elif pos[0] <= 50:
        x = 50
    else :
        x = WIDTH - 200 # calcul : 50 est la moitié du sprite player. 130 est la taille approximatif du sprite de Bender/ennemy. 50 + 130 + 20 de marges = 200

    y = player.pos[1]
    player.pos = [x, y]

def on_mouse_down(button):
    global menu_visible
    if menu_visible == True and button == mouse.LEFT:
        menu_visible = False


def on_key_down(key):
    global pause, fullscreen, menu_visible
    if key == keys.F11:
        fullscreen = not fullscreen
    elif key == keys.ESCAPE:
        exit()

    if menu_visible == True :
        menu_visible = False
    else :
        if key == keys.SPACE:
            pause = not pause
            

def set_enemy_action_animate():
    global enemy_action_visible
    enemy_action.image = 'bender_yay'
    enemy_action.image = 'bender_action'
    clock.schedule_interval(set_enemy_action_normal, 0.7)
    enemy_action_visible = True
    enemy_action.pos = (WIDTH-66, HEIGHT)
    #clock.schedule_interval(set_enemy_action_invisible, 1.50)  --code si je ne le déplace pas.-- bug de collide avec poop qui va vers ship
    

def set_enemy_action_normal():
    enemy_action.image = 'bender_idle'
    

def set_player_eat_then_poop():
    global poop_visible
    player.image = 'nibbler_yay'
    clock.schedule_interval(set_player_normal, 0.8)
    new_poop = Poop()
    new_poop.pos = (player.pos[0] -100, player.pos[1])  # WIDTH/2 -30, HEIGHT-5
    poop_list.append(new_poop)


def set_player_hit_angry():
    player.image = 'nibbler_action'
    clock.schedule_interval(set_player_normal, 1)
 

def set_player_normal():
    player.image = 'nibbler_idle'


def set_food_value_score():
    global food_value_score_visible
    food_value_score_visible = False


def set_enemy_value_score():
    global enemy_value_score_visible
    enemy_value_score_visible = False





    

pgzrun.go()