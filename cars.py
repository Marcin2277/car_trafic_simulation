import pygame
import os
import random
import threading


# ------------------------------ SETTINGS ------------------------------
num_of_roads_x = 3
num_of_roads_y = 3








# ------------------------------ SETUP ------------------------------
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Traffic Simulation")

# general
DIRECTIONS = ["left", "right", "up", "down"]
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
GREY = (100,100,100)
FPS = 60
CHANGE_LIGHTS_EVENT = pygame.USEREVENT + 1

# object properties
CAR_VEL_MAX = 5
CAR_ACC = 0.55 # 0.05
CAR_WIDTH, CAR_HEIGHT = 15, 15
CAR_COLOR = (48,213,200)
COLIDE_DETECT_LENGTH = 3 * CAR_WIDTH
ROAD_WIDTH = 40
INTERSECTION_STOP_BUFOR = 5
INTERSECTION_LIGHT_BUFOR = 15
INTERSECTION_WIDTH = 70
LIGHT_WIDTH = 10


# ------------------------------ FUNCTIONS / CLASSES ------------------------------
class Car:
    def __init__(self, posX: int, posY: int, speed: float, direction: str) -> None:
        self.drawRect = pygame.Rect(posX, posY, CAR_WIDTH, CAR_HEIGHT)
        self.colideRectLeft = pygame.Rect(posX - COLIDE_DETECT_LENGTH + CAR_WIDTH, posY, COLIDE_DETECT_LENGTH, CAR_HEIGHT)
        self.colideRectRight = pygame.Rect(posX, posY, COLIDE_DETECT_LENGTH, CAR_HEIGHT)
        self.colideRectUp = pygame.Rect(posX, posY - COLIDE_DETECT_LENGTH + CAR_HEIGHT, CAR_WIDTH, COLIDE_DETECT_LENGTH)
        self.colideRectDown = pygame.Rect(posX, posY, CAR_WIDTH, COLIDE_DETECT_LENGTH)
        self.activeColideRect = None
        self.speed = speed
        self.direction = direction
        self.acceleration = 0
        self.next_turn = DIRECTIONS[random.randint(0, 3)]
        self.update_position()
    
    def __str__(self) -> str:
        output = f"direction: {self.direction}\n"
        output += f"activeColideRect.x: {self.activeColideRect.x}\n"
        output += f"activeColideRect.y: {self.activeColideRect.y}\n"
        output += f"drawRect.x: {self.drawRect.x}\n"
        output += f"drawRect.y: {self.drawRect.y}\n"
        output += f"speed: {self.speed}\n"
        output += f"acceleration: {self.acceleration}\n"
        return output
    
    def update_speed(self):
        self.speed += self.acceleration
        if self.speed > CAR_VEL_MAX:
            self.speed = CAR_VEL_MAX
            self.acceleration = 0
        if self.speed < 0:
            self.speed = 0
            self.acceleration = 0
    
    def update_colide_area(self):
        self.colideRectLeft.x = self.drawRect.x - COLIDE_DETECT_LENGTH + CAR_WIDTH
        self.colideRectLeft.y = self.drawRect.y
        self.colideRectRight.x = self.drawRect.x
        self.colideRectRight.y = self.drawRect.y
        self.colideRectUp.x = self.drawRect.x
        self.colideRectUp.y = self.drawRect.y - COLIDE_DETECT_LENGTH + CAR_HEIGHT
        self.colideRectDown.x = self.drawRect.x
        self.colideRectDown.y = self.drawRect.y
    
    def update_position(self):
        if self.direction == "left":
            self.drawRect.x -= round(self.speed)
            self.update_colide_area()
            self.activeColideRect = self.colideRectLeft
        if self.direction == "right":
            self.drawRect.x += round(self.speed)
            self.update_colide_area()
            self.activeColideRect = self.colideRectRight
        if self.direction == "up":
            self.drawRect.y -= round(self.speed)
            self.update_colide_area()
            self.activeColideRect = self.colideRectUp
        if self.direction == "down":
            self.drawRect.y += round(self.speed)
            self.update_colide_area()
            self.activeColideRect = self.colideRectDown

    def collides_with_car(self, cars: list):
        for car in cars:
            if self == car:
                continue
            if self.activeColideRect.colliderect(car.drawRect):
                return True
        return False
    
    def red_light_ahead(self, intersections: list):
        for intersection in intersections:
            for stopPoint in intersection.stopPoints:
                if self.activeColideRect.collidepoint(stopPoint) and intersection.lights[self.direction]["color"] == RED:
                    return True
            # if self.activeColideRect.colliderect(intersection.collisionRect) and intersection.lights[self.direction]["color"] == RED:
            #     return True
        return False
    
    def off_screen(sefl):
        if sefl.drawRect.x < 0 - CAR_WIDTH or sefl.drawRect.x > WIDTH:
            return True
        if sefl.drawRect.y < 0 - CAR_HEIGHT or sefl.drawRect.y > HEIGHT:
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


class Intersection:
    phases = [
        {
            "left": {"color": GREEN},
            "right": {"color": RED},
            "up": {"color": RED},
            "down": {"color": RED}
        },
        {
            "left": {"color": RED},
            "right": {"color": RED},
            "up": {"color": GREEN},
            "down": {"color": RED}
        },
        {
            "left": {"color": RED},
            "right": {"color": GREEN},
            "up": {"color": RED},
            "down": {"color": RED}
        },
        {
            "left": {"color": RED},
            "right": {"color": RED},
            "up": {"color": RED},
            "down": {"color": GREEN}
        },
    ]
    
    def __init__(self, midX: int, midY: int) -> None:
        # if car colides stopPoint it stops (but after exiting stopPoint it continues ride (must exit intersection))
        self.stopPoints = [
            (midX - 0.25 * ROAD_WIDTH, midY - ROAD_WIDTH/2 - INTERSECTION_STOP_BUFOR),
            (midX + ROAD_WIDTH/2 + INTERSECTION_STOP_BUFOR, midY - 0.25 * ROAD_WIDTH),
            (midX + 0.25 * ROAD_WIDTH, midY + ROAD_WIDTH/2 + INTERSECTION_STOP_BUFOR),
            (midX - ROAD_WIDTH/2 - INTERSECTION_STOP_BUFOR, midY + 0.25 * ROAD_WIDTH)
        ]
        
        # lights direction defines fight for cars heading that directioni.e. lights["left"] mean light for cars moving from right to left
        self.timer = threading.Timer
        self.currentPhase = 0
        self.lights = {
            "down": {
                "color": RED,
                "rect": pygame.Rect(midX - LIGHT_WIDTH - ROAD_WIDTH/2 - 3, midY - ROAD_WIDTH/2 - LIGHT_WIDTH - INTERSECTION_LIGHT_BUFOR, LIGHT_WIDTH, LIGHT_WIDTH),
            },
            "left": {
                "color": GREEN,
                "rect": pygame.Rect(midX + ROAD_WIDTH/2 + INTERSECTION_LIGHT_BUFOR, midY - LIGHT_WIDTH - ROAD_WIDTH/2 - 3, LIGHT_WIDTH, LIGHT_WIDTH),
            },
            "up": {
                "color": RED,
                "rect": pygame.Rect(midX + ROAD_WIDTH/2 + 3, midY + ROAD_WIDTH/2 + INTERSECTION_LIGHT_BUFOR, LIGHT_WIDTH, LIGHT_WIDTH),
            },
            "right": {
                "color": RED,
                "rect": pygame.Rect(midX - LIGHT_WIDTH - ROAD_WIDTH/2 - INTERSECTION_LIGHT_BUFOR, midY + ROAD_WIDTH/2 + 3, LIGHT_WIDTH, LIGHT_WIDTH),
            }
        }
    
    def updatePhase(self):
        self.currentPhase = (self.currentPhase + 1) % 4
        updateDict(self.lights, self.phases[self.currentPhase])
        


def updateDict(original, delta):
    originalUpdated = original
    # update each parameter separately instead of updated = original.upadte(delta) so it doesn't delete parameters that are not being updated
    for parameter in delta:
        if parameter in originalUpdated:
            if type(delta[parameter]) is dict:
                originalUpdated.update({parameter: updateDict(original[parameter], delta[parameter])})
            else:
                originalUpdated.update({parameter: delta[parameter]})
        else:
            originalUpdated.update({parameter: delta[parameter]})
    return originalUpdated


# calculates where to put obcjet so the middle ponit of the object was in xCordMid and yCordMid
def calculateCornerCord(xCordMid: int, yCordMid: int, objWidth: int, objHeight: int):
    xCordCorner = xCordMid - 0.5 * objWidth
    yCordCorner = yCordMid - 0.5 * objHeight
    return (xCordCorner, yCordCorner)


def draw_window(cars: list[Car], roads: list[Road], intersections: list[Intersection]):
    WIN.fill(WHITE)
    # draw grid
    draw_gird(roads, intersections)
    
    # draw cars
    # test
    # for car in cars:
    #     pygame.draw.rect(WIN, GREEN, car.activeColideRect)
    # test
    for car in cars:
        # test
        # pygame.draw.rect(WIN, GREEN, car.activeColideRect)
        # pygame.draw.rect(WIN, GREEN, car.colideRectLeft)
        # pygame.draw.rect(WIN, GREEN, car.colideRectRight)
        # pygame.draw.rect(WIN, GREEN, car.colideRectUp)
        # pygame.draw.rect(WIN, GREEN, car.colideRectDown)
        # test
        pygame.draw.rect(WIN, CAR_COLOR, car.drawRect)

    pygame.display.update()
    

def cars_movement(cars: list[Car], intersections: list[Intersection]):
    for car in cars:
        car.update_speed()
        car.update_position()
        if car.off_screen():
            cars.remove(car)
        if car.collides_with_car(cars):
            car.stop()
        elif car.red_light_ahead(intersections):
            car.stop()
        else:
            car.start()


def create_grid(num_of_vertical: int, num_of_horizontal: int):
    roads = []
    intersections = []
    # create roads
    for i in range(num_of_vertical):
        roads.append(Road("vertical", WIDTH * (i+1)/(num_of_vertical+1)))
    for i in range(num_of_horizontal):
        roads.append(Road("horizontal", HEIGHT * (i+1)/(num_of_horizontal+1)))
    # create intersections
    vertical = []
    horizontal = []
    for road in roads:
        if road.orientation == "vertical":
            vertical.append(road.mid)
        if road.orientation == "horizontal":
            horizontal.append(road.mid)
    for x in vertical:
        for y in horizontal:
            intersections.append(Intersection(x, y))
    return roads, intersections


def draw_gird(roads: list[Road], intersections: list[Intersection]):
    for road in roads:
        if road.orientation == "vertical":
            pygame.draw.line(WIN, GREY, (road.mid, 0), (road.mid, HEIGHT), ROAD_WIDTH)
        if road.orientation == "horizontal":
            pygame.draw.line(WIN, GREY, (0, road.mid), (WIDTH, road.mid), ROAD_WIDTH)
    for intersection in intersections:
        # test
        for stopPoint in intersection.stopPoints:
            pygame.draw.circle(WIN, BLUE, stopPoint, 3)
        # test
        pygame.draw.rect(WIN, intersection.lights["left"]["color"], intersection.lights["left"]["rect"])
        pygame.draw.rect(WIN, intersection.lights["right"]["color"], intersection.lights["right"]["rect"])
        pygame.draw.rect(WIN, intersection.lights["up"]["color"], intersection.lights["up"]["rect"])
        pygame.draw.rect(WIN, intersection.lights["down"]["color"], intersection.lights["down"]["rect"])


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
    roads, intersections = create_grid(num_of_roads_x, num_of_roads_y)
    cars = []
    
    # test
    # test_car = Car(266, 266, 0, DIRECTIONS[0])
    # test_car.start()
    # cars.append(test_car)
    # test

    pygame.time.set_timer(CHANGE_LIGHTS_EVENT, 1000)
    clock = pygame.time.Clock()
    run = True
    spawn = 0
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == CHANGE_LIGHTS_EVENT:
                for intersection in intersections:
                    intersection.updatePhase()
        
        if random.randint(1,4) == 1:
            spawnPos = getSpawnPos(roads)
            (x,y) = calculateCornerCord(spawnPos[1][0], spawnPos[1][1], CAR_WIDTH, CAR_HEIGHT)
            new_car = Car(x, y, 0, spawnPos[0])
            if new_car.collides_with_car(cars):
                new_car = None
            else:
                new_car.start()
                cars.append(new_car)

        # test
        # if spawn == 0:
        #     if random.randint(1,4) == 1 or True:
        #         spawnPos = roads[2].spawnPosDir1
        #         (x,y) = calculateCornerCord(spawnPos[1][0], spawnPos[1][1], CAR_WIDTH, CAR_HEIGHT)
        #         new_car = Car(x, y, 0, spawnPos[0])
        #         if new_car.collides_with_car(cars):
        #             new_car = None
        #         else:
        #             new_car.start()
        #             cars.append(new_car)
        # # spawn += 1
        # test


        # update_intersections()

        cars_movement(cars, intersections)
        # test
        print(f"len(cars): {len(cars)}")
        # test

        draw_window(cars, roads, intersections)
    
    pygame.quit()


if __name__=="__main__":
    main()
    
    


# Notatki:
# - wpływ światła żółtego (zakładając idealne zachowanie kierowców) vs bez żółtego
# - badanie czasu postoju auta w zależności od czasu trwania sygnalizacji
# - ustalony kierunek wszystkich aut vs losowe skręty
# - na przyszłość ustalanie miejsc docelowych dla każdego auta
