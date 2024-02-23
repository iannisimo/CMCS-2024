# %%
GUI = True

import mesa
import traffic

if GUI:

    W = 8
    H = 8

    w = W * traffic.const.TILE_W
    h = H * traffic.const.TILE_H

    SCALE_MULTIPLE = 10

    canvas_element = traffic.CanvasGridS(traffic.portrayCell, w, h, 800, 800)
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
        'seed': 69,
        'w_tiles': W,
        'h_tiles': H
    })
    server.launch(open_browser=False)

else:

    br = mesa.batch_run(
        traffic.Intersection,
        parameters={
            # 'layers': [tiled_layers],
            # 'rules': [rules],
            # 'trjs': [trjs],
            # 'dlocks': [dlocks],
            # 'city_layout': [map]
        },
        iterations=1,
        max_steps=10,
    )




    print([b['Crashed'] for b in br])
    print([b['Spawned'] for b in br])
    print([b['Despawned'] for b in br])
    print([b['Alive'] for b in br])
    from pprint import pprint
    pprint(([b['Agents'] for b in br]))


# %%
