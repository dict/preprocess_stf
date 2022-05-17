import pandas as pd
from glob import glob
import shutil
import argparse


def main(args):
    preprocess_root = f'{args.root}/preprocess'

    df = pd.read_csv(args.checked_csv)
    for i, v in df.iterrows():
        if v['status'] != 'no':
            continue

        d = f"{preprocess_root}/{v['clip']}"
        print(f'처음과 마지막 {args.frame_count} frame을 no 로 설정되는 비디오:', d)

        jpgs = sorted(glob(d+"/*.jpg"))
        jpgs = jpgs[:args.frame_count] + jpgs[-args.frame_count:]
        for f in jpgs:
            if f.endswith('_no.jpg'):
                continue
            f_no = f.replace('_yes', '_no')
            shutil.move(f, f_no)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=str, help='video path root')
    parser.add_argument('checked_csv', type=str, help='checked csv path')
    parser.add_argument('--frame_count', type=int, default=30, help='checked csv path')
    
    args = parser.parse_args()
    main(args)
