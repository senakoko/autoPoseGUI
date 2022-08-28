import numpy as np


def relabel_points(data, config, width, scale_factor, canvas_width):
    animals = config['animals']
    body_parts = config['body_parts']

    animals_bodyparts = {}
    for an in animals:
        body_pts = {}
        for bp in body_parts:
            if bp in data[an].keys():
                body_pts[bp] = np.array(data[an][bp])
            else:
                body_pts[bp] = np.array([np.nan, np.nan])
        animals_bodyparts[an] = body_pts

    animals_bpts = {}
    for an in animals:
        body_pts = animals_bodyparts[an].values()
        pts = []
        for bpt in body_pts:
            for i, v in enumerate(bpt):
                if i % 2 == 0:
                    new_v = v * (1 / scale_factor)  # new x coordinate
                else:
                    # new y coordinate
                    new_v = width - (v * (1 / scale_factor)) - (
                                (width * scale_factor - canvas_width) * (width / canvas_width))
                pts.append(new_v)
        animals_bpts[an] = np.array(pts)

    return animals_bpts
