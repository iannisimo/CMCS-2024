import numpy as np
import traffic

# How many times should the map be regenerated until at least 2 exits are generated
MAX_SEARCH = 100

_4WayI      = traffic.utils.xcf2np('GRIDS/4WayI.xcf')
_1Way       = traffic.utils.xcf2np('GRIDS/1Way.xcf')
_4WayTL     = traffic.utils.xcf2np('GRIDS/4WayTL.xcf')
_4WayR      = traffic.xcf2np('GRIDS/4WayR.xcf')
_3WayI      = traffic.xcf2np('GRIDS/3WayI.xcf')
_3WayTL     = traffic.xcf2np('GRIDS/3WayTL.xcf')
_3WayR      = traffic.xcf2np('GRIDS/3WayR.xcf') 
_2WayI      = traffic.xcf2np('GRIDS/2WayI.xcf')
_2WayL      = traffic.xcf2np('GRIDS/2WayL.xcf')

RULES       = traffic.utils.get_rules(traffic.xcf2np('GRIDS/rules17Intent.xcf', with_alpha=True))
TRJS        = traffic.utils.get_traj(traffic.xcf2np('GRIDS/trj17.xcf'))
DLOCKS      = traffic.get_dlocks(traffic.xcf2np('GRIDS/Deadlocks.xcf'))

TILES = {
    # '1111i': _4WayI,
    # '1111t': _4WayTL,
    '1111r': _4WayR,
    '0100a': _1Way,
    # '0111i': _3WayI,
    # '0111t': _3WayTL,
    '0111r': _3WayR,
    '0011i': _2WayI,
    '0101i': _2WayL 
}

TILE_W, TILE_H = 17, 17