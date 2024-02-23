import mesa
from city import Pathfinder
import traffic
import numpy as np
import city

class Intersection(mesa.Model):

    def __init__(self, seed=None, w_tiles = 5, h_tiles = 5):
        super().__init__(seed=seed)

        exits = ['0001', '0010', '0100', '1000']
        for i in range(traffic.const.MAX_SEARCH):
            map = city.city_planner(w_tiles, h_tiles, self.random)
            c_layers = city.generate_city(map, traffic.const.TILES, self.random)
            self.city_exits = [(i, j) for i, _ in enumerate(map) for j, _ in enumerate(map[i]) if map[i][j] in exits]
            n_exits = len(self.city_exits)
            if n_exits < 2:
                break


        w = list(c_layers.values())[0].shape[0]
        h = list(c_layers.values())[0].shape[1]

        self.dc = traffic.collector(self)

        self.datacollector = mesa.DataCollector(model_reporters={
            "Crashed": lambda m: m.crashed,
            "Spawned": lambda m: m.spawned,
            "Despawned": lambda m: m.despawned,
            "Alive": lambda m: m.spawned - m.despawned,
            "Steps": lambda m: m.steps,
            # "Agents": lambda _: self.dc.collect_data() 
        })


        colors = [traffic.hsl2rgb(int(360 / n_exits * i), 100, 50) for i in range(n_exits)]
        self.random.shuffle(colors)
        self.exit_colors = {self.city_exits[i]: colors[i] for i in range(n_exits)}
        self.pathfinder = Pathfinder(map)

        self.schedule = mesa.time.RandomActivationByType(self)

        self.grid = mesa.space.MultiGrid(w, h, False)

        self.rules = traffic.const.RULES
        self.trjs = traffic.const.TRJS
        self.dlocks = traffic.const.DLOCKS

        self.already_spawned = False

        self.ids = 0

        self.crashed = 0
        self.spawned = 0
        self.despawned = 0

        self.steps = 0

        for i in range(3):
            for j in range(3):
                self.grid.place_agent(traffic.InfoAgent(0, self), (i, j))

        for x in range(w):
            for y in range(h):
                for k in c_layers.keys():
                    cell_val = c_layers[k][x][y]
                    if cell_val == traffic.BGColor.EMPTY.value:
                        continue
                    elif cell_val == traffic.BGColor.ROAD.value:
                        static = traffic.StaticAgent((x,y), self, traffic.BGColor.ROAD)
                        self.grid.place_agent(static, (x,y))
                    elif cell_val == traffic.InColor.DESPAWN.value:
                        static = traffic.StaticAgent((x,y), self, traffic.InColor.DESPAWN)
                        static.despawnColor = self.get_ecolor((int(x / 17), int(y / 17)))
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
                    
                    elif cell_val == traffic.InColor.TRAFFIC_LIGHT.value:
                        tlController = traffic.TrafficLightController((x,y), self)
                        self.grid.place_agent(tlController, (x,y))
                        self.schedule.add(tlController)
                    
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
        return self.random.choice([e for e in self.city_exits if e != pos])
    
    def get_path(self, pos, exit = None):
        # 17: tile_w/h
        pos = (int(pos[0] / 17), int(pos[1] / 17))
        if not exit:
            exit = self.pick_exit(pos)
        return self.pathfinder.get_path(pos, exit, self.random), exit
    
    def get_ecolor(self, pos):
        return self.exit_colors[pos]

    def step(self) -> None:
        self.datacollector.collect(self)
        self.schedule.step()
        self.steps += 1

    