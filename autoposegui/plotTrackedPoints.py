from skimage import draw
import numpy as np


def create_body_indices(bodyparts, skeleton):
    bpts_val = {}
    for i, bpts in enumerate(bodyparts):
        bpts_val[bpts] = i
    sk_num = []
    for sk in skeleton:
        sk_val = [bpts_val[sk[0]], bpts_val[sk[1]]]
        sk_num.append(sk_val)
    return sk_num


def plot_tracked_points(image, h5, frame_number, skeleton, dot_size=4):
    scorer = h5.columns.get_level_values('scorer').unique().item()
    bodyparts = h5.columns.get_level_values('bodyparts').unique().to_list()
    individuals = h5.columns.get_level_values('individuals').unique().to_list()

    # Color
    # Red for individual 1 and Blue for 2
    color = [[0, 0, 1], [(1, 0, 0)]]

    height, width = image.shape[:2]
    ny, nx = height, width

    bpt_indices = create_body_indices(bodyparts, skeleton)

    for j, ind in enumerate(individuals):

        individual = h5[scorer][ind]
        df_x, df_y = individual.values.reshape((len(individual), -1, 2)).T

        for bp1, bp2 in bpt_indices:
            if not (np.any(np.isnan(df_x[[bp1, bp2], frame_number]))
                    or np.any(np.isnan(df_y[[bp1, bp2], frame_number]))):
                rr, cc, val = draw.line_aa(
                    int(np.clip(df_y[bp1, frame_number], 0, ny - 1)),
                    int(np.clip(df_x[bp1, frame_number], 0, nx - 1)),
                    int(np.clip(df_y[bp2, frame_number], 0, ny - 1)),
                    int(np.clip(df_x[bp2, frame_number], 0, nx - 1))
                )
                image[rr, cc] = (np.array([1, 1, 1]) * 255).astype(np.uint8)

        for i, bp in enumerate(bodyparts):
            rr, cc = draw.disk((df_y[i, frame_number], df_x[i, frame_number]), dot_size, shape=image.shape)
            image[rr, cc, :] = (np.array(color[j]) * 255).astype(np.uint8)

    return image
