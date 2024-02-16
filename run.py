# %%
GUI = False

import mesa
import traffic
import city
import traffic.data_collection as data_collection

import numpy as np

rules       = traffic.utils.get_rules(traffic.xcf2np('GRIDS/rules17Intent.xcf', with_alpha=True))
trjs        = traffic.utils.get_traj(traffic.xcf2np('GRIDS/trj17.xcf'))
dlocks      = traffic.get_dlocks(traffic.xcf2np('GRIDS/Deadlocks.xcf'))
_4WayI      = traffic.utils.xcf2np('GRIDS/4WayI.xcf')
_1Way       = traffic.utils.xcf2np('GRIDS/1Way.xcf')
_4WayTL     = traffic.utils.xcf2np('GRIDS/4WayTL.xcf')
_4WayR      = traffic.xcf2np('GRIDS/4WayR.xcf')
_3WayI      = traffic.xcf2np('GRIDS/3WayI.xcf')
_3WayTL     = traffic.xcf2np('GRIDS/3WayTL.xcf')
_3WayR      = traffic.xcf2np('GRIDS/3WayR.xcf') 
_2WayI      = traffic.xcf2np('GRIDS/2WayI.xcf')
_2WayL      = traffic.xcf2np('GRIDS/2WayL.xcf')



test_map = [
   ['0000', '0100', '0100', '0100', '0000'],
   ['0010', '1111', '1111', '1111', '0001'],
   ['0010', '1111', '1111', '1111', '0001'],
   ['0010', '1111', '1111', '1111', '0001'],
   ['0000', '1000', '1000', '1000', '0000']
]


# test_map = [
#     ['0000', '0100', '0100', '0100', '0000'],
#     ['0010', '1111', '1111', '1101', '0000'],
#     ['0010', '1010', '1100', '1111', '0001'],
#     ['0010', '1111', '1111', '1111', '0001'],
#     ['0000', '1000', '1000', '1000', '0000']
# ]
# test_map = [
#     ['0000', '0100', '0000'],
#     ['0010', '1111', '0001'],
#     ['0000', '1000', '0000'],
# ]
# test_map = [
#     ['0000', '0000', '0000'],
#     ['0010', '0111', '0001'],
#     ['0000', '1000', '0000'],
# ]
# test_map = [
#     ['0000', '0000', '0000', '0000'],
#     ['0000', '1111', '1111', '0000'],
#     ['0010', '1111', '1111', '0000'],
#     ['0000', '0000', '0000', '0000']
# ]

test_map = [
    ['0010', '0011', '0011', '0011', '0011', '0111'],
    ['0000', '0000', '0000', '0000', '0000', '1000']
]

map = np.array(test_map, dtype=object)

# map = city.city_planner(5, 5, 1)
tiles = {
    '1111i': _4WayI,
    '1111t': _4WayTL,
    '1111r': _4WayR,
    '0100a': _1Way,
    # '0111i': _3WayI,
    '0111t': _3WayTL,
    # '0111r': _3WayR,
    '0011i': _2WayI,
    '0101i': _2WayL 
}


tiled_layers = city.generate_city(map, tiles)

if GUI:

    w = list(tiled_layers.values())[0].shape[0]
    h = list(tiled_layers.values())[0].shape[1]

    SCALE_MULTIPLE = 5

    canvas_element = mesa.visualization.CanvasGrid(traffic.portrayCell, w, h, w*SCALE_MULTIPLE, h*SCALE_MULTIPLE)
    chart = mesa.visualization.ChartModule([{
        "Label": "Spawned",
        "Color": "Blue"
    }, {
        "Label": "Despawned",
        "Color": "Purple"
    }, {
        "Label": "Crashed",
        "Color": "Red"
    }, {
        "Label": "Alive",
        "Color": "Green"
    }])

    server = mesa.visualization.ModularServer(traffic.Intersection, [canvas_element], "Intersection", {
        'layers': tiled_layers, 
        'rules': rules,
        'trjs': trjs,
        'dlocks': dlocks,
        'city_layout': map
    })
    server.launch(open_browser=False)

else:

    br = mesa.batch_run(
        traffic.Intersection,
        parameters={
            'layers': [tiled_layers],
            'rules': [rules],
            'trjs': [trjs],
            'dlocks': [dlocks],
            'city_layout': [map]
        },
        iterations=1,
        max_steps=10,
    )




    print([b['Crashed'] for b in br])
    print([b['Spawned'] for b in br])
    print([b['Despawned'] for b in br])
    print([b['Alive'] for b in br])


# %%
