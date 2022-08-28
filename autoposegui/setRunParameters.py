from easydict import EasyDict as eDict


def set_run_parameters(parameters=None):
    if isinstance(parameters, dict):
        parameters = eDict(parameters)
    else:
        parameters = eDict()

    scale_factor = 0.5

    canvas_width = 800

    large_font = 50

    mid_font = 20

    small_font = 10

    smaller_font = 5

    error_font = 100

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
