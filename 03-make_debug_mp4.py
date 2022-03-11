from pathlib import Path
import pdb
import imageio
import cv2
import numpy as np
import imageio_ffmpeg
import os
import argparse
from utils import face_finder as ff, crop_with_fan as cwf
from glob import glob
from tqdm import tqdm


def main(args):
    verbose = True
    mp4s = sorted(glob(os.path.join(args.video_root, '*/*')))
    mp4s += sorted(glob(os.path.join(args.video_root, '*')))
    mp4s = [f for f in mp4s if os.path.isfile(f)]
    mp4s = {Path(e).stem:e for e in mp4s}
    print('len videos : ', len(mp4s))

    ppys = sorted(glob(os.path.join(args.crop_root, '*/df_fan.pickle')))
    ppys = {Path(e).parent.name:Path(e).parent for e in ppys}
    print('len cropped videos : ', len(ppys))

    for i, (name, clip) in enumerate(tqdm(ppys.items())):
        save_path = f'{clip}/debug.mp4'
        if verbose:
            print(f'{i+1}/{len(ppys)}, {save_path}')
        # front 는 일단 안만든다.
        #if '_1.mov' in name: continue
        #if Path(save_path).exists():
        #    print('exist : ', save_path)
        #    continue
            
        #print(f'{i} : {save_path}')
        meta = ff.video_meta(mp4s[name[:-4]])
        debug_mp4 = cwf.save_debug_clip2(clip, meta['fps'], verbose=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('video_root', type=str, help='video path root')
    parser.add_argument('crop_root', type=str, help='crop root path root')
    args = parser.parse_args()

    main(args)

