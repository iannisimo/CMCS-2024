#collect the velocity of each agent in the grid at the time of despawn and store it in a list

import traffic


class collector():
    
    #initialize the dictionary
    data = {}


    def __init__(self, model):
        self.model = model

        
    def collect_data(self):
        for agent in self.model.agents:
            if not agent.pos: continue
            if type(agent) == traffic.Car:
                
                if agent.id not in self.data:
                    self.data[agent.id] = {
                        "speed": [],
                        "acceleration": [],
                        "position": [],
                        "cell_travelled": 0,
                        "alive_time": 0
                    }
                else:
                    self.data[agent.id]["speed"].append(round(agent.speed, 2))
                    self.data[agent.id]["acceleration"].append(agent.state.value)
                    self.data[agent.id]["position"].append(traffic.tupleInt(agent.pos))
                    self.data[agent.id]["cell_travelled"] = agent.cell_travelled
                    self.data[agent.id]["alive_time"] = agent.alive_time    
        return self.data
    



