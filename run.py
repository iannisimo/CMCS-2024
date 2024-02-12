# %%
GUI = False

import mesa
import traffic
import city

import numpy as np

rules = traffic.utils.get_rules(traffic.utils.xcf2np('GRIDS/rules17Intent.xcf', with_alpha=True))
trjs = traffic.utils.get_traj(traffic.utils.xcf2np('GRIDS/trj17.xcf'))
dlocks = traffic.get_dlocks(traffic.xcf2np('GRIDS/Deadlocks.xcf'))
_4WayI = traffic.utils.xcf2np('GRIDS/4WayI.xcf')
_1Way = traffic.utils.xcf2np('GRIDS/1Way.xcf')


test_map = [
    ['0000', '0100', '0100', '0100', '0000'],
    ['0010', '1111', '1111', '1111', '0001'],
    ['0010', '1111', '1111', '1111', '0001'],
    ['0010', '1111', '1111', '1111', '0001'],
    ['0000', '1000', '1000', '1000', '0000']
]
# test_map = [
#     ['0000', '0100', '0000'],
#     ['0010', '1111', '0001'],
#     ['0000', '1000', '0000'],
# ]
# test_map = [
#     ['0000', '0000', '0000', '0000'],
#     ['0000', '1111', '1111', '0000'],
#     ['0010', '1111', '1111', '0000'],
#     ['0000', '0000', '0000', '0000']
# ]
map = np.array(test_map, dtype=object)

# map = city.city_planner(3, 3, 0)
tiles = {
    '1111i': _4WayI,
    '0100a': _1Way
}

tiled_layers = city.generate_city(map, tiles)

if GUI:

    w = list(tiled_layers.values())[0].shape[0]
    h = list(tiled_layers.values())[0].shape[1]

    SCALE_MULTIPLE = 10

    canvas_element = mesa.visualization.CanvasGrid(traffic.portrayCell, w, h, w*SCALE_MULTIPLE, h*SCALE_MULTIPLE)

    server = mesa.visualization.ModularServer(traffic.Intersection, [canvas_element], "Intersection", {
        'layers': tiled_layers, 
        'rules': rules,
        'trjs': trjs,
        'dlocks': dlocks
    })
    server.launch(open_browser=False)

else:

    br = mesa.batch_run(
        traffic.Intersection,
        parameters={
            'layers': [tiled_layers],
            'rules': [rules],
            'trjs': [trjs],
            'dlocks': [dlocks]
        },
        iterations=1,
        max_steps=1000,
    )

    print([b['Crashed'] for b in br])
    print([b['Spawned'] for b in br])
    print([b['Despawned'] for b in br])


# %%
