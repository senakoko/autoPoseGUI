from easydict import EasyDict as eDict


def set_run_parameters(parameters=None):
    """
    The parameters are defined in this file
    :param parameters: the parameters used throughout the package
    :return:
    """
    if isinstance(parameters, dict):
        parameters = eDict(parameters)
    else:
        parameters = eDict()

    animal_key = 'vole_d'  # key to use to save h5 files. It should match key used in the original data

    scale_factor = 0.5  # the scale factor to resize the image. O.5 is recommended

    canvas_width = 800  # the width for the canvas

    large_font = 50  # the font for most of the buttons

    mid_font = 20  # the font for most of the input boxes

    small_font = 10  # the font for some texts

    smaller_font = 5  # the font for some texts

    error_font = 100  # the font for the error messages that are displayed

    if 'animal_key' not in parameters.keys():
        parameters.animal_key = animal_key

    if 'scale_factor' not in parameters.keys():
        parameters.scale_factor = scale_factor

    if 'canvas_width' not in parameters.keys():
        parameters.canvas_width = canvas_width

    if 'large_font' not in parameters.keys():
        parameters.large_font = large_font

    if 'mid_font' not in parameters.keys():
        parameters.mid_font = mid_font

    if 'small_font' not in parameters.keys():
        parameters.small_font = small_font

    if 'smaller_font' not in parameters.keys():
        parameters.smaller_font = smaller_font

    if 'error_font' not in parameters.keys():
        parameters.error_font = error_font

    return parameters
