import traffic
import numpy as np

def hsl2rgb(h, s, l):
    h = h / 360
    s = s / 100
    l = l / 100
    if s == 0:
        r = g = b = l
    else:
        def hue2rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue2rgb(p, q, h + 1/3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1/3)
    return ''.join(['%02x' % int(x * 255) for x in [r, g, b]])

def randomRGB():
    val = hsl2rgb(np.random.randint(0, 360), 100, 80)
    return val

# def randomRGB():
#     val = f"{''.join(['%02x' % x for x in np.random.randint(0, 255, 3)])}"
#     return val

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
            "Filled": "true",
            "Layer": -1,
            "x": cell.pos[0],
            "y": cell.pos[1],
            "Color": f"#{cell.type.value}",
        }
        if cell.type == traffic.BGColor.ROAD:
            # return
            ret['Layer'] = -5
        return ret
    elif type(cell) in [traffic.Car, traffic.agent.MaxVerstappen]:
        # print(cell.intent, cell.intentD)
        if cell.intent != traffic.agent.Intent.NONE:
            return {
                "Shape": "arrowHead",
                "Filled": "false",
                "Layer": 20,
                "x": cell.pos[0],
                "y": cell.pos[1],
                "scale": 1,
                'heading_x': cell.intentD[0],
                'heading_y': cell.intentD[1],
                "Color": f"#{cell.color}",
                "ID": cell.id,
                "POS": (int(cell.pos[0]), int(cell.pos[1]))
            }
        else:
            return {
                "Shape": "circle",
                "Filled": "true",
                "Layer": 20,
                "x": cell.pos[0],
                "y": cell.pos[1],
                "r": 1.5,
                "Color": f"#{cell.color}",
                "ID": cell.id,
                "POS": (int(cell.pos[0]), int(cell.pos[1]))
            }
    elif type(cell) == traffic.TrafficLightController:
        return {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "true",
            "x": cell.pos[0],
            "y": cell.pos[1],
            "Layer": -1,
            "Color": f"#00ffff",
        }
    
    elif type(cell) == traffic.TrafficLight:
        return {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "true",
            "x": cell.pos[0],
            "y": cell.pos[1],
            "Layer": 10,
            "Color": f"#{cell.type.value}",
        }
    elif type(cell) == traffic.InfoAgent:
        d = {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": "true",
            "Layer": 20,
            "Color": "#ff0000",
        }
        if len(cell.model.datacollector.model_vars['Spawned']) > 0:
            mv = cell.model.datacollector.model_vars
            for k in mv:
                d[k] = mv[k][-1]
        return d
    elif type(cell) == traffic.TombstoneAgent:
        return {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 20,
            "x": cell.pos[0],
            "y": cell.pos[1],
            "r": 1,
            "Color": f"#{cell.type.value}",
            "Deaths": cell.deaths
        }