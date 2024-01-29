import mesa
import traffic

class Intersection(mesa.Model):

    def __init__(self, intersection_array):
        super().__init__()

        self.schedule = mesa.time.SimultaneousActivation(self)

        self.grid = mesa.space.MultiGrid(intersection_array.shape[0], intersection_array.shape[1], False)

        for x in range(intersection_array.shape[0]):
            for y in range(intersection_array.shape[1]):
                cell_val = intersection_array[x][y]
                if cell_val == traffic.CellColor.SPAWN.value:
                    spawn_agent = traffic.SpawnAgent((x,y), self)
                    self.grid.place_agent(spawn_agent, (x,y))
                    self.schedule.add(spawn_agent)
                else:
                    static_agent = traffic.StaticAgent((x,y), self, traffic.CellColor(cell_val))
                    self.grid.place_agent(static_agent, (x,y))
        
        self.running = True


    def step(self) -> None:
        self.schedule.step()