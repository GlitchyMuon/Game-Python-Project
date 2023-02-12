import pgzrun
from pgzhelper import *
from random import randint, choice
from os import listdir
from os.path import isfile
import pygame
# from pgzero.builtins import Actor, animate, Rect, images, clock, sounds
# si j'importe tout ci-dessus : n'affiche plus de surlignage rouge mais le scale ne fonctionne plus sur le ship étrangement

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


game_time = 0
score = 0
malus = 300
malus_taken = False
streak = 0
total_food = 0
count_wasted_food = 0
max_wasted_food_allowed = 15
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
        # self.welcome_txt.pos = (WIDTH/2, (self.icon.pos[1]-30))     pos is not recognized because str
        self.press_any_key_txt = "Press any key"
        self.author = "Made by GlitchyMuon"
        self.rules = "++ RULES ++\n\nGuide Nibbler beneath the falling food.\n\nThe darkmatter that he poops will fuel the ship\n\nTo win, the ship has to reach the planet\n(left of the screen)"
        self.tip = "++ Tips ++\n\nBeware of a certain DRINK !!!\n\nThere is a catch... ! ;p\n\nKeep an eye on your Hearts !\n\nBe mindful of foodwaste (# è ;é) !"

    def draw(self):
        self.background.draw()
        self.icon.draw()

    # def update(self, dt):


menu = Menu()
menu_visible = True


# ************************** player ****************************************
class Player(Actor):    # add different initial speed ? then faster with food ?
    def __init__(self):
        super().__init__("nibbler_idle", anchor=['center', 'bottom'])
        self.pos = [WIDTH/2, HEIGHT]
        self.life = 1800

    def update(self):
        global game_over
        if self.life == 0:
            game_over = True


player = Player()

# ************************** player life actor *****************************
heart1 = Actor('heart_full')
heart1.scale = 1.25
heart1.pos = [30, 70]  # or [70, 70] would be centered on textbox
heart2 = Actor('heart_full')
heart2.scale = 1.25
heart2.pos = [(heart1.pos[0]+51), heart1.pos[1]]    # +41 if scale 1 (smaller)
heart3 = Actor('heart_full')
heart3.scale = 1.25
heart3.pos = [(heart2.pos[0]+51), heart1.pos[1]]


# ************************** food ******************************************
food_time = 0
food_list = []
foodnames = []  # les fichiers
for food_file in listdir(r'images/all_food'):
    if isfile(r'images/all_food/' + food_file):
        foodnames.append(food_file)
        # be sure to understand the use of this codelines for later project
# For different scoring of food types, maybe I should make child directory and use listdir.

# 0 in x because doesn't go towards left (-n) nor right(n positive). In y, positive number cause it goes down. If negative, goes up.
food_speed = [0, 240]

# ************************** Enemy = Fortran Beer ****************************
# Time before the first appearance. Adjust if necessary
enemy_time = randint(5, 8)
enemy_list = []
enemy_speed = [0, 240]


# ************************** Enemy Action = Bender *************************
enemy_action = Actor("bender_idle", anchor=['center', 'bottom'])
enemy_action.pos = [WIDTH - 66, HEIGHT]
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


class Poop(Actor):  # heritage method
    def __init__(self):
        super().__init__("darkmatter_rotated", anchor=['center', 'bottom'])

    def update(self, dt):
        # *dt gives the speed in this case
        self.move_towards(ship.sprite, 1020*dt)
        if ship.sprite.colliderect(self):
            # like so if we want to remove after collide
            poop_list.remove(self)
            # if I'd want to shrink the sprite :
            # if self.scale >= 0 :
            # self.scale -= 2 *dt


poop = Poop()


# ************************** Ship Class *********************************************

class Ship:  # or Ship(Actor)
    def __init__(self):
        # super().__init__('planet_express', anchor= ['right', 'center'])
        self.sprite = Actor('planet_express', anchor=['right', 'center'])
        # no need for 'sprite.' if heritage method : super().__init__()
        self.sprite.scale = 0.33
        # 40 = xsmall_burst width
        self.sprite.pos = (
            WIDTH-40, images.planet_express.get_height()*0.33-33)

        self.direction = [-1, 0]
        self.speed = 10
        self.boostspeed = 30        # still need to do something with this and streak
        self.boostspeed_timer = 0   # ditto
        self.move_timer = 0

        self.burstflamesprite_dflt = Actor(
            'xsmall_burst', anchor=['left', 'center'])
        self.burstflamesprite_dflt.scale = 0.50
        self.burstflamesprite_dflt.pos = (
            self.sprite.pos[0], self.sprite.pos[1])

        self.penalty = False

    def move(self, dt):
        global streak
        if self.penalty == True:
            x = self.sprite.pos[0] + self.speed * 1 * -self.direction[0] * dt
            y = self.sprite.pos[1] + self.speed * self.direction[1] * dt
            self.sprite.pos = [x, y]

        elif self.move_timer > 0:
            self.move_timer -= dt
            # tweaked from 0.8 to 0.5 for more longer gametime and also since the ship has to reach a shorter distance to win
            finalspeed = self.speed * streak * 0.5

            x = self.sprite.pos[0] + finalspeed * self.direction[0] * dt
            y = self.sprite.pos[1] + finalspeed * self.direction[1] * dt
            self.sprite.pos = [x, y]
        self.burstflamesprite_dflt.pos = (
            self.sprite.pos[0], self.sprite.pos[1])
        if self.sprite.pos[0] > WIDTH+40:  # 40 = xsmall_burst sprite width
            self.sprite.pos = (WIDTH+40, self.sprite.pos[1])
            # facultative parenthesis here, only needed in a print cause the comma in lot of cases divides the arguments.
        if streak > 0:
            self.boostspeed = 30

    def draw(self):
        global streak
        self.sprite.draw()
        self.burstflamesprite_dflt.draw()

        # reverted logic order from big to small
        if streak >= 10:
            self.burstflamesprite_dflt.image = 'xlarge_burst'
        elif streak >= 7:
            self.burstflamesprite_dflt.image = 'large_burst'
        elif streak >= 5:
            self.burstflamesprite_dflt.image = 'medium_burst'
        elif streak >= 3:
            self.burstflamesprite_dflt.image = 'small_burst'
        elif streak == 0:
            self.burstflamesprite_dflt.image = 'xsmall_burst'

    def decelerate(self):
        self.penalty = True


ship = Ship()  # creates the instance


# ---------------------------- Functions --------------------------------------------------

def draw_menu():

    screen.clear()
    menu.draw()

    screen.draw.text(f"F11 : Fullscreen\nESC : Exit Fullscreen\nPause : Spacebar",
                     (10, 15), color=(255, 255, 255), fontsize=16, fontname="retrogaming")

    screen.draw.text(menu.welcome_txt, center=(WIDTH/2, (HEIGHT/2-300)), color="cyan",
                     gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=80, fontname="ocraext")

    screen.draw.text(menu.rules, (0, (HEIGHT/2-150)), color="white", owidth=0.05,
                     ocolor="grey", align="center", lineheight=1.5, fontsize=18, fontname="retrogaming")

    screen.draw.text(menu.tip, (WIDTH-430, (HEIGHT/2-150)), color="white", owidth=0.05,
                     ocolor="grey",  align="center", lineheight=1.5, fontsize=18, fontname="retrogaming")

    screen.draw.text(menu.press_any_key_txt, center=(WIDTH/2, (HEIGHT-100)), color="purple",
                     gcolor="blue", owidth=0.25, ocolor="grey", fontsize=30, fontname="1up")

    screen.draw.text(menu.author, (WIDTH-275, HEIGHT-30), color="seagreen", gcolor="lightcoral",
                     owidth=0.25, ocolor="darkslategray", fontsize=20, fontname="retrogaming")


def draw_game():  # what's in the draw, has to only draw. Can put if's (not manage collision, nor updates)
    global food, total_food, game_over, pause, win, data_file, record_win, max_wasted_food_allowed

    # if I'd want a fullscreen without the option to opt out of it with esc :    screen.surface = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    screen.clear()
    # screen.fill((1, 7, 46)) if no background image
    background.draw()

    screen.draw.rect(BOX, WHITE)

    screen.draw.textbox(str(score), (15, 100, 200, 50),
                        color=(255, 255, 255), gcolor="green")

    screen.draw.text("Amount of food wasted ! : " + str(count_wasted_food),
                     (20, 160), color=(255, 255, 255), gcolor="red", fontsize=40)

    screen.draw.text("Amount of food eaten : " + str(total_food),
                     (20, 200), color=(255, 255, 255), gcolor="gold", fontsize=40)

    screen.draw.text("Current streak : " + str(streak), (20, 240),
                     color=(255, 255, 255), gcolor="green", fontsize=40)

    for poop in poop_list:
        poop.draw()
    # if I want it to appear behind the player, needs to be drawn Before the player. Cause in the draw function, last elements overlaps the latter ones

    player.draw()

    # ____________ Ship draw ____________
    ship.draw()

    # ____________ Player life hearts draw ____________

    if player.life == 1800:
        heart3.image = 'heart_full'
    elif player.life < 1800 and player.life >= 1500:
        heart3.image = 'heart_half'
    elif player.life < 1500:
        heart3.image = 'heart_empty'
    heart3.draw()

    if player.life >= 1200:
        heart2.image = 'heart_full'
    elif player.life < 1200 and player.life >= 900:
        heart2.image = 'heart_half'

    elif player.life < 900:
        heart2.image = 'heart_empty'
    heart2.draw()

    if player.life == 600:
        heart1.image = 'heart_full'
    elif player.life < 600 and player.life >= 300:
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
    if pause == True:
        screen.draw.text("Game Paused", center=(WIDTH/2, (HEIGHT/2 - 200)), color="cyan",
                         gcolor="magenta", owidth=0.25, ocolor="grey", fontsize=100, fontname="ocraext")
        pause_img.pos = [WIDTH/2, (HEIGHT/2 + 100)]
        pause_img.draw()

    # ____________ Above player score draw ____________

    if food_value_score_visible:
        screen.draw.text("100", center=(
            (player.pos[0]+30), (player.pos[1]-player.height-10)), color="white", gcolor="yellow", fontsize=35)

    # ____________ Hurt score ____________
    if enemy_value_score_visible:
        screen.draw.text(
            "-200", center=((player.pos[0]+30), (player.pos[1]-player.height-10)), color="white", gcolor="red", fontsize=35)

    # ____________ Game Over Screen ____________
    if player.life == 0 or count_wasted_food >= max_wasted_food_allowed:
        if not game_over:
            data_file = open(r"data/hiscore.dat", "a")
            data_file.write(str(score) + "\n")
            data_file.close()

        game_over = True

        screen.clear()  # if I want to clear everything, background and onscreen things included
        # background_img = pygame.image.load('nasa_asteroid_1024x614.jpg').convert_alpha()
        # screen.blit(background_img, (0.0))
        # doesn't work : TypeError: invalid destination position for blit       Must be in main directory
        gameover_bg.draw()
        gameover_img.draw()

        screen.draw.text('G a m e  O v e r', center=(WIDTH/2, (HEIGHT/2 - 200)), color="red",
                         gcolor="yellow", owidth=0.30, ocolor="white", fontsize=150, fontname="rh-shmatter")

        if count_wasted_food >= max_wasted_food_allowed:
            screen.draw.text('You wasted too much food ! ! !', (
                40, (HEIGHT/2 + 80)), color="red", gcolor="orange", owidth=0.30, ocolor="lemonchiffon", fontsize=40, fontname="lazysans")
            screen.draw.text('Amount of food wasted : ' + str(count_wasted_food), (WIDTH-440, (HEIGHT/2 + 80)), color="red",
                             gcolor="orange", owidth=0.30, ocolor="lemonchiffon", fontsize=40, fontname="lazysans")

        data_file = open(r"data/hiscore.dat")
        hiscore_list = data_file.readlines()
        data_file.close()

        hiscore = -1000000000000
        for line in hiscore_list:
            if line:  # if there's a line of highscore in file
                s = int(line.strip())
                if s > hiscore:
                    hiscore = s

        screen.draw.text('Highscore: ' + str(hiscore), center=(WIDTH/2, (HEIGHT/2-310)),
                         color="gold", gcolor="goldenrod2", owidth=0.25, ocolor="lemonchiffon", fontsize=70)

        screen.draw.text('Score: ' + str(score), center=(WIDTH/2, (HEIGHT/2-380)),
                         color="gold", gcolor="goldenrod2", owidth=0.25, ocolor="lemonchiffon", fontsize=70)

        screen.draw.text("Total food eaten : " + str(total_food),
                         (20, 130), color=(255, 255, 255), gcolor="gold", fontsize=50)

        gameover_img.pos = [WIDTH/2, (HEIGHT/2 + 100)]

        # Need to create a list of streaks and screen.draw.text only the maximum streak
        # screen.draw.text("Maximum streak : " + str(streak), (20, 200), color=(255,255,255), gcolor="green", fontsize= 40)

    # ____________ Win Screen ____________
    # 0 if end of screen. 215 if planet orbit
    if ship.sprite.pos[0] <= 220+images.planet_express.get_width()*0.33:
        if not win and record_win == False:
            record_win = record_win = True
            data_file = open(r"data/hiscore.dat", "a")
            data_file.write(str(score) + "\n")
            data_file.close()

        win = True

        screen.clear()

        # screen.fill((61,55,21))    #decide if bgcolor black or this brown
        # (HEIGHT/2 + 100) if smaller img
        win_img.pos = [WIDTH/2, (HEIGHT/2 + 100)]

        win_img.draw()

        screen.draw.text("You won ! \n The ship has arrived succesfully !", center=(WIDTH/2, (HEIGHT/2 - 210)),
                         color="seagreen3", gcolor="lightgoldenrod", owidth=0.30, ocolor="lemonchiffon", fontsize=60, fontname="ocraext")

        screen.draw.text('Score: ' + str(score), center=(WIDTH/2, (HEIGHT/2-390)),
                         color="gold", gcolor="goldenrod2", owidth=0.25, ocolor="lemonchiffon", fontsize=60)

        data_file = open(r"data/hiscore.dat")
        hiscore_list = data_file.readlines()
        data_file.close()

        hiscore = -1000000000000
        for line in hiscore_list:
            if line:  # if there's a line of highscore in file
                s = int(line.strip())
                if s > hiscore:
                    hiscore = s

        screen.draw.text('Highscore: ' + str(hiscore), center=(WIDTH/2, (HEIGHT/2-320)),
                         color="gold", gcolor="goldenrod2", owidth=0.25, ocolor="lemonchiffon", fontsize=60)

        screen.draw.text("Total food eaten : " + str(total_food),
                         (20, 130), color=(255, 255, 255), gcolor="gold", fontsize=50)

        # Need to create a list of streaks and screen.draw.text only the maximum streak
        # screen.draw.text("Maximum streak : " + str(streak), (20, 200), color=(255,255,255), gcolor="green", fontsize= 40)


# ++++++++ General Draw ++++++++++

def draw():
    if fullscreen:
        screen.surface = pygame.display.set_mode(
            (WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen.surface = pygame.display.set_mode((WIDTH, HEIGHT))

    if menu_visible == True:
        draw_menu()
    # elif KeyboardEvent or pygame.MOUSEBUTTONDOWN == True:  # CHECK if it works !

    else:
        draw_game()


def random_pos():
    image_width = 64  # food sprite size
    image_heigth = 64
    modifier = max(image_width, image_heigth) // 2
    # not WIDTH-modifier cause here we want the food to stop at WIDTH-200 like the player, for the player to be able to eat/reach every food, and not appear where Bender will appear
    x = randint(modifier, WIDTH - 200)
    y = 0
    return [x, y]


def random_pos_enemy():
    image_width = 105  # beer sprite size
    image_heigth = 105
    modifier = max(image_width, image_heigth) // 2
    x = randint(modifier, WIDTH - 200)
    y = 0
    return [x, y]


def food_update(dt):  # delta time = (difference with time) elapsed time since last update (1/60 of seconds)
    global food_time, food, score, streak, food_value_score_visible, enemy_value_score_visible, streak, total_food, poop, count_wasted_food

    food_time -= dt  # dt = change in time
    if food_time <= 0.0:  # when time is out (like a hourglass) or under 0
        food = Actor('all_food/' + choice(foodnames),
                     anchor=['center', 'top'])  # to put in general update
        pos = food.pos
        pos = random_pos()
        food_list.append(food)
        food_time = randint(1, 2)  # back to (1, 3) ?
        # check following code if too many objects popping, if yes : adjust randint
        if game_time >= 25:
            food_time = randint(0, 2)
        # Increase randint as the time elapsing ?
        food.pos = pos

    # ____________ Collision with player and/or bottom screen ____________
    mvt_x = food_speed[0] * dt  # * 1/60 of sec sec
    mvt_y = food_speed[1] * dt

    # ____________ Ok food collision with player ____________

    for food in food_list:
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

    # food falling out of screen sight :
        # tweak with height from where to remove, so as not to frustrate player when passing by fast over the falling food
        elif food.pos[1] >= HEIGHT - 15:
            food_list.remove(food)
            count_wasted_food += 1
            # no 'break' cause in break-out game example, sprite only touches/collides only with one thing at the time, here, several food can collide together at the same time with the player


def enemy_update(dt):
    global enemy_time, enemy, score, streak, enemy_value_score_visible, enemy_action_trigger_visible, enemy_action_trigger_speed, malus

    enemy_time -= dt
    if enemy_time <= 0.0:
        enemy = Actor("fortran_beer", anchor=['center', 'top'])
        pos = enemy.pos
        pos = random_pos_enemy()
        enemy_list.append(enemy)
        if game_time >= 20:
            enemy_time = randint(1, 3)
        elif game_time >= 10:
            enemy_time = randint(3, 5)
        else:
            enemy_time = randint(5, 7)  # should maybe increment food too

        enemy.pos = pos

      # *** enemy collision with player ***
    mvt_x = enemy_speed[0] * dt
    mvt_y = enemy_speed[1] * dt

    for enemy in enemy_list:
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
            enemy_action_trigger_speed = [-enemy_action_trigger_maxspeed, 0]
            enemy_action_trigger.pos = [WIDTH - 66, HEIGHT-player.height]

        if enemy.pos[1] >= (HEIGHT-10):
            if enemy in enemy_list:
                enemy_list.remove(enemy)


def enemy_action_trigger_update(dt):
    global enemy_action_trigger, enemy_action_trigger_speed, enemy_action_trigger_visible, enemy_action_trigger_time, ROTATION_SPEED, score, streak

    mvt_x = enemy_action_trigger_speed[0] * dt
    mvt_y = enemy_action_trigger_speed[1] * dt
    enemy_action_trigger.angle += ROTATION_SPEED * dt

    enemy_action_trigger.pos = [
        enemy_action_trigger.pos[0] + mvt_x, enemy_action_trigger.pos[1] + mvt_y]

    if player.colliderect(enemy_action_trigger):
        # enemy_action_trigger_visible = False  would make it disappear too abruptly
        sounds.slap_umph.play()
        set_player_hit_angry()

        # don't put the malus score -= here otherwise the wrench rotating will decrease player.life to 0

        enemy_action_trigger_speed = [0, enemy_action_trigger_maxspeed]
        # important to put it here otherwise Bender/enemy_action_trigger will stay out of screen (right of screen) !
        enemy_action.move_back(-132)


def update_game(dt):
    global streak, score, malus_taken, score, game_over, win

    # if not music.is_playing('neocrey_jump_to_win'):   # Makes win screen lag !!
    # music.queue('neocrey_jump_to_win')
    # music.set_volume(0.2)

    if pause:
        music.pause()
        return  # permits the update of game !!!

    if game_over:
        if music.is_playing('neocrey_jump_to_win'):
            music.stop()
            sounds.icy_game_over.play()  # or this_is_game_over
        return

    if win:
        # music.fadeout(0.15)
        if music.is_playing('neocrey_jump_to_win'):
            music.stop()
            # works !!! so doesn't if I wanna play another music
            sounds.littlerobotsoundfactory_jingle_win_00.play()
        # wmusic.play_once('nebula')       #only works when I press ESC or or continously play if I drag the window ?!
        return

    if dt > 0.5:
        return

    if not pause:
        pos = player.pos
        if pos[0] > WIDTH - 5:
            pos[0] = WIDTH - 5
        elif pos[0] < 5:
            pos[0] = 5

        if pos[1] > WIDTH - 5:
            pos[1] = WIDTH - 5
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
        # try different times/secs
        clock.schedule_interval(set_ship_move_normal, 1)

    for poop in poop_list:
        poop.update(dt)


def update_menu(dt):
    if not music.is_playing('neocrey_jump_to_win'):
        music.play('neocrey_jump_to_win')
    # if not music.is_playing('menu_music'): #intro music
        # music.play_once('menu_music')
        # music.queue('neocrey_jump_to_win')
        music.set_volume(0.2)


# ++++++++ General Update here ++++++++

def update(dt):
    global game_time
    game_time += dt

    if menu_visible == True:
        update_menu(dt)
    else:
        update_game(dt)
    # music.fadeout(0.25)       # Makes game lag !!!


def on_mouse_move(pos):
    if pos[0] > 50 and pos[0] < WIDTH - 200:  # WIDTH and HEIGHT of sprite = 296
        x = pos[0]
    elif pos[0] <= 50:
        x = 50
    else:
        x = WIDTH - 200  # breakdown of difference : 50 is half of player sprite. 130 is the approximative siz of sprite of Bender/ennemy. 50 + 130 + 20 margin = 200

    # otherwise player has a loophole (can reposition themself beneath right food if too many Beers)
    if not pause:
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

    if menu_visible == True:
        menu_visible = False
    else:
        if key == keys.SPACE:
            pause = not pause
            music.unpause()  # unsure if I should put it here


def set_enemy_action_animate():
    global enemy_action_visible
    enemy_action.image = 'bender_yay'
    enemy_action.image = 'bender_action'
    clock.schedule_interval(set_enemy_action_normal, 0.7)
    enemy_action_visible = True
    enemy_action.pos = (WIDTH-66, HEIGHT)
    # clock.schedule_interval(set_enemy_action_invisible, 1.50)  --code if I don't move Bender.-- collide bug with poop going towards the ship


def set_enemy_action_normal():
    enemy_action.image = 'bender_idle'


def set_player_eat_then_poop():
    global poop_visible
    player.image = 'nibbler_yay'
    clock.schedule_interval(set_player_normal, 0.8)
    new_poop = Poop()
    # WIDTH/2 -30, HEIGHT-5
    new_poop.pos = (player.pos[0] - 100, player.pos[1])
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
