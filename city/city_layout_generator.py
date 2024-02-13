# Functions used to generate a layout for the city


# Various types of traffic intersections to fill the city
#   4-way intersection
#   roundabout
#   T-intersection
#   dead end
#   straight
#   curve

# strings NSEW to identify matching lanes
# 0 = no connection
# 1 = connection
# 2 = connection with 2 lanes


import numpy as np
import random
import numpy as np
import matplotlib.pyplot as plt

def plot_city(city):
    # Get the city dimensions
    city_height, city_width = city.shape

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Set the axis limits
    ax.set_xlim(0, city_width)
    ax.set_ylim(0, city_height)

    # Iterate over each cell in the city
    for i in range(city_height):
        for j in range(city_width):
            # Get the connections of the current cell
            connections = city[i][j]

            # Calculate the coordinates of the cell
            x = j
            y = city_height - i - 1

            # Plot the cell as a rectangle
            rect = plt.Rectangle((x, y), 1, 1, facecolor='white', edgecolor='white')
            ax.add_patch(rect)

            # Plot the connections as lines
            if connections[0] == '1':
                ax.plot([x + 0.5, x + 0.5], [y + 0.5, y + 1], color='black')
            if connections[2] == '1':
                ax.plot([x + 0.5, x + 1], [y + 0.5, y + 0.5], color='black')
            if connections[1] == '1':
                ax.plot([x + 0.5, x + 0.5], [y + 0.5, y], color='black')
            if connections[3] == '1':
                ax.plot([x + 0.5, x], [y + 0.5, y + 0.5], color='black')

            # Plot the connections as lines
            if connections[0] == '2':
                ax.plot([x + 0.5, x + 0.5], [y + 0.5, y + 1], color= 'red', linewidth=3)
            if connections[2] == '2':
                ax.plot([x + 0.5, x + 1], [y + 0.5, y + 0.5], color= 'red', linewidth=3)
            if connections[1] == '2':
                ax.plot([x + 0.5, x + 0.5], [y + 0.5, y], color= 'red', linewidth=3)
            if connections[3] == '2':
                ax.plot([x + 0.5, x], [y + 0.5, y + 0.5], color= 'red', linewidth=3)

            # Plot the connections as a blue square
            if connections[0] == 'w':
                rect = plt.Rectangle((x + 0.25, y + 0.25), 0.5, 0.5, facecolor='blue', edgecolor='blue')
                ax.add_patch(rect)
            if connections[2] == 'w':
                rect = plt.Rectangle((x + 0.5, y + 0.25), 0.5, 0.5, facecolor='blue', edgecolor='blue')
                ax.add_patch(rect)
            if connections[1] == 'w':
                rect = plt.Rectangle((x + 0.25, y), 0.5, 0.5, facecolor='blue', edgecolor='blue')
                ax.add_patch(rect)
            if connections[3] == 'w':
                rect = plt.Rectangle((x, y + 0.25), 0.5, 0.5, facecolor='blue', edgecolor='blue')
                ax.add_patch(rect)

    # Set the aspect ratio to equal
    ax.set_aspect('equal')

    # Show the plot
    plt.show()

#TODO: add seed to the random values and different probabilities for the number of lanes
def random_matching_tile(north, south, east, west, seed, max_lanes = 1):
    # Generate a random tile
    tile = ""
    for i in range(4):

        tile += str(random.randint(0, max_lanes))

    #print(north, south, east, west)

    # Match the tile with the adjacent ones, if one or more are None, match with a random tile
    if north is not None:
        tile = tile[:0] + north[1] + tile[1:]
    else:
        tile = tile[:0] + str(random.randint(0, max_lanes)) + tile[1:]
    if south is not None:
        tile = tile[:1] + south[0] + tile[2:]
    else:
        tile = tile[:1] + str(random.randint(0, max_lanes)) + tile[2:]
    if east is not None:
        tile = tile[:2] + east[3] + tile[3:]
    else:
        tile = tile[:2] + str(random.randint(0, max_lanes)) + tile[3:]
    if west is not None:
        tile = tile[:3] + west[2] + tile[4:]
    else:
        tile = tile[:3] + str(random.randint(0, max_lanes)) + tile[4:]
    
    return tile

def depth_first_visit(city, i, j, visited):
    # Check if the current cell is within the city boundaries and not visited
    if i < 0 or i >= len(city) or j < 0 or j >= len(city[0]) or visited[i][j]:
        return
    # Mark the current cell as visited
    visited[i][j] = True
    # Visit the neighboring cells in a depth-first manner
    if city[i][j][0] == '1' or city[i][j][0] == '2':
        depth_first_visit(city, i-1, j, visited)
    if city[i][j][2] == '1' or city[i][j][2] == '2':
        depth_first_visit(city, i, j+1, visited)
    if city[i][j][1] == '1' or city[i][j][1] == '2':
        depth_first_visit(city, i+1, j, visited)
    if city[i][j][3] == '1' or city[i][j][3] == '2':
        depth_first_visit(city, i, j-1, visited)

def city_planner(width, depth, seed):

    if seed == 0:
        #generate a city of 4 way intersections
        city = np.full((depth, width), "1111", dtype=object)
        #plot_city(city)

        return city


    city = np.empty((width, depth), dtype=object)
    for i in range(depth):
        for j in range(width):
            city[i][j] = None

    #fill the four corners 
    city[0][0] = random_matching_tile("0000", "1000","0001","0000",seed)
    city[0][width-1] = random_matching_tile("0000", "1000","0000","0010",seed)
    city[depth-1][0] = random_matching_tile("0100", "0000","0001","0000",seed)
    city[depth-1][width-1] = random_matching_tile("0100", "0000","0000","0010",seed)

    #fill the north and south borders with random random matching tiles
    for i in range(1,width-1):
        city[0][i] = random_matching_tile("0000", None, "1111", "1111",seed)
        city[depth-1][i] = random_matching_tile(None, "0000", "1111", "1111",seed)

    #fill the east and west borders with random random matching tiles
    for i in range(1,depth-1):
        city[i][0] = random_matching_tile("1111", "1111", None, "0000",seed)
        city[i][width-1] = random_matching_tile("1111", "1111", "0000", None,seed)

    #fill the rest of the city
    for i in range(1,depth-1):
        for j in range(1,width-1):
            city[i][j] = random_matching_tile(city[i-1][j], city[i+1][j], city[i][j+1], city[i][j-1],seed)

    # Create a visited matrix to keep track of visited cells
    visited = np.zeros((depth, width), dtype=bool)

    depth_first_visit(city, 0, 0, visited)

    # Set the cells not visited to "0000"
    for i in range(depth):
        for j in range(width):
            if not visited[i][j]:
                city[i][j] = "0000"

    #print(city)

    #plot_city(city)
                
    return city

def nsew2nesw(nsew):
    return nsew[0] + nsew[2] + nsew[1] + nsew[3]

def nesw2nsew(nesw):
    return nesw[0] + nesw[2] + nesw[1] + nesw[3]

def augment_tiles(tiles: dict):
    ret = tiles.copy()
    for key in list(tiles.keys()):
        val = tiles[key]
        nsew = key[:4]
        type = key[4]
        if nsew == '1111':
            continue
        nesw = nsew2nesw(nsew)
        for i in range(1, 4):
            nesw = nesw[-1] + nesw[:-1]
            nsew = nesw2nsew(nesw)
            ret[nsew + type] = {layer_key: np.rot90(val[layer_key], -i) for layer_key in val}
    return ret

def generate_city(city, tiles: dict):

    tiles = augment_tiles(tiles)

    print(tiles.keys())

    tiled = {}

    tile_w = list(tiles.values())[0]['BG'].shape[0]
    tile_h = list(tiles.values())[0]['BG'].shape[1]
    keys = list(tiles.values())[0]
    city_with_tiles_w = city.shape[0] * tile_w
    city_with_tiles_h = city.shape[1] * tile_h


    tiles['0000a'] = {layer_key: np.full((tile_w, tile_h), '000000') for layer_key in keys}

    full_city = {key: np.full((city_with_tiles_w, city_with_tiles_h), '000000') for key in keys}
    for i in range(city.shape[0]):
        for j in range(city.shape[1]):
            city_tile = city[i, j]
            print(city_tile)
            matching_tiles = [key for key in tiles.keys() if key[:4] == city_tile]
            choosen_tile_key = random.choice(matching_tiles)
            choosen_tile = tiles[choosen_tile_key]
            for key in keys:
                base_i, base_j = i*tile_w, j*tile_h
                full_city[key][base_i:base_i+tile_w, base_j:base_j+tile_h] = choosen_tile[key]
    return full_city
 

class Pathfinder():


    def generate_adjacency_map(self, city):
        adjacency_map = {}
        for i in range(len(city)):
            for j in range(len(city[0])):
                if city[i][j] != '0000':
                    neighbors = []
                    if city[i][j][0] == '1':  # Check north connection
                        if i > 0 and city[i-1][j][1] == '1':  # Check south connection of the neighbor
                            neighbors.append((i-1, j))
                    
                    if city[i][j][1] == '1':
                        if i < len(city)-1 and city[i+1][j][0] == '1':
                            neighbors.append((i+1, j))

                    if city[i][j][2] == '1':
                        if j < len(city[0])-1 and city[i][j+1][3] == '1':
                            neighbors.append((i, j+1))

                    if city[i][j][3] == '1':
                        if j > 0 and city[i][j-1][2] == '1':
                            neighbors.append((i, j-1))

                    #print(i, j, neighbors)
                    adjacency_map[(i, j)] = neighbors
                    
        return adjacency_map

    def heuristic(self, node, target):
        # Calculate the Manhattan distance between two nodes
        return abs(node[0] - target[0]) + abs(node[1] - target[1])
    
    def random_min(self, lst, key=None):
        min_items = [item for item in lst if item == min(lst, key=key)]
        return random.choice(min_items)

    def a_star(self, adjacency_map, start, target):
        # Create empty sets for open and closed nodes
        open_set = set()
        closed_set = set()
        # Create a dictionary to store the parent of each node
        parent = {}
        # Create a dictionary to store the cost from start to each node
        g_score = {node: float('inf') for node in adjacency_map}
        g_score[start] = 0
        # Create a dictionary to store the total cost of each node
        f_score = {node: float('inf') for node in adjacency_map}
        f_score[start] = self.heuristic(start, target)

        #check if the start and target are in the adjacency map
        if start not in adjacency_map or target not in adjacency_map:
            return []
        
        
        # Add the start node to the open set
        open_set.add(start)
        while open_set:
            # Find the node with the lowest f_score
            current = self.random_min(open_set, key=lambda node: f_score[node])
            # If the current node is the target, reconstruct the path and return it
            if current == target:
                path = []
                while current in parent:
                    path.append(current)
                    current = parent[current]
                path.append(start)
                path.reverse()
                return path
            # Remove the current node from the open set and add it to the closed set
            open_set.remove(current)
            closed_set.add(current)
            # Explore the neighbors of the current node
            for neighbor in adjacency_map[current]:
                # Calculate the tentative g_score for the neighbor
                tentative_g_score = g_score[current] + 1
                # If the neighbor is already in the closed set and the tentative g_score is higher, skip it
                if neighbor in closed_set and tentative_g_score >= g_score[neighbor]:
                    continue
                # If the neighbor is not in the open set or the tentative g_score is lower, update the values
                if neighbor not in open_set or tentative_g_score < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, target)
                    # Add the neighbor to the open set if it's not already there
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        # If the open set is empty and the target has not been found, return an empty path
        return []

    def __init__(self, city_layout):
        self.adj_map = self.generate_adjacency_map(city_layout)

    def get_path(self, from_where, to_where):
        # print(f'Choosen exit: {to_where} from {from_where}')
        path = self.a_star(self.adj_map, from_where, to_where)
        relative_path = [(path[i-1][0] - path[i][0], path[i][1] - path[i-1][1]) for i in range(1, len(path))]
        relative_path += [relative_path[-1]]
        relative_path = [relative_path[0]] + relative_path
        return relative_path