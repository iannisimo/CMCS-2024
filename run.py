# %%
import mesa
import traffic

a = traffic.data2np('GRIDS/intersection.data')

canvas_element = mesa.visualization.CanvasGrid(traffic.portrayCell, a.shape[0], a.shape[1], a.shape[0]*20, a.shape[1]*20)

server = mesa.visualization.ModularServer(traffic.Intersection, [canvas_element], "Intersection", {'intersection_array': a})

# %%
server.launch(open_browser=False)