import pandas as pd


def swap_labels(h5, frame_number, h5_filename):
    scorer = h5.columns.get_level_values('scorer').unique().item()
    bodyparts = h5.columns.get_level_values('bodyparts').unique().to_list()
    individuals = h5.columns.get_level_values('individuals').unique().to_list()

    anim1 = h5[scorer][individuals[0]].values
    anim2 = h5[scorer][individuals[1]].values

    data1 = anim1.copy()
    data2 = anim2.copy()

    data1[frame_number, :] = anim2[frame_number, :]
    data2[frame_number, :] = anim1[frame_number, :]

    data_df = pd.concat((pd.DataFrame(data1), pd.DataFrame(data2)), axis=1, ignore_index=True)
    col = pd.MultiIndex.from_product([[scorer], individuals, bodyparts, ['x', 'y']],
                                     names=['scorer', 'individuals', 'bodyparts', 'coords'])
    data_ind = h5.index
    dataframe = pd.DataFrame(data_df.values, index=data_ind, columns=col)
    dataframe.to_hdf(h5_filename, 'vole_d')


def swap_label_sequences(h5, from_frame, to_frame, h5_filename):
    scorer = h5.columns.get_level_values('scorer').unique().item()
    bodyparts = h5.columns.get_level_values('bodyparts').unique().to_list()
    individuals = h5.columns.get_level_values('individuals').unique().to_list()

    anim1 = h5[scorer][individuals[0]].values
    anim2 = h5[scorer][individuals[1]].values

    data1 = anim1.copy()
    data2 = anim2.copy()

    data1[from_frame:to_frame, :] = anim2[from_frame:to_frame, :]
    data2[from_frame:to_frame, :] = anim1[from_frame:to_frame, :]

    data_df = pd.concat((pd.DataFrame(data1), pd.DataFrame(data2)), axis=1, ignore_index=True)
    col = pd.MultiIndex.from_product([[scorer], individuals, bodyparts, ['x', 'y']],
                                     names=['scorer', 'individuals', 'bodyparts', 'coords'])
    data_ind = h5.index
    dataframe = pd.DataFrame(data_df.values, index=data_ind, columns=col)
    dataframe.to_hdf(h5_filename, 'vole_d')
