# %%
import mesa
import traffic
import city

# a = traffic.data2np('GRIDS/intersection.data')
rules = traffic.utils.xcf2np('GRIDS/rules17.xcf', with_alpha=True)
trjs = traffic.utils.get_traj(traffic.utils.xcf2np('GRIDS/trj17.xcf'))
layers = traffic.utils.xcf2np('GRIDS/4WayI.xcf')

traffic.utils.get_rules(rules)
exit(0)

map = city.city_planner(3, 3, 0)
tiles = {
    '1111i': layers
}

tiled_layers = city.generate_city(map, tiles)



w = list(tiled_layers.values())[0].shape[0]
h = list(tiled_layers.values())[0].shape[1]

SCALE_MULTIPLE = 5

canvas_element = mesa.visualization.CanvasGrid(traffic.portrayCell, w, h, w*SCALE_MULTIPLE, h*SCALE_MULTIPLE)

server = mesa.visualization.ModularServer(traffic.Intersection, [canvas_element], "Intersection", {'layers': tiled_layers, 'rules': rules})
server.launch(open_browser=False)


# %%

# res = mesa.batch_run(traffic.Intersection, {'layers': [layers], 'rules': [rules]}, 1, 1, -1, 1000, True)
# print(res)

# %%
