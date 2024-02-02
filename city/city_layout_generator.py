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
def random_matching_tile(north, south, east, west, seed):
    # Generate a random tile
    tile = ""
    for i in range(4):

        tile += str(random.randint(0, 2))

    #print(north, south, east, west)

    # Match the tile with the adjacent ones, if one or more are None, match with a random tile
    if north is not None:
        tile = tile[:0] + north[1] + tile[1:]
    else:
        tile = tile[:0] + str(random.randint(0, 2)) + tile[1:]
    if south is not None:
        tile = tile[:1] + south[0] + tile[2:]
    else:
        tile = tile[:1] + str(random.randint(0, 2)) + tile[2:]
    if east is not None:
        tile = tile[:2] + east[3] + tile[3:]
    else:
        tile = tile[:2] + str(random.randint(0, 2)) + tile[3:]
    if west is not None:
        tile = tile[:3] + west[2] + tile[4:]
    else:
        tile = tile[:3] + str(random.randint(0, 2)) + tile[4:]
    
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

def generate_city(city, tiles: dict):

    tiled = {}

    tile_w = list(tiles.values())[0]['BG'].shape[0]
    tile_h = list(tiles.values())[0]['BG'].shape[1]
    city_with_tiles_w = city.shape[0] * tile_w
    city_with_tiles_h = city.shape[1] * tile_h

    for layer in list(list(tiles.values())[0].keys()):
        if 'RULE' in layer:
            continue
        layer_tiles = np.empty((city_with_tiles_w, city_with_tiles_h), dtype=object)
        for i in range(city_with_tiles_w):
            for j in range(city_with_tiles_h):
                matching_tiles = [key for key in tiles.keys() if key[:4] == city[int(i/tile_w)][int(j/tile_h)]]
                layer_tiles[i][j] = tiles[random.choice(matching_tiles)][layer][i%tile_w][j%tile_h]
        tiled[layer] = layer_tiles
    
    # city_with_tiles = np.empty((city.shape[0]*tile_w, city.shape[1]*tile_h), dtype=object)

    # city_with_tiles_w = city_with_tiles.shape[0]
    # city_with_tiles_h = city_with_tiles.shape[1]

    # for i in range(city_with_tiles_w):
    #     for j in range(city_with_tiles_h):
    #         #match the cell with a random tile from "tiles" that matches the first 4 characters of the cell 
    #         matching_tiles = [key for key in tiles.keys() if key[:4] == city[int(i/tile_w)][int(j/tile_h)]]
    #         city_with_tiles[i][j] = tiles[random.choice(matching_tiles)][i%tile_w][j%tile_h]

            
    return tiled
    
