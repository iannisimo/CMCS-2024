from mesa import Agent
from enum import Enum
from random import choice, random
import numpy as np
import traffic

class Intent(Enum):
    STRAIGHT = 1
    RIGHT = 2
    LEFT = 3

class State(Enum):
    ACCELERATING = 1
    DECELERATING = 2
    CRUISING = 3
    STOPPED = 4

class Car(Agent):

    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.type = traffic.CellColor.CAR
        self.direction = self.getInitialHeading()
        self.speed = 1
        self.acceleration = 0
        self.cockiness = random()
        self.intent = choice(list(Intent))
        self.intentD = self.direction
        if self.intent == Intent.RIGHT:
            self.intentD = (self.direction[1], -self.direction[0])
        elif self.intent == Intent.LEFT:
            self.intentD = (-self.direction[1], self.direction[0])
        self.state = State.CRUISING


    def getInitialHeading(self):
        n_types = self.neighbors_types
        if traffic.CellColor.TRAJECTORY in n_types[1]:
            return (-1,0)
        elif traffic.CellColor.TRAJECTORY in n_types[3]:
            return (0,-1)
        elif traffic.CellColor.TRAJECTORY in n_types[5]:
            return (0,1)
        elif traffic.CellColor.TRAJECTORY in n_types[7]:
            return (1,0)
        else:
            raise Exception("No trajectory found")

    @property
    def getIntent(self):
        return self.intent
    
    @property
    def neighborhood(self):
        return np.array(self.model.grid.get_neighborhood(self.pos, True, include_center=True, radius=1)).reshape((3,3,2))
    
    @property
    def neighbors(self):
        neighborhood = self.model.grid.get_neighborhood(self.pos, True, include_center=True, radius=1)
        return [self.model.grid[x] for x in neighborhood]
    
    @property
    def neighbors_types(self):
        return [[a.type for a in x] for x in self.neighbors]

    @property
    def desired_dir(self):
        if self.intent == Intent.STRAIGHT:
            return self.direction
        elif self.intent == Intent.RIGHT:
            pass

    @property
    def desired_pos(self):
        pass        

    def step(self):
        pass

            

    def advance(self) -> None:
        pass

class StaticAgent(Agent):

    def __init__(self, pos, model, type: traffic.CellColor):
        super().__init__(pos, model)
        self.pos = pos
        self.type = type
    
    def step(self):
        pass

    def advance(self):
        pass

class SpawnAgent(Agent):

    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.type = traffic.CellColor.SPAWN

    def step(self):
        if traffic.SPAWN():
            if traffic.CellColor.CAR not in [x.type for x in self.model.grid[self.pos[0]][self.pos[1]]]:
                print("spawning car")
                car = Car(self.pos, self.model)
                self.model.grid.place_agent(car, self.pos)
                self.model.schedule.add(car)
            else:
                print("car already in spawn")