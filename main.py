import pygame
import math
import random
import os

GAME_NAME = "Pong"
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 300
SCREEN_COLOR = (100, 100, 100)
PADDLE_WIDTH = 5
PADDLE_HEIGHT = 50
PADDLE_COLOR = (200, 200, 0)
BALL_RADIUS = 5
BALL_COLOR = (255, 255, 255)
PADDING = {'horizontal': 5, 'vertical': 5}
GAME_POINT = 6

class Game:
    def __init__(self):
        pygame.display.set_caption(GAME_NAME)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.p1_scoreboard = Scoreboard(side='L')
        self.p2_scoreboard = Scoreboard(side='R')
        self.p1 = Player(side='L')
        self.p2 = Player(side='R')
        self.ball = Ball()
        self.padding_left = Padding(side='L')
        self.padding_right = Padding(side='R')
        self.padding_top = Padding(side='T')
        self.padding_bottom = Padding(side='B')
        self.clock = pygame.time.Clock()
        self.game_over = False
        self.paused = False
        self.resume_time = 0
        self.game_over_blanket = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.replay_button = ReplayButton()
        # Sound source  : https://freesound.org/people/plasterbrain/sounds/243020/
        self.game_start_sound = pygame.mixer.Sound(os.path.join('sounds','game_start.ogg'))

        # Sound source  : https://freesound.org/people/NoiseCollector/sounds/4388/
        # License       : https://creativecommons.org/licenses/by/3.0/
        self.hit_sound = pygame.mixer.Sound(os.path.join('sounds','hit.ogg'))

        # Sound source  : https://freesound.org/people/NoiseCollector/sounds/4387/
        # License       : https://creativecommons.org/licenses/by/3.0/
        self.bounce_sound = pygame.mixer.Sound(os.path.join('sounds','bounce.ogg'))

        # Sound source  : https://freesound.org/people/NoiseCollector/sounds/4386/
        # License       : https://creativecommons.org/licenses/by/3.0/
        self.overflow_sound = pygame.mixer.Sound(os.path.join('sounds','overflow.ogg'))

        # Sound source  : https://freesound.org/people/LittleRobotSoundFactory/sounds/274183/
        # License       : https://creativecommons.org/licenses/by/3.0/
        self.game_win_sound = pygame.mixer.Sound(os.path.join('sounds','game_win.ogg'))

        # Sound source  : https://freesound.org/people/myfox14/sounds/382310/
        self.game_lose_sound = pygame.mixer.Sound(os.path.join('sounds', 'game_lose.ogg'))
        self.all_sprites = self.get_all_sprites_group()

    def start(self):
        self.draw()
        self.pause()
        while True:
            event_queue = pygame.event.get()
            for event in event_queue:
                if event.type == pygame.QUIT:
                    self.stop()
            if self.paused:
                if(pygame.time.get_ticks() >= self.resume_time):
                    self.paused = False
                    self.game_start_sound.play()
                    pygame.mouse.set_visible(False)
            elif self.game_over:
                if self.replay_button.rect.collidepoint(pygame.mouse.get_pos()):
                    self.replay_button.highlight()
                else:
                    self.replay_button.reset()
                self.screen.blit(self.replay_button.image, self.replay_button.rect)
                pygame.display.flip()                
                for event in event_queue:
                    if (event.type==pygame.MOUSEBUTTONDOWN) and (event.button==1) and (self.replay_button.rect.collidepoint(event.pos)):
                        self.replay_button.mouse_down_flag = True
                    elif (event.type==pygame.MOUSEBUTTONUP) and (event.button==1) and (self.replay_button.rect.collidepoint(event.pos)) and self.replay_button.mouse_down_flag:
                        self.play_again()
                        self.replay_button.reset()
                        break
            else:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.p2.move_up()
                elif keys[pygame.K_DOWN]:
                    self.p2.move_down()
                self.p1.update(self.ball)
                if (self.p1.rect.colliderect(self.ball.rect) and (self.ball.speed_x < 0)) or (self.p2.rect.colliderect(self.ball.rect) and (self.ball.speed_x > 0)):
                    self.hit_sound.play()
                    self.ball.set_random_speed(math.copysign(1, -self.ball.speed_x), random.choice([-1,1]))
                else:
                    if self.ball_is_overflowing_left():
                        if self.p2_scoreboard.score == (GAME_POINT-1):
                            self.game_win_sound.play()
                            self.draw_game_over(win_status='WIN!')
                            self.game_over = True
                            continue
                        else:
                            self.overflow_sound.play()
                            self.p2_scoreboard.increment_score()
                            self.p1.reset()
                            self.p2.reset()
                            self.ball.reset()
                            self.pause()
                            continue
                    elif self.ball_is_overflowing_right():
                        if self.p1_scoreboard.score == (GAME_POINT-1):
                            self.game_lose_sound.play()
                            self.draw_game_over(win_status='LOSE')
                            self.game_over = True
                            continue
                        else:
                            self.overflow_sound.play()
                            self.p1_scoreboard.increment_score()
                            self.p1.reset()
                            self.p2.reset()
                            self.ball.reset()
                            self.pause()
                            continue
                if self.padding_top.rect.colliderect(self.ball.rect) and (self.ball.speed_y <= 0):
                    self.bounce_sound.play()
                    self.ball.reverse_speed_y()
                    while self.ball.speed_y==0:
                        self.ball.set_random_speed_y(1)
                elif self.padding_bottom.rect.colliderect(self.ball.rect) and (self.ball.speed_y >= 0):
                    self.bounce_sound.play()
                    self.ball.reverse_speed_y()
                    while self.ball.speed_y==0:
                        self.ball.set_random_speed_y(-1)
                self.ball.move()
                self.draw()
                self.clock.tick(80)

    def get_all_sprites_group(self):
        all_sprites = pygame.sprite.Group()
        all_sprites.add(self.p1_scoreboard)
        all_sprites.add(self.p2_scoreboard)
        all_sprites.add(self.p1)
        all_sprites.add(self.p2)
        all_sprites.add(self.ball)
        all_sprites.add(self.padding_left)
        all_sprites.add(self.padding_right)
        all_sprites.add(self.padding_top)
        all_sprites.add(self.padding_bottom)
        return all_sprites

    def draw(self):
        self.screen.fill(SCREEN_COLOR)
        pygame.draw.line(self.screen, (160, 160, 160), (SCREEN_WIDTH/2, 0), (SCREEN_WIDTH/2, SCREEN_HEIGHT), width=2)
        self.all_sprites.draw(self.screen)
        pygame.display.flip()

    def stop(self):
        pygame.quit()
        quit()

    def ball_is_overflowing_left(self):
        return self.padding_left.rect.colliderect(self.ball.rect)

    def ball_is_overflowing_right(self):
        return self.padding_right.rect.colliderect(self.ball.rect)

    def draw_game_over(self, win_status):
        win_status_dialogue = pygame.font.SysFont('monospace', 60, bold=True).render('YOU '+win_status, 1, (0, 0, 0),)
        self.game_over_blanket.fill((200, 255, 255, 150))
        self.game_over_blanket.blit(win_status_dialogue, ((SCREEN_WIDTH - win_status_dialogue.get_width())/2, SCREEN_HEIGHT/2 - win_status_dialogue.get_height()))        
        self.game_over_blanket.blit(self.replay_button.image, self.replay_button.rect)
        self.screen.blit(self.game_over_blanket,(0,0))
        pygame.display.flip()
        pygame.mouse.set_visible(True)

    def pause(self):
        self.resume_time = pygame.time.get_ticks() + 1000
        self.paused = True

    def play_again(self):
        self.game_over = False
        self.p1_scoreboard.reset()
        self.p2_scoreboard.reset()
        self.p1.reset()
        self.p2.reset()
        self.ball.reset()
        self.draw()
        self.pause()

class Scoreboard(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.font_color = (255,255,255)
        self.font_name = 'monospace'
        self.font_height = 40
        self.side = side
        self.font = pygame.font.SysFont(self.font_name, self.font_height)
        self.score = 0
        self.image = self.font.render(str(self.score), 1, self.font_color)
        self.height_from_top = 5
        self.distance_from_middle = 20
        if self.side=='L':
            topleft = (SCREEN_WIDTH/2 - self.distance_from_middle - self.image.get_width(), self.height_from_top + PADDING['vertical'])
        else:
            topleft = (SCREEN_WIDTH/2 + self.distance_from_middle, self.height_from_top + PADDING['vertical']) 
        self.rect = self.image.get_rect(topleft=topleft)

    def update(self, score):
        self.score = score
        self.image = self.font.render(str(self.score), 1, self.font_color)
        if self.side=='L':
            topleft = (SCREEN_WIDTH/2 - self.distance_from_middle - self.image.get_width(), self.height_from_top + PADDING['vertical'])
        else:
            topleft = (SCREEN_WIDTH/2 + self.distance_from_middle, self.height_from_top + PADDING['vertical']) 
        self.rect = self.image.get_rect(topleft=topleft)

    def reset(self):
        self.update(0)

    def increment_score(self):
        self.update(self.score + 1)

class Player(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(PADDLE_COLOR)
        if side=='L':
            self.topleft = (PADDING['horizontal'], (SCREEN_HEIGHT - PADDLE_HEIGHT)/2)
        else:
            self.topleft = (SCREEN_WIDTH - PADDING['horizontal'] - PADDLE_WIDTH, (SCREEN_HEIGHT - PADDLE_HEIGHT)/2)
        self.rect = self.image.get_rect(topleft=self.topleft)
        self.speed = 3

    def move_up(self):
        self.rect.move_ip(0,-self.speed)
        self.overflow_check()

    def move_down(self):
        self.rect.move_ip(0,self.speed)
        self.overflow_check()

    def update(self, ball):
        if(ball.speed_x < 0):
            time = ball.rect.x/(-ball.speed_x)
            y = ball.rect.y + time*ball.speed_y
            if y >= self.rect.bottom:
                self.move_down()
            elif y <= self.rect.top:
                self.move_up()

    def overflow_check(self):
        self.rect.top = max(PADDING['vertical'], self.rect.top)
        self.rect.bottom = min(SCREEN_HEIGHT - PADDING['vertical'], self.rect.bottom)

    def reset(self):
        self.rect = self.image.get_rect(topleft=self.topleft)

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2*BALL_RADIUS, 2*BALL_RADIUS))
        self.image.fill(SCREEN_COLOR)
        pygame.draw.circle(self.image, BALL_COLOR, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.topleft = (SCREEN_WIDTH/2 - BALL_RADIUS, PADDING['vertical']+1)
        self.rect = self.image.get_rect(topleft=self.topleft)
        self.speed_sample_space = {'x':[3,4,5], 'y':[0,2,3,4,5]}
        self.set_speed_x(-2)
        self.set_speed_y(2)

    def move(self):
        self.rect.move_ip(self.speed_x, self.speed_y)

    def reset(self):
        self.rect = self.image.get_rect(topleft=self.topleft)
        self.set_speed_x(-2)
        self.set_speed_y(2)

    def set_speed_x(self, x):
        self.speed_x = x

    def set_speed_y(self, y):
        self.speed_y = y

    def set_random_speed_y(self, dir):
        self.set_speed_y(dir*random.choice(self.speed_sample_space['y']))

    def set_random_speed_x(self, dir):
        self.set_speed_x(dir*random.choice(self.speed_sample_space['x']))

    def set_random_speed(self, x_dir, y_dir):
        self.set_random_speed_x(x_dir)
        self.set_random_speed_y(y_dir)

    def reverse_speed_y(self):
        self.set_speed_y(-self.speed_y)

class Padding(pygame.sprite.Sprite):
    def __init__(self, side):
        super().__init__()
        self.vertical_padding_color = (160, 160, 160)
        if side=='L':
            self.image = pygame.Surface((PADDING['horizontal'], SCREEN_HEIGHT - 2*PADDING['vertical']))
            self.image.fill(SCREEN_COLOR)
            self.topleft = (0, PADDING['vertical'])
        elif side=='R':
            self.image = pygame.Surface((PADDING['horizontal'], SCREEN_HEIGHT - 2*PADDING['vertical']))
            self.image.fill(SCREEN_COLOR)
            self.topleft = (SCREEN_WIDTH - PADDING['horizontal'], PADDING['vertical'])
        elif side=='T':
            self.image = pygame.Surface((SCREEN_WIDTH, PADDING['vertical']))
            self.image.fill(self.vertical_padding_color)
            self.topleft = (0, 0)
        else:
            self.image = pygame.Surface((SCREEN_WIDTH, PADDING['vertical']))
            self.image.fill(self.vertical_padding_color)
            self.topleft = (0, SCREEN_HEIGHT - PADDING['vertical'])
        self.rect = self.image.get_rect(topleft=self.topleft)

class ReplayButton():
    def __init__(self):
        self.font_name = 'monospace'
        self.font_height = 20
        self.image = pygame.font.SysFont(self.font_name, self.font_height, bold=True).render('--Play again--', 1, (200, 200, 0), (255, 0, 0))
        self.topleft = ((SCREEN_WIDTH - self.image.get_width())/2, SCREEN_HEIGHT/2)
        self.rect = self.image.get_rect(topleft=self.topleft)
        self.mouse_down_flag = False

    def highlight(self):
        self.image = pygame.font.SysFont(self.font_name, self.font_height, bold=True).render('--Play again--', 1, (255, 255, 0), (200, 0, 0))

    def reset(self):
        self.image = pygame.font.SysFont(self.font_name, self.font_height, bold=True).render('--Play again--', 1, (200, 200, 0), (255, 0, 0))
        self.mouse_down_flag = False

pygame.init()
Game().start()


