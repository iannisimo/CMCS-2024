import traffic
import numpy as np

def portrayCell(cell):
    """
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the cell in its current state.
    :param cell:  the cell in the simulation
    :return: the portrayal dictionary.
    """
    if cell is None:
        raise AssertionError
    if type(cell) == traffic.StaticAgent or type(cell) == traffic.SpawnAgent:
        return {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "false",
            "Layer": 0,
            "x": cell.pos[0],
            "y": cell.pos[1],
            "Color": f"#{cell.type.value}",
        }
    return {
        "Shape": "arrowHead",
        "Filled": "false",
        "Layer": 1,
        "x": cell.pos[0],
        "y": cell.pos[1],
        "scale": 1.5,
        'heading_x': cell.intentD[0],
        'heading_y': cell.intentD[1],
        "Color": f"Red",
    }
