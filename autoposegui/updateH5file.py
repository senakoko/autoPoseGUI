import pandas as pd


def update_h5file(new_points, h5, frame_number, h5_filename):
    scorer = h5.columns.get_level_values('scorer').unique().item()
    bodyparts = h5.columns.get_level_values('bodyparts').unique().to_list()
    individuals = h5.columns.get_level_values('individuals').unique().to_list()

    data1 = h5[scorer][individuals[0]].values
    data2 = h5[scorer][individuals[1]].values

    data1[frame_number, :] = new_points[individuals[0]]
    data2[frame_number, :] = new_points[individuals[1]]

    data_df = pd.concat((pd.DataFrame(data1), pd.DataFrame(data2)), axis=1, ignore_index=True)
    col = pd.MultiIndex.from_product([[scorer], individuals, bodyparts, ['x', 'y']],
                                     names=['scorer', 'individuals', 'bodyparts', 'coords'])
    data_ind = h5.index
    dataframe = pd.DataFrame(data_df.values, index=data_ind, columns=col)
    dataframe.to_hdf(h5_filename, 'vole_d')
