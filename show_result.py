from glob import glob
from collections import Counter
from IPython.display import HTML
from pathlib import Path

import imageio_ffmpeg
from moviepy.editor import VideoFileClip
from pathlib import Path
import imageio, cv2, random, pandas as pd
from tqdm.auto import tqdm
from moviepy.editor import ImageSequenceClip
import os
import IPython.display as ipd
import numpy as np


def get_writer(out_path, meta):
    ffmpeg_params = None
    size = meta["size"]
    fps = meta["fps"]
    writer = imageio_ffmpeg.write_frames(out_path,
                                         size = size,
                                         fps=fps,
                                         ffmpeg_log_level='error',
                                         quality = 10, # 0~10
                                         output_params=ffmpeg_params)
    
    writer.send(None)  # seed the generator
    return writer


def get_nframes(path):
    clip = VideoFileClip(path)
    nframes = clip.reader.nframes
    clip.close()
    return nframes
    
    
# pickle 에 있는 정보로 얼굴 네모 치면서 비디오 생성
def write_video(in_path, out_path, pickle):
    # document : https://github.com/imageio/imageio-ffmpeg
    reader = imageio_ffmpeg.read_frames(in_path)
    meta = next(reader)
    size = meta["size"]
    fps = meta["fps"]
    writer = get_writer(out_path, meta)
 
    
    nframes = get_nframes(in_path)
    
    df = pd.read_pickle(pickle)
    for idx, f in tqdm(enumerate(reader), total=nframes, desc="read and write"):
        f = np.frombuffer(f, dtype=np.uint8)
        f = f.reshape(size[1], size[0], 3)
        #frame = compose_func(o, f)
        rows = df.query(f'frame_idx == {idx}')
        if len(rows) > 0:
            row = rows.iloc[0]
            x1, y1, x2, y2 = row['box']
            cv2.rectangle(f, (x1, y1), (x2, y2), (255,0,0))
        writer.send(f)  # seed the generator

    writer.close()

def display_video(p, width='width=800', playbackrate=1.0):
    p = str(p)
    assert(Path(p).exists())
    print('playbackrate:',playbackrate)
    html = f"""
    <video {width}  controls autoplay id="theVideo">
        <source src="{p}">
    </video>
    <script>
    video = document.getElementById("theVideo");
    video.playbackRate = {playbackrate};
    </script>
    """
    display(HTML(html))
    
    

# 메타데이터 추출 유틸
def video_meta(file):
    vid = imageio.get_reader(file, 'ffmpeg')
    meta = vid.get_meta_data()
    meta['path'] = file 
    meta['nframes'] = vid.count_frames()
    vid.close()
    return meta
