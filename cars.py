import pygame
import os
import random
import threading
import time


# ------------------------------ SETTINGS ------------------------------
num_of_roads_x = 3
num_of_roads_y = 3

# constants
# general
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 800
DIRECTIONS = ["left", "right", "up", "down"]

# colors
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
GREY = (100,100,100)

# frames per second
FPS = 60

# events
CHANGE_LIGHTS_EVENT = pygame.USEREVENT + 1
GATHER_STATISTICS_EVENT = pygame.USEREVENT + 2
GATHER_STATISTICS_INTERVAL = 500

# car properties
CAR_VEL_MAX = 5
CAR_ACC = 0.55 # 0.05
CAR_WIDTH, CAR_HEIGHT = 15, 15
CAR_COLOR = (48,213,200)
COLIDE_DETECT_LENGTH = 3 * CAR_WIDTH

# road properites
ROAD_WIDTH = 40

# intersection properties
INTERSECTION_STOP_BUFOR = CAR_WIDTH
INTERSECTION_LIGHT_BUFOR = 15
INTERSECTION_WIDTH = 70
LIGHT_WIDTH = 10
YELLOW_DURATION = 500
GREEN_DURATION = 1000

# defined light cycles
cycle1 = [
    {
        "duration": GREEN_DURATION,
        "left": {"color": GREEN},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": GREEN},
        "down": {"color": RED}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": RED},
        "right": {"color": GREEN},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": GREEN}
    },
]


cycle2 = [
    {
        "duration": YELLOW_DURATION,
        "left": {"color": YELLOW},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": GREEN},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": YELLOW},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": YELLOW},
        "down": {"color": RED}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": GREEN},
        "down": {"color": RED}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": YELLOW},
        "down": {"color": RED}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": RED},
        "right": {"color": YELLOW},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": RED},
        "right": {"color": GREEN},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": RED},
        "right": {"color": YELLOW},
        "up": {"color": RED},
        "down": {"color": RED}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": YELLOW}
    },
    {
        "duration": GREEN_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": GREEN}
    },
    {
        "duration": YELLOW_DURATION,
        "left": {"color": RED},
        "right": {"color": RED},
        "up": {"color": RED},
        "down": {"color": YELLOW}
    },
]



# ------------------------------ SETUP ------------------------------
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Car Traffic Simulation")



# ------------------------------ CLASSES ------------------------------
class Car:
    def __init__(self, posX: int, posY: int, speed: float, direction: str) -> None:
        self.draw_rect = pygame.Rect(posX, posY, CAR_WIDTH, CAR_HEIGHT)
        self.colide_rect_left = pygame.Rect(posX - COLIDE_DETECT_LENGTH + CAR_WIDTH, posY, COLIDE_DETECT_LENGTH, CAR_HEIGHT)
        self.colide_rect_right = pygame.Rect(posX, posY, COLIDE_DETECT_LENGTH, CAR_HEIGHT)
        self.colide_rect_up = pygame.Rect(posX, posY - COLIDE_DETECT_LENGTH + CAR_HEIGHT, CAR_WIDTH, COLIDE_DETECT_LENGTH)
        self.colide_rect_down = pygame.Rect(posX, posY, CAR_WIDTH, COLIDE_DETECT_LENGTH)
        self.active_colide_rect = None
        self.speed = speed
        self.direction = direction
        self.acceleration = 0
        self.next_turn = DIRECTIONS[random.randint(0, 3)]
        self.stop_timer = Timer()
        self.update_position()
    
    def __str__(self) -> str:
        output = f"direction: {self.direction}\n"
        output += f"active_colide_rect.x: {self.active_colide_rect.x}\n"
        output += f"active_colide_rect.y: {self.active_colide_rect.y}\n"
        output += f"draw_rect.x: {self.draw_rect.x}\n"
        output += f"draw_rect.y: {self.draw_rect.y}\n"
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
        self.colide_rect_left.x = self.draw_rect.x - COLIDE_DETECT_LENGTH + CAR_WIDTH
        self.colide_rect_left.y = self.draw_rect.y
        self.colide_rect_right.x = self.draw_rect.x
        self.colide_rect_right.y = self.draw_rect.y
        self.colide_rect_up.x = self.draw_rect.x
        self.colide_rect_up.y = self.draw_rect.y - COLIDE_DETECT_LENGTH + CAR_HEIGHT
        self.colide_rect_down.x = self.draw_rect.x
        self.colide_rect_down.y = self.draw_rect.y
    
    def update_position(self):
        if self.direction == "left":
            self.draw_rect.x -= round(self.speed)
            self.update_colide_area()
            self.active_colide_rect = self.colide_rect_left
        if self.direction == "right":
            self.draw_rect.x += round(self.speed)
            self.update_colide_area()
            self.active_colide_rect = self.colide_rect_right
        if self.direction == "up":
            self.draw_rect.y -= round(self.speed)
            self.update_colide_area()
            self.active_colide_rect = self.colide_rect_up
        if self.direction == "down":
            self.draw_rect.y += round(self.speed)
            self.update_colide_area()
            self.active_colide_rect = self.colide_rect_down

    def collides_with_car(self, cars: list):
        for car in cars:
            if self == car:
                continue
            if self.active_colide_rect.colliderect(car.draw_rect):
                return True
        return False
    
    def red_light_ahead(self, intersections: list):
        for intersection in intersections:
            for stop_point in intersection.stop_points:
                if self.active_colide_rect.collidepoint(stop_point) and intersection.lights[self.direction]["color"] == RED:
                    return True
            # if self.active_colide_rect.colliderect(intersection.collisionRect) and intersection.lights[self.direction]["color"] == RED:
            #     return True
        return False
    
    def off_screen(sefl):
        if sefl.draw_rect.x < 0 - CAR_WIDTH or sefl.draw_rect.x > SCREEN_WIDTH:
            return True
        if sefl.draw_rect.y < 0 - CAR_HEIGHT or sefl.draw_rect.y > SCREEN_HEIGHT:
            return True
        return False
    
    # check if car is not moving if spped==0 start / continue running timer
    def measure_stop_timer(self):
        if self.speed == 0 and not self.stop_timer.runnung:
            self.stop_timer.start()
        elif self.speed != 0 and self.stop_timer.runnung:
            self.stop_timer.stop()
        else:
            pass

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
            self.spawn_pos_dir1 = ("up", (mid + 0.25 * ROAD_WIDTH, SCREEN_HEIGHT))
            self.spawn_pos_dir2 = ("down", (mid - 0.25 * ROAD_WIDTH, 0))
        elif orientation == "horizontal":
            self.spawn_pos_dir1 = ("right", (0, mid + 0.25 * ROAD_WIDTH))
            self.spawn_pos_dir2 = ("left", (SCREEN_WIDTH, mid - 0.25 * ROAD_WIDTH))
    
    def __str__(self) -> str:
        output = f"orientation: {self.orientation}\n"
        output += f"mid: {self.mid}\n"
        output += f"spawn_pos_dir1: {self.spawn_pos_dir1}\n"
        output += f"spawn_pos_dir2: {self.spawn_pos_dir2}\n"
        return output


class Intersection:
    def __init__(self, mid_x: int, mid_y: int, cycle: list) -> None:
        # if car colides stop_point it stops (but after exiting stop_point it continues ride (must exit intersection))
        self.stop_points = [
            (mid_x - 0.25 * ROAD_WIDTH, mid_y - ROAD_WIDTH/2 - INTERSECTION_STOP_BUFOR),
            (mid_x + ROAD_WIDTH/2 + INTERSECTION_STOP_BUFOR, mid_y - 0.25 * ROAD_WIDTH),
            (mid_x + 0.25 * ROAD_WIDTH, mid_y + ROAD_WIDTH/2 + INTERSECTION_STOP_BUFOR),
            (mid_x - ROAD_WIDTH/2 - INTERSECTION_STOP_BUFOR, mid_y + 0.25 * ROAD_WIDTH)
        ]
        
        # lights direction defines fight for cars heading that directioni.e. lights["left"] mean light for cars moving from right to left
        self.timer = threading.Timer
        self.cycle = cycle
        self.current_phase = 0
        self.lights = {
            "down": {
                "color": RED,
                "rect": pygame.Rect(mid_x - LIGHT_WIDTH - ROAD_WIDTH/2 - 3, mid_y - ROAD_WIDTH/2 - LIGHT_WIDTH - INTERSECTION_LIGHT_BUFOR, LIGHT_WIDTH, LIGHT_WIDTH),
            },
            "left": {
                "color": GREEN,
                "rect": pygame.Rect(mid_x + ROAD_WIDTH/2 + INTERSECTION_LIGHT_BUFOR, mid_y - LIGHT_WIDTH - ROAD_WIDTH/2 - 3, LIGHT_WIDTH, LIGHT_WIDTH),
            },
            "up": {
                "color": RED,
                "rect": pygame.Rect(mid_x + ROAD_WIDTH/2 + 3, mid_y + ROAD_WIDTH/2 + INTERSECTION_LIGHT_BUFOR, LIGHT_WIDTH, LIGHT_WIDTH),
            },
            "right": {
                "color": RED,
                "rect": pygame.Rect(mid_x - LIGHT_WIDTH - ROAD_WIDTH/2 - INTERSECTION_LIGHT_BUFOR, mid_y + ROAD_WIDTH/2 + 3, LIGHT_WIDTH, LIGHT_WIDTH),
            }
        }
    
    def update_phase(self):
        pygame.time.set_timer(CHANGE_LIGHTS_EVENT, self.cycle[self.current_phase]["duration"])
        self.current_phase = (self.current_phase + 1) % len(self.cycle)
        updateDict(self.lights, self.cycle[self.current_phase])


class Timer:
    def __init__(self) -> None:
        self.previous_start_time = None
        self.running_time = 0
        self.runnung = False
    
    def start(self):
        self.previous_start_time = time.time()
        self.runnung = True
    
    def stop(self):
        self.running_time += time.time() - self.previous_start_time
        self.runnung = False
    
    def read_timer(self):
        if self.runnung:
            return self.running_time + time.time() - self.previous_start_time
        return self.running_time
        

# ------------------------------ FUNCTIONS ------------------------------
def updateDict(original, delta):
    original_updated = original
    # update each parameter separately instead of updated = original.upadte(delta) so it doesn't delete parameters that are not being updated
    for parameter in delta:
        if parameter in original_updated:
            if type(delta[parameter]) is dict:
                original_updated.update({parameter: updateDict(original[parameter], delta[parameter])})
            else:
                original_updated.update({parameter: delta[parameter]})
        else:
            original_updated.update({parameter: delta[parameter]})
    return original_updated


# calculates where to put obcjet so the middle ponit of the object was in x_cord_mid and y_cord_mid
def calculate_corner_cord(x_cord_mid: int, y_cord_mid: int, objWidth: int, objHeight: int):
    x_cord_corner = x_cord_mid - 0.5 * objWidth
    y_cord_corner = y_cord_mid - 0.5 * objHeight
    return (x_cord_corner, y_cord_corner)


def draw_window(cars: list[Car], roads: list[Road], intersections: list[Intersection]):
    WIN.fill(WHITE)
    # draw grid
    draw_gird(roads, intersections)
    
    # draw cars
    # test
    # for car in cars:
    #     pygame.draw.rect(WIN, GREEN, car.active_colide_rect)
    # test
    for car in cars:
        # test
        # pygame.draw.rect(WIN, GREEN, car.active_colide_rect)
        # pygame.draw.rect(WIN, GREEN, car.colide_rect_left)
        # pygame.draw.rect(WIN, GREEN, car.colide_rect_right)
        # pygame.draw.rect(WIN, GREEN, car.colide_rect_up)
        # pygame.draw.rect(WIN, GREEN, car.colide_rect_down)
        # test
        pygame.draw.rect(WIN, CAR_COLOR, car.draw_rect)

    pygame.display.update()
    

def cars_movement(cars: list[Car], intersections: list[Intersection]):
    for car in cars:
        # update speed an position
        car.update_speed()
        car.update_position()
        # remove cars which left screen
        if car.off_screen():
            cars.remove(car)
        # stop car if obstacle ahead (otherwise keep moving)
        if car.collides_with_car(cars):
            car.stop()
        elif car.red_light_ahead(intersections):
            car.stop()
        else:
            car.start()
        # update stop timer
        car.measure_stop_timer()


def create_grid(num_of_vertical: int, num_of_horizontal: int):
    roads = []
    intersections = []
    # create roads
    for i in range(num_of_vertical):
        roads.append(Road("vertical", SCREEN_WIDTH * (i+1)/(num_of_vertical+1)))
    for i in range(num_of_horizontal):
        roads.append(Road("horizontal", SCREEN_HEIGHT * (i+1)/(num_of_horizontal+1)))
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
            intersections.append(Intersection(x, y, cycle2))
    return roads, intersections


def draw_gird(roads: list[Road], intersections: list[Intersection]):
    for road in roads:
        if road.orientation == "vertical":
            pygame.draw.line(WIN, GREY, (road.mid, 0), (road.mid, SCREEN_HEIGHT), ROAD_WIDTH)
        if road.orientation == "horizontal":
            pygame.draw.line(WIN, GREY, (0, road.mid), (SCREEN_WIDTH, road.mid), ROAD_WIDTH)
    for intersection in intersections:
        # test
        for stop_point in intersection.stop_points:
            pygame.draw.circle(WIN, BLUE, stop_point, 3)
        # test
        pygame.draw.rect(WIN, intersection.lights["left"]["color"], intersection.lights["left"]["rect"])
        pygame.draw.rect(WIN, intersection.lights["right"]["color"], intersection.lights["right"]["rect"])
        pygame.draw.rect(WIN, intersection.lights["up"]["color"], intersection.lights["up"]["rect"])
        pygame.draw.rect(WIN, intersection.lights["down"]["color"], intersection.lights["down"]["rect"])


# returns spawn positon and direction to be headed
def get_spawn_pos(roads: list[Road]):
    road = roads[random.randint(0, len(roads)-1)]
    if random.randint(0,1) == 0:
        spawnPos = road.spawn_pos_dir1
    else:
        spawnPos = road.spawn_pos_dir2
    return spawnPos


def update_statistics(statistics: dict, cars: list[Car]):
    statistics["number_of_cars"] = len(cars)
    total_stop_time = 0
    for car in cars:
        total_stop_time += car.stop_timer.read_timer()
    avg_stop_time = total_stop_time / len(cars)
    statistics["avg_stop_time"] = avg_stop_time


# ------------------------------ MAIN ------------------------------
def main():
    statistics = {
        "number_of_cars": 0,
        "avg_stop_time": 0
    }
    
    roads, intersections = create_grid(num_of_roads_x, num_of_roads_y)
    cars = []
    
    # test
    # test_car = Car(266, 266, 0, DIRECTIONS[0])
    # test_car.start()
    # cars.append(test_car)
    # test

    pygame.time.set_timer(CHANGE_LIGHTS_EVENT, 1000)
    pygame.time.set_timer(GATHER_STATISTICS_EVENT, GATHER_STATISTICS_INTERVAL)
    clock = pygame.time.Clock()
    run = True
    spawn = 0
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # if event.type == pygame.KEYDOWN:
            #     print("Changed interval")
            #     pygame.time.set_timer(CHANGE_LIGHTS_EVENT, 500)
            if event.type == CHANGE_LIGHTS_EVENT:
                for intersection in intersections:
                    intersection.update_phase()
            if event.type == GATHER_STATISTICS_EVENT:
                update_statistics(statistics, cars)
                print(statistics)
        
        if random.randint(1,4) == 1:
            spawnPos = get_spawn_pos(roads)
            (x,y) = calculate_corner_cord(spawnPos[1][0], spawnPos[1][1], CAR_WIDTH, CAR_HEIGHT)
            new_car = Car(x, y, 0, spawnPos[0])
            if new_car.collides_with_car(cars):
                new_car = None
            else:
                new_car.start()
                cars.append(new_car)

        # test
        # if spawn == 0:
        #     if random.randint(1,4) == 1 or True:
        #         spawnPos = roads[2].spawn_pos_dir1
        #         (x,y) = calculate_corner_cord(spawnPos[1][0], spawnPos[1][1], CAR_WIDTH, CAR_HEIGHT)
        #         new_car = Car(x, y, 0, spawnPos[0])
        #         if new_car.collides_with_car(cars):
        #             new_car = None
        #         else:
        #             new_car.start()
        #             cars.append(new_car)
        # spawn += 1
        # test


        # update_intersections()

        cars_movement(cars, intersections)
        
        # test
        # for car in cars:
        #     print(car.stop_timer.read_timer())
        # test
        # test
        # print(f"len(cars): {len(cars)}")
        # test

        draw_window(cars, roads, intersections)
    
    pygame.quit()


if __name__=="__main__":
    main()
    
    


# Notatki symulacyjne:
# - wpływ światła żółtego (zakładając idealne zachowanie kierowców) vs bez żółtego
# - badanie czasu postoju auta w zależności od czasu trwania sygnalizacji
# - ustalony kierunek wszystkich aut vs losowe skręty
# - badanie wpływu przyśpieszenia i vmax aut
# - na przyszłość ustalanie miejsc docelowych dla każdego auta

# Notatki implementacyjne:
# - dóży wpływ ma punkt rozpoczęcia hamowania przed skrzyżowaniem (zbyt blisko skrzyżowania oznacza zatrzymanie się na skrzyżowaniu)
