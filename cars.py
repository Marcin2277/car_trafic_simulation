import pygame
import os
import random


# ------------------------------ SETTINGS ------------------------------
num_of_roads_x = 2
num_of_roads_y = 2








# ------------------------------ SETUP ------------------------------
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Traffic Simulation")

# general
DIRECTIONS = ["left", "right", "up", "down"]
WHITE = (255,255,255)
RED = (255,0,0)
GREY = (100,100,100)
FPS = 60

# object properties
CAR_VEL_MAX = 5
CAR_ACC = 0.05
CAR_WIDTH, CAR_HEIGHT = 15, 15
ROAD_WIDTH = 40


# ------------------------------ FUNCTIONS / CLASSES ------------------------------
class Car:
    def __init__(self, posX: int, posY: int, speed: float, direction: str) -> None:
        self.mainRect = pygame.Rect(posX, posY, CAR_WIDTH, CAR_HEIGHT)
        self.speed = speed
        self.direction = direction
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
            self.mainRect.x -= round(self.speed)
        if self.direction == "right":
            self.mainRect.x += round(self.speed)
        if self.direction == "up":
            self.mainRect.y -= round(self.speed)
        if self.direction == "down":
            self.mainRect.y += round(self.speed)

    def colides_with_car(self, cars: list):
        # sposób 1
        # if self.mainRect.collideobjects(cars, key=lambda o: o.mainRect):
        #     return True
        # return False

        # sposób 2
        for car in cars:
            if self == car:
                continue
            if self.mainRect.colliderect(car.mainRect):
                return True
        return False
    
    def off_screen(sefl):
        print(f"x: {sefl.mainRect.x}")
        if sefl.mainRect.x < 0 - CAR_WIDTH or sefl.mainRect.x > WIDTH:
            return True
        if sefl.mainRect.y < 0 - CAR_HEIGHT or sefl.mainRect.y > HEIGHT:
            return True
        return False

    def start(self):
        self.acceleration = CAR_ACC
    
    def stop(self):
        self.acceleration = -1 * CAR_ACC


class Road:
    def __init__(self, orientation: str, mid: int) -> None:
        self.orientation = orientation
        self.mid = mid                      # x cordinate of the middle of the road
        if orientation == "vertical":
            # touple containing directions and x cordinate for cars moving that direction
            self.spawnPosDir1 = ("up", (mid + 0.25 * ROAD_WIDTH, HEIGHT))
            self.spawnPosDir2 = ("down", (mid - 0.25 * ROAD_WIDTH, 0))
        elif orientation == "horizontal":
            self.spawnPosDir1 = ("right", (0, mid + 0.25 * ROAD_WIDTH))
            self.spawnPosDir2 = ("left", (WIDTH, mid - 0.25 * ROAD_WIDTH))
    
    def __str__(self) -> str:
        output = f"orientation: {self.orientation}\n"
        output += f"mid: {self.mid}\n"
        output += f"spawnPosDir1: {self.spawnPosDir1}\n"
        output += f"spawnPosDir2: {self.spawnPosDir2}\n"
        return output


# calculates where to put obcjet so the middle ponit of the object was in xCordMid and yCordMid
def calculateCornerCord(xCordMid: int, yCordMid: int, objWidth: int, objHeight: int):
    xCordCorner = xCordMid - 0.5 * objWidth
    yCordCorner = yCordMid - 0.5 * objHeight
    return (xCordCorner, yCordCorner)


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
        if car.off_screen():
            cars.remove(car)
            print("off screen")
        if car.colides_with_car(cars):
            car.stop()


def create_grid(num_of_vertical: int, num_of_horizontal: int):
    roads = []
    for i in range(num_of_vertical):
        roads.append(Road("vertical", WIDTH * (i+1)/(num_of_vertical+1)))
    for i in range(num_of_horizontal):
        roads.append(Road("horizontal", HEIGHT * (i+1)/(num_of_horizontal+1)))
    return roads


def draw_gird(roads: list[Road]):
    for road in roads:
        if road.orientation == "vertical":
            pygame.draw.line(WIN, GREY, (road.mid, 0), (road.mid, HEIGHT), ROAD_WIDTH)
        if road.orientation == "horizontal":
            pygame.draw.line(WIN, GREY, (0, road.mid), (WIDTH, road.mid), ROAD_WIDTH)


# returns spawn positon and direction to be headed
def getSpawnPos(roads: list[Road]):
    road = roads[random.randint(0, len(roads)-1)]
    if random.randint(0,1) == 0:
        spawnPos = road.spawnPosDir1
    else:
        spawnPos = road.spawnPosDir2
    return spawnPos


# ------------------------------ MAIN ------------------------------
def main():
    roads = create_grid(num_of_roads_x, num_of_roads_y)
    cars = []
    
    # test
    test_car = Car(266, 266, 0, DIRECTIONS[0])
    # test_car.start()
    cars.append(test_car)
    # test

    clock = pygame.time.Clock()
    run = True
    spawn = 0
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        # if random.randint(1,4) == 1:
        #     spawnPos = getSpawnPos(roads)
        #     (x,y) = calculateCornerCord(spawnPos[1][0], spawnPos[1][1], CAR_WIDTH, CAR_HEIGHT)
        #     new_car = Car(x, y, 0, spawnPos[0])
        #     if new_car.colides_with_car(cars):
        #         pass
        #     else:
        #         new_car.start()
        #         cars.append(new_car)

        # test
        if spawn == 0:
            if random.randint(1,4) == 1 or True:
                spawnPos = roads[2].spawnPosDir1
                (x,y) = calculateCornerCord(spawnPos[1][0], spawnPos[1][1], CAR_WIDTH, CAR_HEIGHT)
                new_car = Car(x, y, 0, spawnPos[0])
                if new_car.colides_with_car(cars):
                    new_car = None
                else:
                    new_car.start()
                    cars.append(new_car)
        # spawn += 1
        # test


        # test
        print(f"len(cars): {len(cars)}")
        # test
        cars_movement(cars)
        # test
        print(f"len(cars): {len(cars)}")
        # test

        draw_window(cars, roads)
    
    pygame.quit()


if __name__=="__main__":
    main()
