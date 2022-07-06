from glob import glob
from tqdm import tqdm
import utils.make_random_mels as mm
import argparse
import os
import imageio
import os
from pathlib import Path



def main(args):
    audios = sorted(glob(os.path.join(args.crop_root, '*/audio.wav')))
    print('audio len:', len(audios))

    print('make mels')
    for audio in tqdm(audios):
        mm.save_mels(audio)

    print('save fps')
    mp4s = [Path(e.replace('/audio.wav','/debug.mp4')) for e in audios]
    
    import imageio
    for mp4 in tqdm(mp4s):
        if not os.path.exists(mp4):
            print(f'pass : {mp4}')
            continue
        r = imageio.get_reader(mp4)
        fps = r.get_meta_data()['fps']
        with open(mp4.parent/'fps.txt', 'w') as f:
            f.write(f'{fps:.2f}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('crop_root', type=str, help='crop root path root')
    args = parser.parse_args()

    main(args)
