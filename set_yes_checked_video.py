import pandas as pd
from glob import glob
import shutil
import argparse


def main(args):
    preprocess_root = f'{args.root}/preprocess'

    df = pd.read_csv(args.checked_csv)
    #df = df.query('status == "yes"')
    print('yes 로 설정되는 비디오 개수:', len(df))
    
    for i, v in df.iterrows():
        d = f"{preprocess_root}/{v['clip']}"
        print('yes 로 설정되는 비디오:', d)

        jpgs = sorted(glob(d+"/*.jpg"))
        for f in jpgs:
            if f.endswith('_yes.jpg'):
                continue
            f_no = f.replace('_no.jpg', '_yes.jpg')
            shutil.move(f, f_no)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=str, help='video path root')
    parser.add_argument('checked_csv', type=str, help='checked csv path')
    
    args = parser.parse_args()
    main(args)
