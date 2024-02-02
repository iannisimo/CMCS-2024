import mesa
import pandas as pd
import traffic
from enum import Enum

TILES = [0]

def careDir(to_care: traffic.agent.Intent, val: str) -> bool:
    if to_care == traffic.agent.Intent.LEFT:
        if val in ['1', '4', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
            return True
    elif to_care == traffic.agent.Intent.STRAIGHT:
        if val in['2', '4' '5','7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
            return True
    elif to_care == traffic.agent.Intent.RIGHT:
        if val in ['3', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']:
            return True
    return False

class Rules(Enum):
    GIVE_LEFT = 'ff0000'
    GIVE_STRAIGHT = '00ff00'
    GIVE_RIGHT = '0000ff'
    GIVE_LEFT_STRAIGHT = 'ffff00'
    GIVE_LEFT_RIGHT = 'ff00ff'
    GIVE_STRAIGHT_RIGHT = '00ffff'
    GIVE_ALL = 'ffffff'

class Stops(Enum):
    STOP_4_ISECTION = 'ff8800'

class Origins(Enum):
    ORIGIN_4_ISECTION = '010101'

class Intersection(mesa.Model):

    def __init__(self, layers: dict, rules: dict, trjs: dict):
        super().__init__()


        self.intersection_rules = {}
        for layer in rules:
            rule_layer = rules[layer]
            rule = []
            for x in range(rule_layer.shape[0]):
                for y in range(rule_layer.shape[1]):
                    if rule_layer[x][y] != traffic.CellColor.EMPTY.value:
                        rule.append((x, y, rule_layer[x][y]))
            rule = pd.DataFrame(rule, columns=['x', 'y', 'rule'])
            rule['rule'] = rule['rule'].astype('category')
            origin = rule[rule['rule'].isin([r.value for r in Stops])].iloc[0]
            rule = rule[~rule['rule'].isin([r.value for r in Stops])]
            rule['x'] = rule['x'] - origin['x']
            rule['y'] = rule['y'] - origin['y']
            rule['give_left'] = rule['rule'].str[0] == 'f'
            rule['give_straight'] = rule['rule'].str[2] == 'f'
            rule['give_right'] = rule['rule'].str[4] == 'f'
            rule['blinker_left'] = rule['rule'].str[1]
            rule['blinker_straight'] = rule['rule'].str[3]
            rule['blinker_right'] = rule['rule'].str[5]
            del rule['rule']
            self.intersection_rules[origin['rule']] = rule


        self.datacollector = mesa.datacollection.DataCollector()

        
        # remove all layers that are rules
        layers = {k: v for k, v in layers.items() if not k.startswith('RULE')}

        self.schedule = mesa.time.RandomActivationByType(self)

        w = list(layers.values())[0].shape[0]
        h = list(layers.values())[0].shape[1]

        self.interest_points = {}
        for t in TILES:
            ipt = []
            for x in range(w):
                for y in range(h):
                    if layers['IN'][x][y] != traffic.CellColor.EMPTY.value:
                        ipt.append((traffic.CellColor(layers['IN'][x][y]), x, y))
            self.interest_points[t] = pd.DataFrame(ipt, columns=['type', 'x', 'y'])
            self.interest_points[t]['type'] = self.interest_points[t]['type'].astype('category')
            self.interest_points[t].sort_values(by=['type'], inplace=True)
            self.interest_points[t].set_index(['type'], inplace=True)

        prop_layers = {k: mesa.space.PropertyLayer(k, layers[k].shape[0], layers[k].shape[1], default_value=traffic.CellColor.EMPTY, dtype=traffic.CellColor) for k in layers.keys()}
        for k in prop_layers.keys():
            for x in range(layers[k].shape[0]):
                for y in range(layers[k].shape[1]):
                    prop_layers[k].set_cell((x,y), traffic.CellColor(layers[k][x][y]))

        self.grid = mesa.space.MultiGrid(w, h, False)

        for x in range(w):
            for y in range(h):
                for k in prop_layers.keys():
                    cell_val = prop_layers[k].data[x][y]
                    if cell_val == traffic.CellColor.EMPTY:
                        continue
                    elif cell_val == traffic.CellColor.SPAWN:
                        spawn_agent = traffic.SpawnAgent((x,y), self)
                        self.grid.place_agent(spawn_agent, (x,y))
                        self.schedule.add(spawn_agent)
                    else:
                        static_agent = traffic.StaticAgent((x,y), self, traffic.CellColor(cell_val))
                        self.grid.place_agent(static_agent, (x,y))
        
        self.running = True


    def step(self) -> None:
        self.schedule.step()