import numpy as np
from enum import Enum
import traffic

class CellColor(Enum):
    TRAJECTORY = 'e5e5e5'
    ROAD = 'ffffff'
    WALL = '000000'
    STOP = 'ff8800'
    STRAIGHT = 'ff0078'
    RIGHT = '8500ff'
    LEFT = 'ed00ff'
    SPAWN = '0000ff'
    DESPAWN = 'ff00ff'
    CAR = '0'


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