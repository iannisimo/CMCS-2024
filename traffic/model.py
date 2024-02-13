import mesa
from city import Pathfinder
import pandas as pd
import traffic
from enum import Enum
import numpy as np

class Intersection(mesa.Model):

    @staticmethod
    def agents_stats(self):
        return {
            "speed": a.speed if type(a) == traffic.Car else -1
        for a in self.agents}

    def __init__(self, layers: dict, rules: dict, trjs: dict, dlocks: dict, city_layout: np.array):
        super().__init__()
        w = list(layers.values())[0].shape[0]
        h = list(layers.values())[0].shape[1]

        self.datacollector = mesa.DataCollector(model_reporters={
            "Crashed": lambda m: m.crashed,
            "Spawned": lambda m: m.spawned,
            "Despawned": lambda m: m.despawned,
            "Alive": lambda m: m.spawned - m.despawned,
            "Agents": self.agents_stats
        })

        exits = ['0001', '0010', '0100', '1000']
        self.city_exits = [(i, j) for i, _ in enumerate(city_layout) for j, _ in enumerate(city_layout[i]) if city_layout[i][j] in exits]
        self.pathfinder = Pathfinder(city_layout)

        self.schedule = mesa.time.RandomActivationByType(self)

        self.grid = mesa.space.MultiGrid(w, h, False)

        self.rules = rules
        self.trjs = trjs
        self.dlocks = dlocks

        self.already_spawned = False

        self.ids = 0

        self.crashed = 0
        self.spawned = 0
        self.despawned = 0


        for i in range(3):
            for j in range(3):
                self.grid.place_agent(traffic.InfoAgent(0, self), (i, j))

        for x in range(w):
            for y in range(h):
                for k in layers.keys():
                    cell_val = layers[k][x][y]
                    if cell_val == traffic.BGColor.EMPTY.value:
                        continue
                    elif cell_val == traffic.BGColor.ROAD.value:
                        static = traffic.StaticAgent((x,y), self, traffic.BGColor.ROAD)
                        self.grid.place_agent(static, (x,y))
                    elif cell_val == traffic.InColor.DESPAWN.value:
                        static = traffic.StaticAgent((x,y), self, traffic.InColor.DESPAWN)
                        self.grid.place_agent(static, (x,y))
                    elif cell_val == traffic.InColor.SPAWN.value:
                        spawn = traffic.SpawnAgent((x,y), self)
                        self.grid.place_agent(spawn, (x,y))
                        self.schedule.add(spawn)
                    elif cell_val in [o.value for o in traffic.OrColor]:
                        static = traffic.StaticAgent((x,y), self, traffic.OrColor(cell_val))
                        self.grid.place_agent(static, (x,y))
                    elif cell_val in [s.value for s in traffic.StColor]:
                        static = traffic.StaticAgent((x,y), self, traffic.StColor(cell_val))
                        self.grid.place_agent(static, (x,y))
                        # static_car = traffic.Car((x,y), self)
                        # self.grid.place_agent(static_car, (x,y))
                    
                    elif cell_val == traffic.InColor.TRAFFIC_LIGHT.value:
                        tlController = traffic.TrafficLightController((x,y), self)
                        self.grid.place_agent(tlController, (x,y))
                        self.schedule.add(tlController)
                    

                # for k in prop_layers.keys():
                #     cell_val = prop_layers[k].data[x][y]
                #     if cell_val == traffic.CellColor.EMPTY:
                #         continue
                #     elif cell_val == traffic.CellColor.SPAWN:
                #         spawn_agent = traffic.SpawnAgent((x,y), self)
                #         self.grid.place_agent(spawn_agent, (x,y))
                #         self.schedule.add(spawn_agent)
                #     else:
                #         if cell_val in [
                #             traffic.CellColor.EMPTY,
                #             traffic.CellColor.WALL,
                #             traffic.CellColor.ROAD
                #             ]:
                #             continue
                #         static_agent = traffic.StaticAgent((x,y), self, traffic.CellColor(cell_val))
                #         self.grid.place_agent(static_agent, (x,y))
        
        self.running = True

    def next_uid(self):
        self.ids += 1
        return self.ids
    
    def get_agent(self, id):
        a = [a for a in self.agents if 'id' in a.__dict__ and a.id == id]
        if len(a) > 0:
            return a[0]
        return None
    
    def pick_exit(self, pos):
        from random import choice
        return choice([e for e in self.city_exits if e != pos])
    
    def get_path(self, pos, exit = None):
        # 17: tile_w/h
        pos = (int(pos[0] / 17), int(pos[1] / 17))
        if not exit:
            exit = self.pick_exit(pos)
        return self.pathfinder.get_path(pos, exit), exit

    def step(self) -> None:
        self.datacollector.collect(self)
        self.schedule.step()

    