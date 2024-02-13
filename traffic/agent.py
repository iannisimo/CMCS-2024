from mesa import Agent, Model
from enum import Enum
from random import choice, random
import numpy as np
import pandas as pd
import traffic


def rotate(vector, direction):
    if direction == (0,1):             # up.
        return np.dot(np.array([[0,1],[-1,0]]), vector)
    elif direction == (-1,0):          # left
        return np.dot(np.array([[1,0],[0,1]]), vector)
    elif direction == (0,-1):          # down
        return np.dot(np.array([[0,-1],[1,0]]), vector)
    elif direction == (1,0):           # right
        return np.dot(np.array([[-1,0],[0,-1]]), vector)
    
def rotateIntent(intentD, direction):
    if direction == (-1, 0):
        if intentD == (1, 0):
            return traffic.RelativeDirection.DOWN
        elif intentD == (-1, 0):
            return traffic.RelativeDirection.UP
        elif intentD == (0, 1):
            return traffic.RelativeDirection.RIGHT
        elif intentD == (0, -1):
            return traffic.RelativeDirection.LEFT
    elif direction == (0, 1):
        if intentD == (1, 0):
            return traffic.RelativeDirection.RIGHT
        elif intentD == (-1, 0):
            return traffic.RelativeDirection.LEFT
        elif intentD == (0, 1):
            return traffic.RelativeDirection.UP
        elif intentD == (0, -1):
            return traffic.RelativeDirection.DOWN
    elif direction == (1, 0):
        if intentD == (1, 0):
            return traffic.RelativeDirection.UP
        elif intentD == (-1, 0):
            return traffic.RelativeDirection.DOWN
        elif intentD == (0, 1):
            return traffic.RelativeDirection.LEFT
        elif intentD == (0, -1):
            return traffic.RelativeDirection.RIGHT
    elif direction == (0, -1):
        if intentD == (1, 0):
            return traffic.RelativeDirection.LEFT
        elif intentD == (-1, 0):
            return traffic.RelativeDirection.RIGHT
        elif intentD == (0, 1):
            return traffic.RelativeDirection.DOWN
        elif intentD == (0, -1):
            return traffic.RelativeDirection.UP

def Rel2Intent(rel):
    if rel == traffic.RelativeDirection.UP: return Intent.STRAIGHT
    if rel == traffic.RelativeDirection.LEFT: return Intent.LEFT
    if rel == traffic.RelativeDirection.RIGHT: return Intent.RIGHT


def rotatePath(path_i_0, path_i_1):
    return Rel2Intent(rotateIntent(path_i_0, path_i_1))


CELL_LENGTH = 1
MAX_SPEED = 1
ACCELERATION = .09
DECELERATION = - 0.17

DEADLOCK_PATIENCE = 4

class Intent(Enum):
    STRAIGHT = 0
    RIGHT = 1
    LEFT = 2
    NONE = 3

INTENT_TO_GIVEWAY = {
    Intent.LEFT: 'give_left',
    Intent.STRAIGHT: 'give_straight',
    Intent.RIGHT: 'give_right',
}

INTENT_TO_BLINKER = {
    Intent.LEFT: 'blinker_left',
    Intent.STRAIGHT: 'blinker_straight',
    Intent.RIGHT: 'blinker_right',
}

class State(Enum):
    ACCELERATING = 1
    DECELERATING = 2
    CRUISING = 3
    STOPPED = 4

class Car(Agent):
    def __init__(self, pos, model):
        super().__init__(model.next_uid(), model)
        self.color = traffic.randomRGB()
        self.type = traffic.BGColor.CAR
        
        self.pos = pos
        self.next_direction = self.getInitialHeading()
        self.direction = self.next_direction
        self.initialD = self.direction
        self.intent = Intent.NONE
        self.real_direction = (0, 0)
        self.speed = 0
        self.acceleration = 0
        self.state = State.ACCELERATING

        self.frac_move = 0

        self.trajectory = [self.direction]
        self.origin_point = self.pos

        self.dlocked = 0
        self.last_dlock = None

        path, _ = self.model.get_path(self.pos)
        self.intents = [rotatePath(path[i-1], path[i]) for i in range(1, len(path))]

        self.mean_speed = 0

        self.total_steps = 0

    def add_to_mean(self, old_mean, new_val):
        return ((self.total_steps - 1) / self.total_steps) * old_mean + (new_val / self.total_steps)

    def newIntent(self):
        # return choice([Intent.STRAIGHT, Intent.LEFT, Intent.RIGHT])
        return self.intents.pop(0)
    
    def getCell(self, pos):
        return self.model.grid[pos] if pos[0] >= 0 and pos[0] < self.model.grid.width and pos[1] >= 0 and pos[1] < self.model.grid.height else []
    
    def isCellEmpty(self, pos):
        return len(self.getCell(pos)) == 0

    def getInitialHeading(self):
        headings = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for h in headings:
            if not self.isCellEmpty((self.pos[0] + h[0], self.pos[1] + h[1])):
                return h

    @property
    def intentD(self):
        if self.intent == Intent.RIGHT:
            return (self.direction[1], -self.direction[0])
        elif self.intent == Intent.LEFT:
            return (-self.direction[1], self.direction[0])
        elif self.intent == Intent.STRAIGHT:
            return self.direction
        return (0, 0)
    
    def rotateTrajectory(self, trajectory):
        return [rotate(np.array([x[0], x[1]]), self.direction) for x in trajectory]

    def check_type_under_me(self, type_to_check):
        cell = self.getCell(self.pos)
        cell_types = [type(x.type) for x in cell]
        filtered_to_type = [x for x in cell if type(x.type) == type_to_check]
        if len(filtered_to_type) > 0:
            return filtered_to_type[0]
        return None
    
    @property
    def time_to_stop(self):
        return - (self.speed) / DECELERATION

    @property
    def safe_distance(self):
        # Get the distance needed to stop given the current speed and the DECELERATION rate
        delta_s = ((self.speed) * self.time_to_stop) + 0.5 * DECELERATION * (self.time_to_stop ** 2)
        return delta_s
    
    def car_at(self, pos):
        cell = self.getCell(pos)
        cell = [x for x in cell if x != self]
        cell_types = [x.type for x in cell]
        if traffic.BGColor.CAR in cell_types:
            return [x for x in cell if x.type == traffic.BGColor.CAR][0]
        return None
    
    def redlight_at(self, pos):
        cell = self.getCell(pos)
        cell = [x for x in cell if x != self]
        cell_types = [x.type for x in cell]
        if traffic.TLColor.RED in cell_types:
            return True
        return False
        
    def obstacle_at(self, pos, last=False):
        cell = self.getCell(pos)
        cell = [x for x in cell if x != self]
        cell_types = [x.type for x in cell]
        cell_type_types = [type(x) for x in cell_types]
        if traffic.BGColor.CAR in cell_types:
            return True
        elif traffic.StColor in cell_type_types:
            return True and not last
        return False
    
    def obstacle_in_front(self, up_to):
        traj_len = len(self.trajectory)
        traj = self.trajectory if traj_len > 0 else [(0, 0)]
        origin = self.origin_point if traj_len > 0 else self.pos
        for i in range(0, up_to + 1):
            if i < traj_len:
                pos = (origin[0] + traj[i][0], origin[1] + traj[i][1])
            else:
                pos = (
                    origin[0] + (traj[traj_len - 1][0]) + (i - traj_len + 1) * self.real_direction[0], 
                    origin[1] + (traj[traj_len - 1][1]) + (i - traj_len + 1) * self.real_direction[1])
            if self.obstacle_at(pos, i == up_to):
                return True
        return False
                

    # Retrun false if needs to be removed
    def simulation_checks(self, pos):
        cell = self.getCell(pos)
        cell = [x for x in cell if x != self]
        cell_types = [x.type for x in cell]
        cell_type_types = [type(x) for x in cell_types]
        # check if is on new origin
        if traffic.OrColor in cell_type_types:
            self.direction = self.next_direction
            new_origin = [x.type for x in cell if type(x.type) == traffic.OrColor][0]
            self.intent = self.newIntent()
            self.trajectory = self.rotateTrajectory(self.model.trjs[new_origin][self.intent])
            self.origin_point = pos
            self.direction = (int(self.trajectory[0][0]), int(self.trajectory[0][1]))
            self.initialD = self.direction

        # check if is on despawn
        if traffic.InColor.DESPAWN in cell_types:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.already_spawned = False
            self.model.despawned += 1
            return False
        # check if crashed with another car
        if traffic.BGColor.CAR in cell_types:
            for a in cell + [self]:
                if a.type == traffic.BGColor.CAR:
                    self.model.grid.remove_agent(a)
                    self.model.schedule.remove(a)
                    self.model.crashed += 1
            return False
        
        return True
    
    # return false if needs to stay in place
    def agent_checks(self):
        ret = True
        cell = self.getCell(self.pos)
        cell = [x for x in cell if x != self]
        cell_types = [x.type for x in cell]
        cell_type_types = [type(x) for x in cell_types]
        if traffic.StColor in cell_type_types:
            stop = [x for x in cell if type(x.type) == traffic.StColor][0]
            rules = self.model.rules[stop.type]
            if stop.type in self.model.dlocks:
                colors = ''
                for dlock in self.model.dlocks[stop.type].iterrows():
                    d_xy = rotate((dlock[1]['x'], dlock[1]['y']), self.direction)
                    d_pos = (self.pos[0] + d_xy[0], self.pos[1] + d_xy[1])
                    other = self.car_at(d_pos)
                    other_col = other.color if other != None else '000000'
                    colors += other_col
                if self.last_dlock == colors:
                    self.dlocked += 1
                else:
                    self.dlocked = 0
                    self.last_dlock = colors
            giveway = INTENT_TO_GIVEWAY[self.intent]
            rules = rules[rules[giveway] != 0]
            for rule in rules.iterrows():
                r_xy = rotate((rule[1]['x'], rule[1]['y']), self.direction)
                r_pos = (self.pos[0] + r_xy[0], self.pos[1] + r_xy[1])
                # TODO Optimize if too slow
                if self.redlight_at(r_pos):
                    return False
                other = self.car_at(r_pos)
                r = rule[1][giveway]
                if other:
                    # print(f'I am {self.color} - {self.intent} and I am giving way to {other.color} - {other.intent} at {r_pos}')
                    iCanGo = traffic.doYouKnowTheWay(r, rotateIntent(other.intentD, self.direction))
                    # print(f'I can{"" if iCanGo else "not"} go')
                    if not iCanGo:
                        ret = False
        if self.dlocked > DEADLOCK_PATIENCE and ret == False:
            if random() < 1/8:
                ret = True
                # print(f'I am {self.color} - {self.intent} and i choose so go.')
        return ret

    
    @property
    def on_stop(self):
        return traffic.StColor in [type(x.type) for x in self.getCell(self.pos)]

    def step(self):
        self.total_steps += 1
        if not self.pos:
            return
        self.move()
        self.mean_speed = self.add_to_mean(self.mean_speed, self.speed)
        if self.total_steps > 10: 
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)

    def to_int(self, tuple):
        return (int(tuple[0]), int(tuple[1]))

    def move(self):
        if self.obstacle_in_front(int((self.safe_distance + self.frac_move))):
            self.state = State.DECELERATING
        else:
            self.state = State.ACCELERATING
        match self.state:
            case State.ACCELERATING:
                self.speed += ACCELERATION
                if self.speed > MAX_SPEED:
                    self.speed = MAX_SPEED
                    self.state = State.CRUISING
            case State.DECELERATING:
                self.speed += DECELERATION
                if self.speed < 0:
                    self.speed = 0
                    self.state = State.STOPPED
            case State.CRUISING:
                self.speed = MAX_SPEED
            case State.STOPPED:
                self.speed = 0
        if not self.agent_checks():
            return

        self.frac_move += self.speed
        moves = int(self.frac_move / CELL_LENGTH)
        self.frac_move = self.frac_move % CELL_LENGTH
        next_pos = self.pos
        for i in range(moves):
            if not self.simulation_checks(next_pos): return
            if len(self.trajectory) > 0:
                pos = next_pos
                next_pos = (self.origin_point[0] + self.trajectory[0][0], self.origin_point[1] + self.trajectory[0][1])
                self.real_direction = (
                    next_pos[0] - pos[0],
                    next_pos[1] - pos[1]
                )
                if self.real_direction[0] == 0 or self.real_direction[1] == 0:
                    self.next_direction = self.to_int(self.real_direction)
                del self.trajectory[0]
            else:
                next_pos = (next_pos[0] + self.real_direction[0], next_pos[1] + self.real_direction[1])
        self.model.grid.move_agent(self, next_pos)
        self.pos = next_pos


class StaticAgent(Agent):

    def __init__(self, pos, model, type: traffic.Color):
        super().__init__(pos, model)
        self.pos = pos
        self.type = type
    
    def step(self):
        pass

    def advance(self):
        pass

class SpawnAgent(Agent):

    def __init__(self, pos, model):
        super().__init__(model.next_uid(), model)
        self.pos = pos
        self.type = traffic.InColor.SPAWN

    def step(self):
        # if self.model.already_spawned: return
        if traffic.SPAWN():
            self.model.already_spawned = True
            if Car not in [type(x) for x in self.model.grid[self.pos[0]][self.pos[1]]]:
                car = Car(self.pos, self.model)
                self.model.grid.place_agent(car, self.pos)
                self.model.schedule.add(car)
                self.model.spawned += 1
            else:
                pass

class SelfDestructAgent(Agent):

    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.type = traffic.InColor.DESPAWN
        self.model.grid.place_agent(self, self.pos)
        self.model.schedule.add(self)

    def step(self):
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)

    def advance(self):
        pass

class TrafficLightController(Agent):
    def __init__(self, pos, model):
        super().__init__(model.next_uid(), model)
        self.pos = pos
        self.type = traffic.InColor.TRAFFIC_LIGHT
        self.state = False
        self.time = 0
        
        for i in [-2, 2]:
            for j in [-2, 2]:
                tl = traffic.TrafficLight((pos[0] + i, pos[1] + j), model)
                model.grid.place_agent(tl, (pos[0] + i, pos[1] + j))


    def step(self):

        if self.time == 0:
            self.state = not self.state
            if self.state:
                self.model.grid[self.pos[0] -2][self.pos[1]-2][0].type = traffic.TLColor.GREEN
                self.model.grid[self.pos[0] +2][self.pos[1]+2][0].type = traffic.TLColor.GREEN
                self.model.grid[self.pos[0] -2][self.pos[1]+2][0].type = traffic.TLColor.RED
                self.model.grid[self.pos[0] +2][self.pos[1]-2][0].type = traffic.TLColor.RED

            else:
                self.model.grid[self.pos[0] -2][self.pos[1]-2][0].type = traffic.TLColor.RED
                self.model.grid[self.pos[0] +2][self.pos[1]+2][0].type = traffic.TLColor.RED
                self.model.grid[self.pos[0] -2][self.pos[1]+2][0].type = traffic.TLColor.GREEN
                self.model.grid[self.pos[0] +2][self.pos[1]-2][0].type = traffic.TLColor.GREEN

        # elif self.time == 7:
            
        #     if self.state:
        #         self.model.grid[self.pos[0] -2][self.pos[1]-2][0].type = traffic.TLColor.YELLOW
        #         self.model.grid[self.pos[0] +2][self.pos[1]+2][0].type = traffic.TLColor.YELLOW
            
        #     else:
        #         self.model.grid[self.pos[0] -2][self.pos[1]+2][0].type = traffic.TLColor.YELLOW
        #         self.model.grid[self.pos[0] +2][self.pos[1]-2][0].type = traffic.TLColor.YELLOW
            
            
        self.time = (self.time + 1) % 100


class TrafficLight(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.type = traffic.TLColor.RED

class InfoAgent(Agent):

    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)
    
class MaxVerstappen(Car):
    def __init__(self, pos, model):
        super().__init__(model.next_uid(), model)

    @property
    def speed(self):
        return 3
    
    @speed.setter
    def speed(self, value):
        pass