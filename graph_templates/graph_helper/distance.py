from geopy.distance import distance as geopy_distance

import math


def distance(from_vert, to_vert, taxicab=True, distance_unit=None) -> float:
    """Computes distance between two points.

    Attributes:
        from_vert      pair of the source coordinates
        to_vert        pair of the target coordinates
        taxicab        usage of taxicab or Euclidean metric
        distance_unit  if not None, used as a parameter for convergence from GPS coordinates
                       (e.g., 'm' or 'meters', 'mi' or 'miles', 'km' or 'kilometers')
    """
    if distance_unit is None:
        # no GPS, no unit
        if taxicab:
            return abs(from_vert[0] - to_vert[0]) + abs(from_vert[1] - to_vert[1])
        else:
            return math.sqrt((from_vert[0] - to_vert[0]) ** 2 + (from_vert[1] - to_vert[1]) ** 2)

    # GPS, units by ‹distance_unit›

    if taxicab:
        d = geopy_distance(from_vert, (to_vert[0], from_vert[1])) + \
            geopy_distance(from_vert, (from_vert[0], to_vert[1]))
    else:
        # Euclidean distance
        d = geopy_distance(from_vert, to_vert)

    # convert to units given by ‹distance_unit›
    return getattr(d, distance_unit)
