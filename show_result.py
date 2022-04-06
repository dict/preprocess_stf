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


def result02_get_counts_all(root):

    mp4s = sorted(glob(f'{root}/clip/*.mp4'))
    mp4s = {Path(e).stem:e for e in mp4s}

    anchors = sorted(glob(f'{root}/df_info/df_anchor_i/*.pickle'))
    anchors = {Path(e).stem: e for e in anchors}

    ppys = sorted(glob(f'{root}/preprocess/*/df_fan.pickle'))
    ppys = {Path(e).parent.name:Path(e).parent for e in ppys}
    
    # 프리프로세싱되지 않은 pickle list 
    errors = set(anchors.keys()) - set(ppys.keys()) 
    errors = sorted(list(errors))

    print(f'anchors:{len(anchors)}, mp4s:{len(mp4s)}, ppys:{len(ppys)}')
    print(f'errors: {len(errors)}')
    return {'anchors':anchors, 'mp4s':mp4s, 'ppys':ppys, 'errors': errors}


def result02_show_errors(anchors, mp4s, ppys, errors):
    if len(errors) == 0:
        print('error 가 없습니다.')
        return
    
    
    # 프리프로세싱되지 않은 pickle list 하나하나 살펴보기 
    for name in errors:
        print(name)
        df = pd.read_pickle(anchors[name])
        display(df.head())

        print('mp4:', mp4s[name[:-4]])
        show_result.display_video(mp4s[name[:-4]])

        print('name:', name)
        assert(Path(mp4s[name[:-4]]).exists())
        if input() == 'q':
            break
        ipd.clear_output(wait=True)
        
        
    
def result02_show_review(anchors, mp4s, ppys, errors, check_csv, playbackrate=1.5, width=600):
    for i, (name, clip) in enumerate(ppys.items()):
        print('i:', i)
        try:
            df = pd.read_csv(check_csv)
        except:
            df = pd.DataFrame([], columns=['clip', 'status'])

        if name in df['clip'].values:
            continue

        ipd.display(df.tail(3))

        cs = pd.read_pickle(clip/'df_fan.pickle')['cropped_size'].values[0]

        print(f'{(len(df), i)}/{len(ppys)}: name({name}), cropped_size({cs}px)')
        display_video(clip/'debug.mp4', width=f'width={width}', playbackrate=playbackrate)
        c = input()
        if c == 'q' or c == 'Q' or c == 'ㅂ':
            break

        checks = {'y':'yes', 'n':'no', 'Y':'yes', 'N':'no', 'ㅛ':'yes', 'ㅜ':'no'}
        if c in checks:
            status = checks[c]
        else:
            status = None 

        df = df.append({'clip':name, 'status': status}, ignore_index=True)

        df.to_csv(check_csv, index=False)
        ipd.clear_output(wait=True)        
        
        
def result01_get_counts_all(root):
    mp4s = sorted(glob(f'{root}/clip/*.mp4', recursive=True))
    df_face   = glob(f'{root}/df_info/df_face_info/*.pickle')
    df_anchor = glob(f'{root}/df_info/df_anchor_i/*.pickle')

    print(f'df_face:{len(set(df_face))}, df_anchor:{len(set(df_anchor))}, mp4s:{len(set(mp4s))}')
    return {'df_face':df_face, 'df_anchor':df_anchor, 'mp4s':mp4s}
    
    
def result01_show_review(df_face, df_anchor, mp4s, playbackrate=1.5, width=600):
    for p in df_anchor:
        sample_mp4 = [f for f in mp4s if Path(f).stem == Path(p).stem[:-4]][0]
        print(p)
        out_name = f'temp/{Path(p).name}.mp4'
        os.makedirs(os.path.dirname(out_name), exist_ok=True)
        write_video(sample_mp4, out_name, p)
        display_video(out_name, width=f'width={width}', playbackrate=playbackrate)
        c = input()
        if c == 'q' or c == 'Q' or c == 'ㅂ':
            break
        ipd.clear_output(wait=True)
