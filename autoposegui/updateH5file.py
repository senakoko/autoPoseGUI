import pandas as pd
from setRunParameters import set_run_parameters


def update_h5file(new_points, h5, frame_number, h5_filename):
    """
    Update the H5 file with the adjusted relabeled body points
    :param new_points: the adjusted newly tracked body points
    :param h5: the H5 data (not the filepath)
    :param frame_number: the frame number for the image that was relabeled
    :param h5_filename: the filepath for the H5 file
    :return: Saves the newly adjusted tracked points (overwrites the current H5 file)
    """
    parameters = set_run_parameters()
    scorer = h5.columns.get_level_values('scorer').unique().item()
    bodyparts = h5.columns.get_level_values('bodyparts').unique().to_list()
    individuals = h5.columns.get_level_values('individuals').unique().to_list()

    data_df = pd.DataFrame()
    for i in range(len(individuals)):
        data = h5[scorer][individuals[i]].values
        if len(new_points.keys()) == 2:
            data[frame_number, :] = new_points[individuals[i]]
        else:
            if individuals[i] in new_points.keys():
                data[frame_number, :] = new_points[individuals[i]]
        df = pd.DataFrame(data)
        data_df = pd.concat((data_df, df), axis=1, ignore_index=True)

    col = pd.MultiIndex.from_product([[scorer], individuals, bodyparts, ['x', 'y']],
                                     names=['scorer', 'individuals', 'bodyparts', 'coords'])
    data_ind = h5.index
    dataframe = pd.DataFrame(data_df.values, index=data_ind, columns=col)
    dataframe.to_hdf(h5_filename, parameters.animal_key)
