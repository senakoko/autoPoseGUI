import pandas as pd


def propagate_previous_frame(h5, frame_number, h5_filename):
    """
    Propagate rightly tracked body points from the previous image to the current one
    :param h5: the H5 data (not the filepath)
    :param frame_number: the frame number for the current image
    :param h5_filename: the filepath for the H5 file
    :return:
    """
    scorer = h5.columns.get_level_values('scorer').unique().item()
    bodyparts = h5.columns.get_level_values('bodyparts').unique().to_list()
    individuals = h5.columns.get_level_values('individuals').unique().to_list()

    data_df = pd.DataFrame()
    for i in range(len(individuals)):
        data = h5[scorer][individuals[i]].values
        data[frame_number, :] = data[frame_number-1, :]
        df = pd.DataFrame(data)
        data_df = pd.concat((data_df, df), axis=1, ignore_index=True)

    col = pd.MultiIndex.from_product([[scorer], individuals, bodyparts, ['x', 'y']],
                                     names=['scorer', 'individuals', 'bodyparts', 'coords'])
    data_ind = h5.index
    dataframe = pd.DataFrame(data_df.values, index=data_ind, columns=col)
    dataframe.to_hdf(h5_filename, 'vole_d')
