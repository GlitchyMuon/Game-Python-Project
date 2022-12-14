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

fullscreen = True
pause = False
game_over = False
win = False
record_win = False


# pour les différents scores, p-e que je devrais faire des sous-dossiers, et faire un dirlist.

game_time = 0
score = 0
malus = 300
malus_taken = False
streak = 0
total_food = 0
food_value_score_visible = False
enemy_value_score_visible = False


background = Actor("space_planet_left")
pause_img = Actor("hypnotoad_effect_filter_transparent_noborders")

gameover_img = Actor("planet_express_crash")
gameover_bg = Actor("nasa_asteroid_1440x900")

win_img = Actor("futurama_yipee")

# ************************** Menu Class *********************************

class Menu():
    def __init__(self):
        self.background = Actor('space_planet_bottom')
        self.icon = Actor('nibbler_spaceship')
        self.icon.size = (500, 500)
        self.icon.pos = (WIDTH/2, HEIGHT/2)
        self.welcome_txt = "Welcome to Space Gobbler !"
        #self.welcome_txt.pos = (WIDTH/2, (self.icon.pos[1]-30))     pos is not recognized because str
        self.title_txt = "Press any key"
        self.author = "Made by GlitchyMuon"
        self.rules = "++ RULES ++\n\nGuide Nibbler beneath the falling food.\n\nThe darkmatter that he poops will fuel the ship\n\nTo win, the ship has to reach the planet\n(left of the screen)"
        self.tip = "++ Tips ++\n\nBeware of a certain DRINK !!!\n\nThere is a catch... ! ;)\n\nKeep an eye on your Hearts !"

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

    def update(self): # not working
        global game_over
        if self.life == 0 :
            game_over = True

player = Player()

# ************************** player life actor *****************************
heart1 = Actor('heart_full')
heart1.scale = 1.25
heart1.pos = [30, 70] # or [70, 70] would be centered on textbox
heart2 = Actor('heart_full')
heart2.scale = 1.25
heart2.pos = [(heart1.pos[0]+51), heart1.pos[1]]    # +41 if scale 1 (smaller)
heart3 = Actor('heart_full')
heart3.scale = 1.25
heart3.pos = [(heart2.pos[0]+51), heart1.pos[1]]


# ************************** food ******************************************
food_time = 0
food_list = []
foodnames = [] # les fichiers
for food_file in listdir(r'images/all_food'):
    if isfile(r'images/all_food/' + food_file):
        foodnames.append(food_file)
        #be sure to understand the use of this codelines for later project

food_speed = [0, 240] # 0 en x car ne va ni vers la gauche(-n) ni droite(n positif). En y nombre positif car va vers le bas. Si négatif, va vers le haut

#************************** Enemy = Fortran Beer ****************************
enemy_time = randint(5, 8) # temps avant le premier
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

class Poop(Actor): #méthode héritage
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
        self.sprite.pos = (WIDTH-40, images.planet_express.get_height()*0.33-33)            # 40 = xsmall_burst width

        self.direction = [-1, 0]
        self.speed = 10
        self.boostspeed = 30        # still need to do something with this and streak
        self.boostspeed_timer = 0   # ditto
        self.move_timer = 0        

        self.burstflamesprite_dflt = Actor('xsmall_burst', anchor=['left','center'])
        self.burstflamesprite_dflt.scale = 0.50
        self.burstflamesprite_dflt.pos = (self.sprite.pos[0], self.sprite.pos[1])
        
        self.penalty = False
    
    def move(self, dt):
        global streak
        if self.penalty == True:
            x = self.sprite.pos[0] + self.speed * 1 * -self.direction[0] * dt
            y = self.sprite.pos[1] + self.speed * self.direction[1] * dt
            self.sprite.pos = [x , y]

        elif self.move_timer > 0 :
            self.move_timer -= dt
            finalspeed= self.speed *streak * 0.5    #tweaked from 0.8 to 0.5 for more longer gametime and also since the ship has to reach a shorter distance to win

            x = self.sprite.pos[0] + finalspeed * self.direction[0] * dt
            y = self.sprite.pos[1] + finalspeed * self.direction[1] * dt
            self.sprite.pos = [x , y]
        self.burstflamesprite_dflt.pos = (self.sprite.pos[0], self.sprite.pos[1])
        if self.sprite.pos[0] > WIDTH+40 : # 40 = xsmall_burst sprite width
            self.sprite.pos = (WIDTH+40, self.sprite.pos[1]) 
            #parenthèses facultatif ici, sauf dans un print car la virgule dans beaucoup de cas sépare les éléments.
        
        if streak > 0:
            self.boostspeed = 30
        

    def draw(self):
        global streak
        self.sprite.draw()
        self.burstflamesprite_dflt.draw()

        # reverted logic order from big to small
        if streak >= 10:
            self.burstflamesprite_dflt.image = 'xlarge_burst'
        elif streak >= 7 :
            self.burstflamesprite_dflt.image = 'large_burst'
        elif streak >= 5:
            self.burstflamesprite_dflt.image = 'medium_burst'
        elif streak >= 3:
            self.burstflamesprite_dflt.image = 'small_burst'
        elif streak == 0 :
            self.burstflamesprite_dflt.image = 'xsmall_burst'
        
        
    def decelerate(self):
        self.penalty = True
        

ship = Ship() #crée l'instance


# ---------------------------- Functions --------------------------------------------------

def draw_menu():

    screen.clear()
    menu.draw()

    screen.draw.text(f"F11 : Fullscreen\nESC : Exit Fullscreen\nPause : Spacebar", (10, 15), color=(255,255,255), fontsize=16, fontname="retrogaming")

    screen.draw.text(menu.welcome_txt, center=(WIDTH/2, (HEIGHT/2-300)), color="cyan", gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=80, fontname="ocraext")

    screen.draw.text(menu.rules, (0, (HEIGHT/2-150)), color="white", owidth=0.05, ocolor="grey", align="center", lineheight=1.5, fontsize=18, fontname="retrogaming")

    screen.draw.text(menu.tip, (WIDTH-430, (HEIGHT/2-150)), color="white", owidth=0.05, ocolor="grey",  align="center", lineheight=1.5, fontsize=18, fontname="retrogaming")

    screen.draw.text(menu.title_txt, center=(WIDTH/2, (HEIGHT-100)), color="purple", gcolor='blue', owidth=0.25, ocolor="grey", fontsize= 30, fontname ="1up")

    screen.draw.text(menu.author, (WIDTH-275, HEIGHT-30), color='seagreen', gcolor='lightcoral', owidth=0.25, ocolor= 'darkslategray', fontsize= 20, fontname="retrogaming")


def draw_game(): # ce qui est dans le draw, ne doit que draw. On peut mettre des if (pas gérer de collision, ni update)
    global food, total_food, game_over, pause, win, data_file, record_win

    # si je veux fullscreen sans pouvoir en sortir :    screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    screen.clear()
    # screen.fill((1, 7, 46)) si pas de background
    background.draw()

    screen.draw.rect(BOX, WHITE)

    screen.draw.textbox(str(score), (15, 100, 200, 50), color=(255,255,255), gcolor="green")

    screen.draw.text("Quantity of food eaten : " + str(total_food), (20, 160), color=(255,255,255), gcolor="gold", fontsize= 40)
    screen.draw.text("Current streak : " + str(streak), (20, 200), color=(255,255,255), gcolor="green", fontsize= 40)
    
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

    # ____________ Foods draw ____________
    
    for food in food_list: 
        food.draw()

    # ____________ Fortran Beer/Enemy draw ____________

    
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

    # ____________ Hurt score ____________
    if enemy_value_score_visible:
        screen.draw.text("-200", center=((player.pos[0]+30), (player.pos[1]-player.height-10)), color="white", gcolor="red", fontsize= 35)


    # ____________ Game Over Screen ____________
    if player.life == 0 :
        if not game_over :
            data_file = open(r"data/hiscore.dat", "a")
            data_file.write(str(score)+ "\n")
            data_file.close()

        game_over = True

        screen.clear()  #si je veux que tout s'efface, y compris le background et tout l'affichage
        #background_img = pygame.image.load('nasa_asteroid_1024x614.jpg').convert_alpha()
        #screen.blit(background_img, (0.0))
        # doesn't work : TypeError: invalid destination position for blit       Must be in main directory
        gameover_bg.draw()
        gameover_img.draw() 

        screen.draw.text('G a m e  O v e r', center=(WIDTH/2, (HEIGHT/2 - 200)), color="red", gcolor="yellow", owidth=0.30, ocolor="white", fontsize=150, fontname = "rh-shmatter")
    

        data_file = open(r"data/hiscore.dat")
        hiscore_list = data_file.readlines()
        data_file.close()

        hiscore = -1000000000000
        for line in hiscore_list:
            if line: #s'il y a une ligne
                s = int(line.strip())
                if s > hiscore:
                    hiscore = s

        screen.draw.text('Highscore: ' + str(hiscore), center=(WIDTH/2, (HEIGHT/2-310)), color="gold2", gcolor="darkgoldenrod", owidth=0.25, ocolor="grey", fontsize=70)

        screen.draw.text('Score: ' + str(score), center=(WIDTH/2, (HEIGHT/2-380)), color="gold", gcolor="darkgoldenrod", owidth=0.25, ocolor="grey", fontsize=70)
        gameover_img.pos = [WIDTH/2, (HEIGHT/2 + 100)]



    # ____________ Win Screen ____________
    if ship.sprite.pos[0] <= 220+images.planet_express.get_width()*0.33 : # 0 if end of screen. 215 if planet orbit
        if not win and record_win == False :
            record_win = record_win = True
            data_file = open(r"data/hiscore.dat", "a")
            data_file.write(str(score)+ "\n")
            data_file.close()

        win = True


        screen.clear()

        #screen.fill((61,55,21))    #decide if bgcolor black or this brown
        win_img.pos= [WIDTH/2, (HEIGHT/2 + 100)]    #(HEIGHT/2 + 100) if smaller img
        win_img.draw()
        screen.draw.text("You won ! \n The ship has arrived succesfully !", center=(WIDTH/2, (HEIGHT/2 -220)), color="seagreen3", gcolor="lightgoldenrod", owidth=0.25, ocolor="grey", fontsize=60, fontname="ocraext")

        screen.draw.text('Score: ' + str(score), center=(WIDTH/2, (HEIGHT/2-390)), color="gold", gcolor="darkgoldenrod", owidth=0.25, ocolor="grey", fontsize=60)

        data_file = open(r"data/hiscore.dat")
        hiscore_list = data_file.readlines()
        data_file.close()

        hiscore = -1000000000000
        for line in hiscore_list:
            if line: #s'il y a une ligne
                s = int(line.strip())
                if s > hiscore:
                    hiscore = s
        
        screen.draw.text('Highscore: ' + str(hiscore), center=(WIDTH/2, (HEIGHT/2-310)), color="gold", gcolor="goldenrod1", owidth=0.25, ocolor="grey", fontsize=60)
    
    
# ++++++++ General Draw ++++++++++

def draw():
    if fullscreen:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT))

    if menu_visible == True:
        draw_menu()
    #elif KeyboardEvent or pygame.MOUSEBUTTONDOWN == True:  # CHECK si fonctionne !
    
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
    global food_time, food, score, streak,food_value_score_visible, enemy_value_score_visible, streak, total_food, poop

    food_time -= dt # dt = changement du temps
    if food_time <= 0.0: # quand le sablier est vide ou en dessous de 0
        food = Actor('all_food/' + choice(foodnames), anchor= ['center', 'top']) # à mettre dans update
        pos = food.pos
        pos = random_pos()
        food_list.append(food)
        food_time = randint(1,3)
        # check following code if too many objects popping, if yes : adjust randint
        if game_time >= 25:
            food_time = randint(0,2)
        food.pos = pos

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
            total_food += 1
            streak += 1

           
    # ____________ Darkmatter/Poop generating ____________
            set_player_eat_then_poop()

        elif food.pos[1] >= HEIGHT -10:
            food_list.remove(food)
            # pas de break car dans le casse-brique, touche une brique à la foi, ici, plusieurs food peuvent collide


def enemy_update(dt):
    global enemy_time, enemy, score, streak, enemy_value_score_visible, enemy_action_trigger_visible, enemy_action_trigger_speed, malus

    enemy_time -= dt 
    if enemy_time <= 0.0:
        enemy = Actor("fortran_beer", anchor=['center', 'top'])
        pos = enemy.pos
        pos = random_pos_enemy()
        enemy_list.append(enemy)
        if game_time >= 20:
            enemy_time = randint(1,3)
        elif game_time >= 10 :
            enemy_time = randint(3,5)
        else :
            enemy_time = randint(5,7)       #should maybe increment food too

        enemy.pos = pos

      # *** enemy collision with player ***
    mvt_x = enemy_speed[0] * dt
    mvt_y = enemy_speed[1] * dt

    for enemy in enemy_list :
        enemy.pos = [enemy.pos[0] + mvt_x, enemy.pos[1] + mvt_y]        
        if player.colliderect(enemy):
            enemy_list.remove(enemy)
            sounds.glug_glug_glug.play()

            score -= malus
            streak = 0
            player.life -= malus

            set_enemy_action_animate()
            enemy_value_score_visible = True
            clock.schedule_interval(set_enemy_value_score, 0.8)
            enemy_action_trigger_visible = True
            enemy_action_trigger_speed = [-enemy_action_trigger_maxspeed,0]
            enemy_action_trigger.pos = [WIDTH -66, HEIGHT-player.height]
            
        if enemy.pos[1] >= (HEIGHT-10):
            if enemy in enemy_list :
                enemy_list.remove(enemy)


def enemy_action_trigger_update(dt):
    global enemy_action_trigger, enemy_action_trigger_speed, enemy_action_trigger_visible, enemy_action_trigger_time, ROTATION_SPEED, score, streak

    mvt_x = enemy_action_trigger_speed[0] * dt
    mvt_y = enemy_action_trigger_speed[1] * dt
    enemy_action_trigger.angle += ROTATION_SPEED * dt

    enemy_action_trigger.pos = [enemy_action_trigger.pos[0] + mvt_x, enemy_action_trigger.pos[1] + mvt_y]

    if player.colliderect(enemy_action_trigger):
        #enemy_action_trigger_visible = False  would make it disappear too abruptly
        sounds.slap_umph.play()
        set_player_hit_angry()

        #don't put the malus score -= here otherwise the wrench rotating will decrease player.life to 0

        enemy_action_trigger_speed = [0, enemy_action_trigger_maxspeed]
        enemy_action.move_back(-132)  #important de le mettre ici sinon il reste en dehors de l'écran !
        


def update_game(dt):
    global streak, score, malus_taken, score, game_over, win
    
    #if not music.is_playing('neocrey_jump_to_win'):   # Makes win screen lag !!
        #music.queue('neocrey_jump_to_win')
        #music.set_volume(0.2)

    if pause :
        music.pause()
        return  # permet d'arrêter l'update du game !!!

    if game_over:
        if music.is_playing('neocrey_jump_to_win'):
            music.stop()
            sounds.icy_game_over.play()    #or this_is_game_over
        return
    
    if win :
        #music.fadeout(0.15)
        if music.is_playing('neocrey_jump_to_win'):
            music.stop()
            sounds.littlerobotsoundfactory_jingle_win_00.play()     #works !!! so doesn't if I wanna play another music
        #wmusic.play_once('nebula')       #only works when I press ESC or or continously play if I drag the window ?!
        return


    if dt > 0.5 :
        return
        
    if not pause :
        pos = player.pos
        if pos[0] > WIDTH -5:
            pos[0] = WIDTH -5
        elif pos[0] < 5:
            pos[0] = 5
            
        if pos[1] > WIDTH -5:
            pos[1] = WIDTH -5
        elif pos[1] < 5:
            pos[1] = 5
        
        player.pos = pos

    food_update(dt)
    enemy_update(dt)

    if enemy_action_trigger_visible == True:
        enemy_action_trigger_update(dt)

    # *** moving ship ***
    ship.move(dt)

    if player.colliderect(enemy_action_trigger):
        malus_taken = True
        set_ship_decelarate()
        clock.schedule_interval(set_ship_move_normal, 1) # try different times/secs
       
    for poop in poop_list :
        poop.update(dt)

    

def update_menu(dt):
    if not music.is_playing('neocrey_jump_to_win'):
        music.play('neocrey_jump_to_win')
    #if not music.is_playing('menu_music'): #intro music
        #music.play_once('menu_music')
        #music.queue('neocrey_jump_to_win')
        music.set_volume(0.2)


# ++++++++ General Update here ++++++++

def update(dt):
    global game_time
    game_time += dt

    if menu_visible == True :
        update_menu(dt)
    else :
        update_game(dt)
    # music.fadeout(0.25)       #Makes game lag !!! 
        
        


def on_mouse_move(pos): 
    if pos[0] > 50 and pos[0] < WIDTH - 200 : #largeur et hauteur sprite = 296
        x = pos[0]
    elif pos[0] <= 50:
        x = 50
    else :
        x = WIDTH - 200 # calcul : 50 est la moitié du sprite player. 130 est la taille approximatif du sprite de Bender/ennemy. 50 + 130 + 20 de marges = 200

    if not pause : # otherwise player has a loophole (can reposition themself beneath right food if too many Beers)
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
            music.unpause() #pas sûr que je dois le mettre ici
            

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


def set_ship_decelarate():
    ship.decelerate()


def set_ship_move_normal():
    global malus_taken
    malus_taken = False
    ship.penalty = False


pgzrun.go()
