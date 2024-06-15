import pygame
import os

WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Traffic Simulation")

WHITE = (255,255,255)
RED = (255,0,0)

FPS = 60
VEL = 5
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55, 40

YELLOW_SPACCESHIP_IMAGE = pygame.image.load(
    os.path.join('Assets', 'spaceship_yellow.png'))
YELLOW_SPACCESHIP = pygame.transform.rotate(pygame.transform.scale(
    YELLOW_SPACCESHIP_IMAGE, (SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 90)
RED_SPACCESHIP_IMAGE = pygame.image.load(
    os.path.join('Assets', 'spaceship_red.png'))
RED_SPACCESHIP = pygame.transform.rotate(pygame.transform.scale(
    RED_SPACCESHIP_IMAGE, (SPACESHIP_WIDTH,SPACESHIP_HEIGHT)), 270)

def draw_window(red, yellow):
    WIN.fill(WHITE)
    WIN.blit(YELLOW_SPACCESHIP, (yellow.x, yellow.y))
    WIN.blit(RED_SPACCESHIP, (red.x, red.y))
    pygame.display.update()


def handle_yellow_movement(keys, yellow):
    if keys[pygame.K_a]: # LEFT
        yellow.x -= VEL
    if keys[pygame.K_d]: # RIGHT
        yellow.x += VEL
    if keys[pygame.K_w]: # UP
        yellow.y -= VEL
    if keys[pygame.K_s]: # DOWN
        yellow.y += VEL


def handle_red_movement(keys, red):
    if keys[pygame.K_LEFT]: # LEFT
        red.x -= VEL
    if keys[pygame.K_RIGHT]: # RIGHT
        red.x += VEL
    if keys[pygame.K_UP]: # UP
        red.y -= VEL
    if keys[pygame.K_DOWN]: # DOWN
        red.y += VEL


def main():
    red = pygame.Rect(700, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)
    yellow = pygame.Rect(100, 300, SPACESHIP_WIDTH, SPACESHIP_HEIGHT)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys_pressed = pygame.key.get_pressed()
        handle_yellow_movement(keys_pressed, yellow)
        handle_red_movement(keys_pressed, red)
        
        draw_window(red, yellow)
    
    pygame.quit()


if __name__=="__main__":
    main()