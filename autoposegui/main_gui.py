import PySimpleGUI as sg
import cv2
import yaml
from pathlib import Path
import pandas as pd
from processFrame import process_frame
from plotTrackedPoints import plot_tracked_points
from swapLabels import swap_labels, swap_label_sequences
from lastFrameNumber import last_frame_number
from relabelPoints import relabel_points
from updateH5file import update_h5file
from setRunParameters import set_run_parameters
from propagatePreviousFrame import propagate_previous_frame


def main_gui():
    """ GUI MainFrame"""
    sg.theme('DarkAmber')
    parameters = set_run_parameters()
    scale_factor = parameters.scale_factor
    # Layout #######################################################################################################

    # Top Layout ############################################################################
    top_layout = [[sg.Text('Video FilePath', font=parameters.small_font),
                   sg.In(size=(parameters.large_font, 1), enable_events=True, key="Files_Vid", expand_x=True,
                         background_color='white', text_color='black', font=parameters.small_font),
                   sg.FileBrowse(size=(parameters.small_font, 1), font=parameters.smaller_font)],
                  [sg.Text('H5 FilePath', font=parameters.small_font),
                   sg.In(size=(parameters.large_font, 1), enable_events=True, key="Files_H5", expand_x=True,
                         background_color='white', text_color='black', font=parameters.small_font),
                   sg.FileBrowse(size=(parameters.small_font, 1), font=parameters.small_font)],
                  [sg.Text('', size=(0, 1), key='Output', font=parameters.mid_font)]
                  ]

    # Left Layout ############################################################################
    left_side_layout = [[sg.Graph(
        canvas_size=(parameters.canvas_width, parameters.canvas_width),
        graph_bottom_left=(0, 0),
        graph_top_right=(parameters.canvas_width, parameters.canvas_width),
        key='Graph',
        enable_events=True,
        drag_submits=True
    )]]
    # left_side_layout = [[sg.Image(filename="", key="Image")]]

    # Bottom Layout ############################################################################
    bottom_layout = [
        [sg.Slider(range=(0, 1000), default_value=0, resolution=1, orientation='h',
                   expand_x=True, enable_events=True, key="Frame_Slider", font=parameters.mid_font),
         sg.Text('Go To Frame', font=parameters.large_font),
         sg.In(size=(parameters.small_font, 1), enable_events=True, key='Go_To',
               font=parameters.large_font, background_color='white', text_color='black'),
         sg.Button('Previous Frame', enable_events=True, key="Previous_Frame", size=parameters.small_font,
                   auto_size_button=True, font=parameters.small_font),
         sg.Button('Next Frame', enable_events=True, key="Next_Frame", size=parameters.small_font,
                   auto_size_button=True, font=parameters.small_font),
         sg.Button('Swap Labels', enable_events=True, key="Swap_Labels", size=parameters.small_font,
                   auto_size_button=True, font=parameters.small_font),
         sg.Button('Quit', button_color='red', size=parameters.small_font, auto_size_button=True,
                   font=parameters.small_font)
         ]
    ]

    # Using Configuration Files ############################################################################
    config_path = Path('.') / 'config.yaml'

    with open(config_path, 'r') as fr:
        config = yaml.load(fr, Loader=yaml.FullLoader)

    last_frame_path = Path('.') / 'last_video_frame.yaml'

    if last_frame_path.exists():
        with open(last_frame_path, 'r') as fr:
            last_frame_data = yaml.load(fr, Loader=yaml.FullLoader)

    # Right Layout ############################################################################
    body_parts = config['body_parts']
    bodyparts_layout = sg.Listbox(values=body_parts, key=f'Bodypart', enable_events=True,
                                  size=(parameters.mid_font, len(body_parts)), font=parameters.small_font)

    animals_layout = [
        sg.Combo(config['animals'], default_value='', font=parameters.large_font, key="Animals",
                 background_color='white', text_color='black')]

    right_lower_layout = [[sg.Text('Swap Sequence of Frames', font=parameters.large_font)],
                          [sg.Button('Mark Start', enable_events=True, key='Mark_Start',
                                     font=parameters.large_font)],
                          [sg.Text('From: ', font=parameters.large_font),
                           sg.In(enable_events=True, key='From_Frame', background_color='white',
                                 text_color='black', font=parameters.small_font)],
                          [sg.Button('Mark End', enable_events=True, key='Mark_End',
                                     font=parameters.large_font)],
                          [sg.Text('To: ', font=parameters.large_font),
                           sg.In(enable_events=True, key='To_Frame', background_color='white',
                                 text_color='black', font=parameters.small_font)],
                          [sg.Button('Swap Sequence', enable_events=True, key='Swap_Sequence',
                                     font=parameters.large_font)]]

    right_side_layout = [
        [sg.Button('Relabel Animals', font=parameters.large_font, enable_events=True, key="Relabel_Animals")],
        [sg.Text('Select Animal', font=parameters.large_font)], animals_layout, [bodyparts_layout],
        [sg.Button('Done Labeling', enable_events=True, key='Done_Labeling', font=parameters.large_font)],
        [sg.HSeparator()],
        [sg.Text('Propagate Rightly Labeled Previous Frame', font=parameters.large_font)],
        [sg.Button('Propagate', font=parameters.large_font, enable_events=True, key="Propagate")],
        [sg.HSeparator()]
    ]

    for val2 in right_lower_layout:
        right_side_layout.append(val2)

    # Left-Right Layout ############################################################################
    left_right_layout = [sg.Column(left_side_layout, size=(parameters.canvas_width, parameters.canvas_width)),
                         sg.VSeparator(),
                         sg.Column(right_side_layout, vertical_alignment='top', element_justification='left',
                                   size=(300, parameters.canvas_width))]

    # Main Layout ############################################################################
    main_layout = [
        [top_layout],
        [sg.HSeparator()],
        [left_right_layout],
        [sg.HSeparator()],
        [bottom_layout]
    ]

    window = sg.Window(title='AutoPoseGUI', layout=main_layout, finalize=True,
                       return_keyboard_events=True, use_default_focus=True)
    graph = window['Graph']
    window.bind('<Button-2>', '+RIGHT CLICK+')
    graph.bind('<Button-2>', '+RIGHT CLICK+')
    listbox = window['Bodypart']
    dragging = False
    start_point = end_point = None

    # Code to Read Files ############################################################################

    body_parts_keys = {}
    for i, v in enumerate(body_parts):
        body_parts_keys[v] = i

    animal_bodypoints = {}
    bodypoints1 = {}
    bodypoints2 = {}
    index = 0
    frame_number = 0
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Quit'):
            try:
                if values["Files_Vid"]:
                    last_frame_number(frame_number, vid_filename)
            except TypeError:
                break
            break

        # Load the video file
        if event == 'Files_Vid':
            try:
                vid_filename = values["Files_Vid"]
                cap = cv2.VideoCapture(vid_filename)
                length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                slider = window['Frame_Slider']
                slider.Range = (0, length)
                slider.Update(range=(0, length))
                # Load the last frame from when the GUI was closed in the previous session
                if last_frame_path.exists():
                    frame_number = last_frame_data[vid_filename]
                    cap.set(1, frame_number)
                    ret, image = cap.read()
                else:
                    ret, image = cap.read()
                slider.Update(value=frame_number)
                # Resize the image
                image = process_frame(image, scale_factor=scale_factor)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                # window["Graph"].update(data=imgbytes)
                window["Output"].update(f"Frames: {frame_number} / {length}")
            except AttributeError:
                sg.popup_error('Unable to load the Video', font=parameters.error_font)
            except KeyError:
                sg.popup_error('Select a Video', font=parameters.error_font)

        # Load the H5 file and plot it
        if event == 'Files_H5':
            try:
                h5_filename = values["Files_H5"]
                h5 = pd.read_hdf(h5_filename)
                skeleton = config['skeleton']
                # Rescale the loaded image to the normal size before plotting the points. Only done here
                image = process_frame(image, scale_factor=int(1 / scale_factor))
                image = plot_tracked_points(image, h5, frame_number, skeleton)
                image = process_frame(image)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                # window["Image"].update(data=imgbytes)
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)

        # Sliding through the video
        if event == 'Frame_Slider':
            try:
                frame_number = int(values['Frame_Slider'])
                if frame_number > length:
                    frame_number = length - 1
                if values['Go_To']:
                    goto_number = window['Go_To']
                    goto_number.Update(value=frame_number)
                cap.set(1, frame_number)
                ret, image = cap.read()
                if values["Files_H5"]:
                    image = plot_tracked_points(image, h5, frame_number, skeleton)
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
                else:
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
            except AttributeError:
                sg.popup_error('Loaded the Last Frame', font=parameters.error_font)
            except UnboundLocalError:
                sg.popup_error('Load the Video', font=parameters.error_font)

        # Moving forward through the video one frame at a time.
        if event == 'Next_Frame' or event.startswith('Right'):
            try:
                frame_number += 1
                # Define boundary for video file
                if frame_number > length:
                    frame_number = length - 1
                slider.Update(value=frame_number)
                if values['Go_To']:
                    goto_number = window['Go_To']
                    goto_number.Update(value=frame_number)
                cap.set(1, frame_number)
                ret, image = cap.read()
                if values["Files_H5"]:
                    image = plot_tracked_points(image, h5, frame_number, skeleton)
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
                else:
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)
            except AttributeError:
                sg.popup_error('Loaded the Last Frame', font=parameters.error_font)

        # Moving Backward through the video one frame at a time.
        if event == 'Previous_Frame' or event.startswith('Left'):
            try:
                frame_number -= 1
                # Define lower boundary for video file
                if frame_number < 0:
                    frame_number = 0
                slider.Update(value=frame_number)
                if values['Go_To']:
                    goto_number = window['Go_To']
                    goto_number.Update(value=frame_number)
                cap.set(1, frame_number)
                ret, image = cap.read()
                if values["Files_H5"]:
                    image = plot_tracked_points(image, h5, frame_number, skeleton)
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
                else:
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)

        # Going to a specific frame in the video
        if event == 'Go_To':
            try:
                val_num = values['Go_To']
                if val_num == '':
                    val_num = '0'
                else:
                    val_num = val_num
                frame_number = int(val_num)
                slider.Update(value=frame_number)
                cap.set(1, frame_number)
                ret, image = cap.read()
                if values["Files_H5"]:
                    image = plot_tracked_points(image, h5, frame_number, skeleton)
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
                else:
                    image = process_frame(image, scale_factor=scale_factor)
                    imgbytes = cv2.imencode('.png', image)[1].tobytes()
                    window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                    # window["Image"].update(data=imgbytes)
                    window["Output"].update(f"Frames: {frame_number} / {length}")
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)
            except AttributeError:
                sg.popup_error('Loaded the Last Frame', font=parameters.error_font)
            except ValueError:
                sg.popup_error('Number MUST BE Positive', font=parameters.error_font)

        # Swap the labels for mis-tracked points on the animals for a single frame
        if event == 'Swap_Labels':
            try:
                h5_filename = values["Files_H5"]
                swap_labels(h5, frame_number, h5_filename)
                h5 = pd.read_hdf(h5_filename)
                image = process_frame(image, scale_factor=int(1 / scale_factor))
                image = plot_tracked_points(image, h5, frame_number, skeleton)
                image = process_frame(image)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                # window["Image"].update(data=imgbytes)
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)

        # Swap the labels for mis-tracked points on the animals for a sequence of frames.
        # Only works for two tracked animals.
        if event == 'Swap_Sequence':
            try:
                h5_filename = values["Files_H5"]
                from_frame_num = int(values['From_Frame'])
                to_frame_num = int(values['To_Frame'])
                if to_frame_num == length:
                    to_frame_num = to_frame_num
                else:
                    to_frame_num += 1
                swap_label_sequences(h5, from_frame_num, to_frame_num, h5_filename)
                h5 = pd.read_hdf(h5_filename)
                image = process_frame(image, scale_factor=int(1 / scale_factor))
                image = plot_tracked_points(image, h5, frame_number, skeleton)
                image = process_frame(image)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                # window["Image"].update(data=imgbytes)
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)

        # Get the frame number to start the sequence swap
        if event == 'Mark_Start':
            from_number = window['From_Frame']
            from_number.Update(value=frame_number)

        # Get the frame number to end the sequence swap
        if event == 'Mark_End':
            end_number = window['To_Frame']
            end_number.Update(value=frame_number)

        # Relabel badly tracked points again
        if event == 'Relabel_Animals':
            try:
                cap.set(1, frame_number)
                ret, image = cap.read()
                image = process_frame(image, scale_factor=scale_factor)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
                animal_bodypoints = {}
                bodypoints1 = {}
                bodypoints2 = {}
                index = 0
            except UnboundLocalError:
                sg.popup_error('You need to load a frame')

        # Relabeling the points
        if values['Animals']:
            animal_id = window['Animals'].get()
            if animal_id == config['animals'][1]:
                color = 'blue'
            else:
                color = 'red'
            if values['Bodypart']:
                if event == '+RIGHT CLICK+':
                    x, y = values["Graph"]
                    start_point = (x, y)
                    graph.draw_point(start_point, 6, color)
                    bpt = window['Bodypart'].get()[0]
                    if animal_id == config['animals'][1]:
                        bodypoints2[bpt] = start_point
                        animal_bodypoints[animal_id] = bodypoints2
                    else:
                        bodypoints1[bpt] = start_point
                        animal_bodypoints[animal_id] = bodypoints1

                    index = body_parts_keys[bpt]
                    index += 1
                    if index == len(body_parts):
                        index = 0
                    listbox.update(set_to_index=[index], scroll_to_index=index)

        # Adjust the relabeled points to the actual dimensions of the image.
        # Update the H5 file with the relabeled points and replot it
        if event == 'Done_Labeling':
            try:
                cap.set(1, frame_number)
                ret, image = cap.read()
                width = image.shape[1]
                new_points = relabel_points(animal_bodypoints, config, width, scale_factor, parameters.canvas_width)
                update_h5file(new_points, h5, frame_number, h5_filename)
                h5 = pd.read_hdf(h5_filename)
                image = plot_tracked_points(image, h5, frame_number, skeleton)
                image = process_frame(image)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)

        # Propagate rightly tracked body points from the previous image to the current one
        if event == "Propagate":
            try:
                propagate_previous_frame(h5, frame_number, h5_filename)
                h5 = pd.read_hdf(h5_filename)
                cap.set(1, frame_number)
                ret, image = cap.read()
                image = plot_tracked_points(image, h5, frame_number, skeleton)
                image = process_frame(image)
                imgbytes = cv2.imencode('.png', image)[1].tobytes()
                window["Graph"].draw_image(data=imgbytes, location=(0, parameters.canvas_width))
            except UnboundLocalError:
                sg.popup_error('Load the Video first', font=parameters.error_font)

    window.close()


if __name__ == '__main__':
    main_gui()
