from mesa import Agent
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

CELL_LENGTH = 1
MAX_SPEED = 1
ACCELERATION = .09
DECELERATION = - 0.17

MAX_WAITING = 20

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
        super().__init__(pos, model)
        self.color = traffic.randomRGB()
        self.type = traffic.BGColor.CAR
        
        self.pos = pos
        self.next_direction = self.getInitialHeading()
        self.direction = self.next_direction
        self.intent = Intent.NONE
        self.real_direction = (0, 0)
        self.speed = 0
        self.acceleration = 0
        self.state = State.ACCELERATING

        self.frac_move = 0

        self.trajectory = [self.direction]
        self.origin_point = self.pos

    def newIntent(self):
        # todo: add logic to change intent based on a list
        return choice([Intent.LEFT, Intent.STRAIGHT, Intent.RIGHT])
    
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
        return - (self.speed + ACCELERATION) / DECELERATION

    @property
    def safe_distance(self):
        # Get the distance needed to stop given the current speed and the DECELERATION rate
        delta_s = ((self.speed + ACCELERATION) * self.time_to_stop) + 0.5 * DECELERATION * (self.time_to_stop ** 2)
        return delta_s
    
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
        if self.state == State.STOPPED:
            return
        # TODO : Go without the trajectory
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
    
    def agent_checks(self):
        cell = self.getCell(self.pos)
        cell = [x for x in cell if x != self]
        cell_types = [x.type for x in cell]
        cell_type_types = [type(x) for x in cell_types]
        if traffic.StColor in cell_type_types:
            # do rule checks
            pass

    
    @property
    def on_stop(self):
        return traffic.StColor in [type(x.type) for x in self.getCell(self.pos)]

    def step(self):
        if not self.pos:
            return
        self.move()

    def to_int(self, tuple):
        return (int(tuple[0]), int(tuple[1]))

    def move(self):
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
        self.agent_checks()
        if self.obstacle_in_front(int((self.safe_distance + self.frac_move))):
            self.state = State.DECELERATING
        else:
            self.state = State.ACCELERATING

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

# class Car(Agent):

#     def __init__(self, pos, model):
#         super().__init__(pos, model)
#         self.color = traffic.randomRGB()
#         self.waiting_time = 0
#         self.pos = pos
#         self.type = traffic.CellColor.CAR
#         self.direction = self.getInitialHeading()
#         self.true_direction = self.direction
#         self.speed = MAX_SPEED
#         self.acceleration = 0
#         self.cockiness = .5
#         self.intent = choice(list(Intent))
#         # self.intent = Intent.LEFT
#         self.intentD = self.direction
#         if self.intent == Intent.RIGHT:
#             self.intentD = (self.direction[1], -self.direction[0])
#         elif self.intent == Intent.LEFT:
#             self.intentD = (-self.direction[1], self.direction[0])
#         self.state = State.CRUISING
#         self.frac_move = 0


#     def getInitialHeading(self):
#         n_types = self.neighbors_types
#         if traffic.CellColor.TRAJECTORY in n_types[1]:
#             return (-1,0)
#         elif traffic.CellColor.TRAJECTORY in n_types[3]:
#             return (0,-1)
#         elif traffic.CellColor.TRAJECTORY in n_types[5]:
#             return (0,1)
#         elif traffic.CellColor.TRAJECTORY in n_types[7]:
#             return (1,0)
#         else:
#             raise Exception("No trajectory found")
        
#     def getTile(self):
#         return 0

#     @property
#     def getIntent(self):
#         return self.intent
    
#     @property
#     def neighborhood(self):
#         return np.array(self.model.grid.get_neighborhood(self.pos, True, include_center=True, radius=1)).reshape((3,3,2))
    
#     @property
#     def relative_neighborhood(self):
#         if self.direction == (1,0):
#             return np.rot90(self.neighborhood, k=2)
#         elif self.direction == (0,1):
#             return np.rot90(self.neighborhood, k=1)
#         elif self.direction == (-1,0):
#             return self.neighborhood
#         elif self.direction == (0,-1):
#             return np.rot90(self.neighborhood, k=-1)
    
#     @property
#     def relative_neighbors(self):
#         r_neighd = self.relative_neighborhood.reshape(9, 2)
#         return [self.model.grid[x] for x in r_neighd]
    
#     @property
#     def neighbors(self):
#         neighs = self.model.grid.get_neighborhood(self.pos, True, include_center=True, radius=1)
#         return [self.model.grid[x] for x in neighs]
    
#     @property
#     def neighbors_types(self):
#         return [[a.type for a in x] for x in self.neighbors]
    
#     @property
#     def relative_neighbors_types(self):
#         return [[a.type for a in x] for x in self.relative_neighbors]
    
#     def find_trajectory(self) -> tuple:
#         candidates = [False] * 9
#         r_neighs = self.relative_neighbors_types
#         for i in range(9):
#             if traffic.CellColor.TRAJECTORY in r_neighs[i]:
#                 candidates[i] = True
#         return candidates
        
#     def typeInCell(self, pos: tuple, type: traffic.CellColor):
#         if pos[0] < 0 or \
#                 pos[0] >= self.model.grid.width or \
#                 pos[1] < 0 or \
#                 pos[1] >= self.model.grid.height:
#             return False
#         for a in self.model.grid[pos]:
#             if a.type == type:
#                 return True
#         return False
        
#     @property
#     def desired_next(self):
#         candidates_pref = [
#             7, 9, 8,
#             5, 0, 6,
#             0, 0, 0
#         ]
#         candidates = self.find_trajectory()
#         if self.intent == Intent.STRAIGHT:
#             candidates[1] *= 2
#         elif self.intent == Intent.RIGHT:
#             candidates[0] = 0
#             candidates[2] *= 2
#             candidates[3] = 0
#         elif self.intent == Intent.LEFT:
#             candidates[0] *= 2
#             candidates[2] = 0
#             candidates[5] = 0
#         candidates = [candidates[i] * candidates_pref[i] for i in range(9)]

#         return candidates.index(max(candidates))
    
#     def is_on(self, type: traffic.CellColor):
#         return type in self.neighbors_types[4]

#     @property
#     def relative_left(self):
#         if self.direction == (1,0):
#             return (0,1)
#         elif self.direction == (0,1):
#             return (-1,0)
#         elif self.direction == (-1,0):
#             return (0,-1)
#         elif self.direction == (0,-1):
#             return (1,0)
        
#     @property
#     def relative_right(self):
#         if self.direction == (1,0):
#             return (0,-1)
#         elif self.direction == (0,1):
#             return (1,0)
#         elif self.direction == (-1,0):
#             return (0,1)
#         elif self.direction == (0,-1):
#             return (-1,0)

#     @property    
#     def rotation(self):
#         if self.direction == (0,1):             # up.
#             return np.array([[0,1],[-1,0]])
#         elif self.direction == (-1,0):          # left
#             return np.array([[1,0],[0,1]])
#         elif self.direction == (0,-1):          # down
#             return np.array([[0,-1],[1,0]])
#         elif self.direction == (1,0):           # right
#             return np.array([[-1,0],[0,-1]])

#     def find_next_type(self, type: traffic.CellColor):
#         df: pd.DataFrame = self.model.interest_points[self.getTile()].loc[type]
#         heading_x, heading_y = self.true_direction
        
#         df['x_dist'] = df.x - self.pos[0]
#         df['y_dist'] = df.y - self.pos[1]
#         df['angle'] = np.arctan2(heading_x * df.y_dist - heading_y * df.x_dist,
#                                  heading_x * df.x_dist + heading_y * df.y_dist)
        
#         df = df[(df.angle == 0)]
#         df['dist'] = np.sqrt(df.x_dist**2 + df.y_dist**2)
#         if df.empty:
#             return None
#         return df.sort_values(by=['dist']).iloc[0]
    
#     def next_in_front(self, type: traffic.CellColor, max_range = 10):
#         for i in range(1, max_range + 1):
#             if self.typeInCell((self.pos[0] + i * self.true_direction[0], self.pos[1] + i * self.true_direction[1]), type):
#                 return i-1
#         return -1
    
#     def dist_from_next_car(self):
#         df = self.find_next_type(traffic.CellColor.CAR)
#         if df is None:
#             return 100
#         return df.dist
    
#     def give_way(self):
#         self.waiting_time += 1
#         # if self.waiting_time > MAX_WAITING:
#         #     self.model.grid.remove_agent(self)
#         #     self.model.schedule.remove(self)
#         #     traffic.tracking.addDNF()
#         #     return True
#         rand = np.random.uniform(0, 10)
#         if rand < self.cockiness:
#             traffic.tracking.addDORKS()
#             return False
#         return True

#     def getCarInPos(self, pos: tuple):
#         for a in self.model.grid[pos]:
#             if a.type == traffic.CellColor.CAR:
#                 return a
#         return None

#     def step(self):
#         if self.is_on(traffic.CellColor.STOP):
#             ruleset = self.model.intersection_rules[traffic.CellColor.STOP.value]
#             ruleset = ruleset[ruleset[INTENT_TO_GIVEWAY[self.intent]] == True]
#             for _, rule in ruleset.iterrows():
#                 rule_vector = np.array([rule.x, rule.y])
#                 abs_x = self.pos[0] + np.dot(self.rotation, rule_vector)[0]
#                 abs_y = self.pos[1] + np.dot(self.rotation, rule_vector)[1]
#                 # sda = traffic.SelfDestructAgent((abs_x, abs_y), self.model)
#                 # self.model.grid.place_agent(sda, (abs_x, abs_y))
#                 # self.model.schedule.add(sda)
#                 if self.typeInCell((abs_x, abs_y), traffic.CellColor.CAR):
#                     other_intent = self.getCarInPos((abs_x, abs_y)).intent
#                     care_val = rule[INTENT_TO_BLINKER[self.intent]]
#                     doesItCare = traffic.model.careDir(other_intent, care_val)
#                     if doesItCare:
#                         if self.give_way():
#                             return
#                         else:
#                             break


#         if self.is_on(traffic.CellColor.DESPAWN):
#             self.model.grid.remove_agent(self)
#             self.model.schedule.remove(self)
#             return
#         self.frac_move += self.speed
#         to_add_x = 0
#         to_add_y = 0
#         if self.desired_next == 0:
#             to_add_x += self.relative_left[0] + self.direction[0]
#             to_add_y += self.relative_left[1] + self.direction[1]
#         elif self.desired_next == 1:
#             to_add_x += self.direction[0]
#             to_add_y += self.direction[1]
#         elif self.desired_next == 2:
#             to_add_x += self.relative_right[0] + self.direction[0]
#             to_add_y += self.relative_right[1] + self.direction[1]
#         elif self.desired_next == 3:
#             to_add_x += self.relative_left[0]
#             to_add_y += self.relative_left[1]
#         elif self.desired_next == 5:
#             to_add_x += self.relative_right[0]
#             to_add_y += self.relative_right[1]

#         new_x = self.pos[0] + to_add_x
#         new_y = self.pos[1] + to_add_y

#         if self.typeInCell((new_x, new_y), traffic.CellColor.CAR):
#             return

#         if self.desired_next == 0:
#             self.true_direction = (self.direction[0] + self.relative_left[0], 
#                                         self.direction[1] + self.relative_left[1])
#         elif self.desired_next == 1:
#             self.true_direction = self.direction
#         elif self.desired_next == 2:
#             self.true_direction = (self.direction[0] + self.relative_right[0],
#                                         self.direction[1] + self.relative_right[1])
#         elif self.desired_next == 3:
#             self.true_direction = self.relative_left
#             self.direction = self.true_direction
#         elif self.desired_next == 5:
#             self.true_direction = self.relative_right
#             self.direction = self.true_direction


#         if self.frac_move >= CELL_LENGTH:
#             self.waiting_time = 0
#             self.frac_move = self.frac_move % CELL_LENGTH
#             new_pos = (new_x, new_y)
#             self.model.grid.move_agent(self, new_pos)
                


    

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
        super().__init__(pos, model)
        self.pos = pos
        self.type = traffic.InColor.SPAWN

    def step(self):
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

    def step(self):
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)

    def advance(self):
        pass