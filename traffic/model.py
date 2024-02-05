import mesa
import pandas as pd
import traffic
from enum import Enum

class Intersection(mesa.Model):

    def __init__(self, layers: dict, rules: dict, trjs: dict):
        super().__init__()
        w = list(layers.values())[0].shape[0]
        h = list(layers.values())[0].shape[1]

        self.datacollector = mesa.datacollection.DataCollector()

        self.schedule = mesa.time.RandomActivationByType(self)

        self.grid = mesa.space.MultiGrid(w, h, False)

        self.rules = rules
        self.trjs = trjs

        self.already_spawned = False


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


    def step(self) -> None:
        self.schedule.step()