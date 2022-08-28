from pathlib import Path
import yaml


def last_frame_number(frame_number, video_file):
    destination_file = Path('.') / 'last_video_frame.yaml'

    video_frame = {f"{video_file}": frame_number}

    if not destination_file.exists():
        with open(destination_file, 'w') as fw:
            yaml.dump(video_frame, fw, default_flow_style=False, sort_keys=False)
    else:
        with open(destination_file, 'r') as fr:
            data = yaml.load(fr, Loader=yaml.FullLoader)
            data[f'{video_file}'] = frame_number
        with open(destination_file, 'w') as fw:
            yaml.dump(data, fw, default_flow_style=False, sort_keys=False)
