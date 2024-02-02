import numpy as np
from enum import Enum
import traffic
import numpy as np
from gimpformats.gimpXcfDocument import GimpDocument

class CellColor(Enum):
    TRAJECTORY = '928b7d'
    ROAD = 'ffffff'
    WALL = '010101'
    STOP = 'ff8800'
    STRAIGHT = 'ff0078'
    RIGHT = '8500ff'
    LEFT = 'ed00ff'
    SPAWN = '0000ff'
    DESPAWN = 'ff00ff'
    CAR = 'dd0000'
    EMPTY = '000000'
    SDA = '444477'

class CellType(Enum):
    TRAJECTORY = 0
    ROAD = 1
    WALL = 2
    STOP = 3
    STRAIGHT = 4
    RIGHT = 5
    LEFT = 6
    SPAWN = 7
    DESPAWN = 8
    CAR = 9
    EMPTY = 10
    SDA = 11

CellColor2CellType = {
    '928b7d': CellType.TRAJECTORY,
    'ffffff': CellType.ROAD,
    '010101': CellType.WALL,
    'ff8800': CellType.STOP, # 4-way intersection stop
    'ff8811': CellType.STOP, # 3-way intersection stop
    'ff8822': CellType.STOP, # 3-way intersection give-way
    'ff8833': CellType.STOP, # Roundabout enter
    'ff0078': CellType.STRAIGHT,
    '8500ff': CellType.RIGHT,
    'ed00ff': CellType.LEFT,
    '0000ff': CellType.SPAWN,
    'ff00ff': CellType.DESPAWN,
    'dd0000': CellType.CAR,
    '000000': CellType.EMPTY,
    '444477': CellType.SDA
}


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

def xcf2np(xcf_file: str) -> dict:
    project = GimpDocument(xcf_file)

    name_id = {project[i].name: i for i in range(len(project.layers))}

    w = project.width
    h = project.height
    data = {}
    for i in range(len(name_id)):
        grid = np.array(project[i].image.getdata())
        # change elements of grid st when grid[3] == 0 -> grid = [0,0,0,0]
        grid = np.array([np.array([0,0,0,0]) if x[3] == 0 else x for x in grid])
        grid = grid[:, :3].reshape((w, h, 3))
        grid1d = np.array([[''.join(['%02x' % x for x in y]) for y in z] for z in grid])
        data[project[i].name] = grid1d
    
    return data

def get_neighhd(x, y):
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            yield x + i, y + j


import pandas as pd
def get_traj(trjs: dict):
    trajectoryes = {}
    for trj in trjs:
        traj = []
        for x in range(trj.shape[0]):
            for y in range(trj.shape[1]):
                if trj[x][y] != traffic.CellColor.EMPTY.value:
                    traj.append((x, y, trj[x][y]))
        traj = pd.DataFrame(traj, columns=['x', 'y', 'traj'])
        traj['traj'] = traj['traj'].astype('category')
        origin = traj[traj['traj'].isin([o.value for o in Origins])].iloc[0]
        trjs = traj[~traj['traj'].isin([o.value for o in Origins])]
        traj['x'] = traj['x'] - origin['x']
        traj['y'] = traj['y'] - origin['y']
        trjs[traffic.agent.Intent.LEFT] = trjs['traj'].str[0] == 'f'
        trjs[traffic.agent.Intent.STRAIGHT] = trjs['traj'].str[2] == 'f'
        trjs[traffic.agent.Intent.RIGHT] = trjs['traj'].str[4] == 'f'
        del trjs['traj']

        for intent in [traffic.agent.Intent.LEFT, traffic.agent.Intent.STRAIGHT, traffic.agent.Intent.RIGHT]:
            t = trjs[trjs[intent]]
            x, y = origin[x], origin[y]

