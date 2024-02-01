# %%
import mesa
import traffic

# a = traffic.data2np('GRIDS/intersection.data')
rules = traffic.utils.xcf2np('GRIDS/rules.xcf')
layers = traffic.utils.xcf2np('GRIDS/intersection.xcf')

w = list(layers.values())[0].shape[0]
h = list(layers.values())[0].shape[1]

canvas_element = mesa.visualization.CanvasGrid(traffic.portrayCell, w, h, w*20, h*20)

server = mesa.visualization.ModularServer(traffic.Intersection, [canvas_element], "Intersection", {'layers': layers, 'rules': rules})


# %%
server.launch(open_browser=False)
# %%
