import numpy as np
from enum import Enum
import traffic
import numpy as np
from gimpformats.gimpXcfDocument import GimpDocument

class RelativeDirection(Enum):
    UP = 3
    RIGHT = 2
    DOWN = 1
    LEFT = 0

class Color(Enum):
    pass

# Static cells
class BGColor(Color):
    EMPTY = '000000'
    ROAD = '010101'
    CAR = '000000'
    WHITE = 'ffffff'

# Interest points
class InColor(Color):
    SPAWN = '0000ff'
    DESPAWN = 'ff00ff'
    TRAFFIC_LIGHT = '00ff00'

# Stop signal
    # When crossing, stop and find the related ruleset
class StColor(Color):
    STOP_4_ISECTION = 'ff8800'

class TLColor(Color):
    RED = 'ff0000'
    YELLOW = 'ffff00'
    GREEN = '00ff00'

# Origin of the tile
    # Get the new trajectory for the car
class OrColor(Color):
    ORIGIN_4_ISECTION   = 'ff88ff'
    ORIGIN_1_OUT        = 'ff89ff'
    ORIGIN_1_IN         = 'ff90ff'


def data2np(data_file: str) -> np.ndarray:
    """
    Convert data file to numpy array.
    """
    with open(data_file, 'r') as f:
        data = f.buffer.read()
    print(len(data))
    grid = np.frombuffer(data, dtype=np.uint8).reshape((int(np.sqrt(len(data) / 3)), int(np.sqrt(len(data) / 3)), 3))
    grid_hex = np.array([[''.join(['%02x' % x for x in y]) for y in z] for z in grid])

    return grid_hex

def xcf2np(xcf_file: str, with_alpha = False) -> dict:
    project = GimpDocument(xcf_file)

    name_id = {project[i].name: i for i in range(len(project.layers))}

    w = project.width
    h = project.height
    data = {}
    for i in range(len(name_id)):
        grid = np.array(project[i].image.getdata())
        # change elements of grid st when grid[3] == 0 -> grid = [0,0,0,0]
        grid = np.array([np.array([0,0,0,0]) if x[3] == 0 else x for x in grid])
        alpha = grid[:, 3]
        grid = grid[:, :3].reshape((w, h, 3))
        grid1d = np.array([[''.join(['%02x' % x for x in y]) for y in z] for z in grid])
        if with_alpha:
            data[project[i].name] = (grid1d, alpha.reshape((w, h)))
        else:
            data[project[i].name] = grid1d
    
    return data

import pandas as pd
def get_traj(trjs: dict):
    ret = {}
    for trj_name in trjs:
        traj = []
        trj = trjs[trj_name]
        for x in range(trj.shape[0]):
            for y in range(trj.shape[1]):
                if trj[x][y] != BGColor.EMPTY.value:
                    traj.append((x, y, trj[x][y]))
        traj = pd.DataFrame(traj, columns=['x', 'y', 'traj'])
        traj['traj'] = traj['traj'].astype('category')
        origin = traj[traj['traj'].isin([o.value for o in OrColor])].iloc[0]
        traj = traj[~traj['traj'].isin([o.value for o in OrColor])].copy()
        traj[traffic.agent.Intent.LEFT] = traj['traj'].str[0] == 'f'
        traj[traffic.agent.Intent.STRAIGHT] = traj['traj'].str[2] == 'f'
        traj[traffic.agent.Intent.RIGHT] = traj['traj'].str[4] == 'f'
        del traj['traj']

        origin_type = OrColor(origin['traj'])

        ret[origin_type] = {}
        for intent in [traffic.agent.Intent.LEFT, traffic.agent.Intent.STRAIGHT, traffic.agent.Intent.RIGHT]:
            ret[origin_type][intent] = []
            t = traj[traj[intent]]
            x, y = origin['x'], origin['y']
            origin_x, origin_y = x, y
            while t.shape[0] > 1:
                t = t[(t['x'] != x) | (t['y'] != y)]
                neighs = t[(t['x'].isin([x-1, x, x+1]))]
                neighs = neighs[(neighs['y'].isin([y-1, y, y+1]))]
                neighs = neighs[~((neighs['x'] == x) * (neighs['y'] == y))]
                neigh = neighs.iloc[0]
                x, y = neigh['x'], neigh['y']
                ret[origin_type][intent].append((x - origin_x, y - origin_y))
    return ret

def get_rules(rules: dict):
    ret = {}
    for rule_name in rules:
        rule = rules[rule_name]
        i_points = []
        origin = None
        colors = rule[0]
        alphas = rule[1]
        for x in range(len(colors)):
            for y in range(len(colors[0])):
                color = colors[x][y]
                alpha = alphas[x][y]
                if color != BGColor.EMPTY.value:
                    if alpha != 255:
                        origin = (x, y, color)
                    else:
                        i_points.append((x, y, color))
        i_points = pd.DataFrame(i_points, columns=['x', 'y', 'rule'])
        i_points['rule'] = i_points['rule'].astype('category')
        give_left = i_points['rule'].str[0] == 'f'
        give_straight = i_points['rule'].str[2] == 'f'
        give_right = i_points['rule'].str[4] == 'f'
        i_points['give_left'] = i_points['rule'].str[1].apply(int, base=16) * give_left
        i_points['give_straight'] = i_points['rule'].str[3].apply(int, base=16) * give_straight
        i_points['give_right'] = i_points['rule'].str[5].apply(int, base=16) * give_right
        i_points['x'] = i_points['x'] - origin[0]
        i_points['y'] = i_points['y'] - origin[1]
        ret[StColor(origin[2])] = i_points
    return ret

def get_dlocks(dlocks: dict):
    ret = {}
    for dlock_name in dlocks:
        dlock = dlocks[dlock_name]
        d_points = []
        origin = None
        origin_xy = None
        for x in range(len(dlock)):
            for y in range(len(dlock[0])):
                col = dlock[x][y]
                if col == BGColor.EMPTY.value:
                    continue
                if col in [s.value for s in StColor]:
                    origin = StColor(col)
                    origin_xy = (x, y)
                    continue
                d_points += [(x, y)]
        print(origin_xy)
        ret[origin] = pd.DataFrame(d_points)
        ret[origin].columns = ['x', 'y']
        ret[origin]['x'] = ret[origin]['x'] - origin_xy[0]
        ret[origin]['y'] = ret[origin]['y'] - origin_xy[1]
    return ret

# send an int which encodes the rule (0-f) and the intent the found car (relative to me)
# returns true if it is not on my way
def doYouKnowTheWay(rule: int, relative_intent: RelativeDirection) -> bool:
    return rule & (1 << relative_intent.value) == 0

def doINeedToGiveTheDuckingWay(rule: int, relative_real_direction: tuple) -> bool:
    U = 7
    UR = 6
    R = 5
    DR = 4
    D = 3
    DL = 2
    L = 1
    UL = 0
    if relative_real_direction == (-1, 0):
        return rule & (1 << U) != 0
    elif relative_real_direction == (-1, 1):
        return rule & (1 << UR) != 0
    elif relative_real_direction == (0, 1):
        return rule & (1 << R) != 0
    elif relative_real_direction == (1, 1):
        return rule & (1 << DR) != 0
    elif relative_real_direction == (1, 0):
        return rule & (1 << D) != 0
    elif relative_real_direction == (1, -1):
        return rule & (1 << DL) != 0
    elif relative_real_direction == (0, -1):
        return rule & (1 << L) != 0
    elif relative_real_direction == (-1, -1):
        return rule & (1 << UL) != 0
        
