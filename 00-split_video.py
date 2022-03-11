import argparse
from tqdm import tqdm
import pdb
from moviepy.editor import VideoFileClip
import os
from glob import glob
from pathlib import Path
import subprocess


def main(args):
    print(args)
    print(f'### split {args.split_secs} secs')
    vids = sorted(glob(os.path.join(args.input, '**/*'), recursive=True))
    vids = [f for f in vids if os.path.isfile(f)]
    print(f'video root : {args.input}, video len : {len(vids)}')
    print('video list :')
    print('\t'+('\n\t'.join(vids)))

    overlap = 2 # 양쪽 2초 씩 더 한다.
    split_video_duration = args.split_secs
    
    # 30초 단위로 자르는데 2 초씩 앞뒤로(총 4초) 겹치게 한다.
    for vi, v in enumerate(tqdm(vids)):
        vid = VideoFileClip(v)
        duration = int(vid.duration)
        all_split = duration // split_video_duration
        _, ext = os.path.splitext(v)
        for i in range(all_split):
            f = '/'.join(v.split('/')[-2:])
            f = f.replace(' ', '_')
    
            remain = duration - (i * split_video_duration)
    
            to = (i+1)*split_video_duration if i < (all_split-1) else duration
            to = min(to + overlap, duration)
            ss = max(i*split_video_duration - overlap, 0)
            def sec_to_str(sec):
                return f'{int(sec/(60*60)):02d}:{int(sec%(60*60)/60):02d}:{sec%60:02d}'
            #print(ss, sec_to_str(ss), ', ', to, sec_to_str(to))
            ss_str = sec_to_str(ss)
            to_str = sec_to_str(to)
    
            dst_name = f"{os.path.join(args.output, f)}.{i:02d}-{all_split:02d}.ss-{ss//60:02d}-{ss%60:02d}.to-{to//60:02d}-{to%60:02d}{ext}"
    
            # old
            cmd = ['ffmpeg', '-i', v, '-ss' ,ss_str, '-to', to_str,
                   '-c:v', 'copy', '-c:a', 'aac', '-map', '0', dst_name]
            if Path(dst_name).exists():
                continue
    
            if not os.path.exists(os.path.dirname(dst_name)):
                os.makedirs(os.path.dirname(dst_name), exist_ok=True)
            with open(args.ffmpeg_out, 'a') as out:
                print(f'################ video : {vi}/{len(vids)}, split : {i}/{all_split} =================\n')
                out.write(f'################ video : {vi}/{len(vids)}, split : {i}/{all_split} =================\n')
                return_code = subprocess.call(cmd, stdout=out, stderr=out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='video path root')
    parser.add_argument('output', type=str, help='output root')
    parser.add_argument('--split_secs', required=False, type=str, default=30)
    parser.add_argument('--ffmpeg_out', required=False, type=str, 
                        default='./result_00-split_videos.log', help='ffmpeg output')
    args = parser.parse_args()
    main(args)
