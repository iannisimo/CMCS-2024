import traffic
import numpy as np

def randomRGB():
    val = f"{''.join(['%02x' % x for x in np.random.randint(0, 255, 3)])}"
    return val

def portrayCell(cell):
    """
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the cell in its current state.
    :param cell:  the cell in the simulation
    :return: the portrayal dictionary.
    """
    if cell is None:
        raise AssertionError
    if type(cell) == traffic.StaticAgent or type(cell) == traffic.SpawnAgent or type(cell) == traffic.SelfDestructAgent:
        ret = {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "false",
            "Layer": 10,
            "x": cell.pos[0],
            "y": cell.pos[1],
            "Color": f"#{cell.type.value}",
        }
        if cell.type == traffic.CellColor.ROAD:
            ret['Layer'] = 0
        elif cell.type == traffic.CellColor.TRAJECTORY:
            ret['Layer'] = 5
        return ret
    return {
        "Shape": "arrowHead",
        "Filled": "false",
        "Layer": 20,
        "x": cell.pos[0],
        "y": cell.pos[1],
        "scale": 1.5,
        'heading_x': cell.intentD[0],
        'heading_y': cell.intentD[1],
        "Color": f"#{cell.color}",
    }