import pygame
import os
import random


# Settings
num_of_roads_x = 3
num_of_roads_y = 3








# Setup
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Traffic Simulation")

WHITE = (255,255,255)
RED = (255,0,0)
GREY = (100,100,100)

DIRECTIONS = ["left", "right", "up", "down"]

FPS = 60
CAR_VEL_MAX = 5
CAR_WIDTH, CAR_HEIGHT = 25, 15
ROAD_WIDTH = 40


class Car:
    def __init__(self, rect: pygame.Rect, speed: int, direction: str) -> None:
        self.mainRect = rect

        self.speed = speed
        self.direction = "right"
        self.acceleration = 0
        self.next_turn = DIRECTIONS[random.randint(0, 3)]
    
    def update_speed(self):
        self.speed += self.acceleration
        if self.speed > CAR_VEL_MAX:
            self.speed = CAR_VEL_MAX
            self.acceleration = 0
        if self.speed < 0:
            self.speed = 0
            self.acceleration = 0
    
    def update_position(self):
        if self.direction == "left":
            self.mainRect.x -= self.speed
        if self.direction == "right":
            self.mainRect.x += self.speed
        if self.direction == "up":
            self.mainRect.y -= self.speed
        if self.direction == "left":
            self.mainRect.y += self.speed

    def start(self):
        self.acceleration = 1
    
    def stop(self):
        self.acceleration = -1


def draw_window(cars: list[Car], roads: dict):
    WIN.fill(WHITE)

    draw_gird(roads)

    for car in cars:
        pygame.draw.rect(WIN, RED, car.mainRect)

    pygame.display.update()
    

def cars_movement(cars: list[Car]):
    for car in cars:
        car.update_speed()
        car.update_position()


def create_grid(num_of_vertical: int, num_of_horizontal: int):
    roads = {}
    roads["vertical"] = []     # only x cordinates of the roads
    roads["horizontal"] = []   # only y cordinates of the roads
    for i in range(num_of_vertical):
        # roads.append(pygame.Rect(0, ((i+1) * HEIGHT/(x+1)) - ROAD_WIDTH/2, WIDTH, ROAD_WIDTH))
        roads["vertical"].append((i+1) * WIDTH/(num_of_vertical+1))
    for i in range(num_of_horizontal):
        roads["horizontal"].append((i+1) * HEIGHT/(num_of_vertical+1))
    return roads


def draw_gird(roads: dict):
    for x_cordinate in roads["vertical"]:
        pygame.draw.line(WIN, GREY, (x_cordinate, 0), (x_cordinate, HEIGHT), ROAD_WIDTH)
    for y_cordinate in roads["horizontal"]:
        pygame.draw.line(WIN, GREY, (0, y_cordinate), (WIDTH, y_cordinate), ROAD_WIDTH)


def main():
    roads = create_grid(num_of_roads_x, num_of_roads_y)
    cars = []
    # test
    test_car = Car(pygame.Rect(400, 400, CAR_WIDTH, CAR_HEIGHT), 0, 0)
    test_car.start()
    cars.append(test_car)
    # test

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        # if random.randint(1,40) == 1:
        #     new_car = Car(pygame.Rect(0, 100, CAR_WIDTH, CAR_HEIGHT), CAR_VEL_MAX, 0)
        #     cars.append(new_car)


        cars_movement(cars)
        
        draw_window(cars, roads)
    
    pygame.quit()


if __name__=="__main__":
    main()
