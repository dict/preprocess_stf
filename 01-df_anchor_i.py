from utils import face_finder as ff
from glob import glob
from pathlib import Path
from IPython.display import display
from PIL import Image
import cv2
import imageio
import torch
import subprocess
import sys
import argparse
import os
from tqdm import tqdm
import traceback


g_args = None


def log(*args):
    print(g_args.JOB_ID, ':', *args)


def main(args):
    cuda = f'cuda:{args.gpu[args.JOB_ID%args.GPU_NUM]}'
    log('cuda:', cuda)
    args.cuda = cuda
    ff.init_face_finder(device=cuda)

    #mp4s = sorted(glob('hunet/211125_split_30sec/**/*.mov', recursive=False))
    mp4s = sorted(glob(os.path.join(args.input, '*')))
    mp4s += sorted(glob(os.path.join(args.input, '**/*')))
    mp4s = [f for f in mp4s if os.path.isfile(f)]
    log('*** video count : ', len(mp4s))
    #len(mp4s), Path(g_reference_face).exists(), mp4s
    
    # 폴더명 없이 파일 명으로만 저장할 것이라서 파일명이 중복되지 않는지 검증한다
    names = [Path(m).name for m in mp4s]
    # 중복 목록 프린트
    if len(names) != len(set(names)):
        from collections import Counter
        log(Counter(names))
    # 중복이 있으면 문제가 생기므로, assert 로 확인
    assert(len(names) == len(set(names)))
    
    # 아나운서 얼굴 정보를 구한다.
    df_face, imgs = ff.find_face(args.reference_face)
    
    #  assert: 사진에 등장하는 얼굴은 경수 아나운서 얼굴 1개여야 한다
    assert(len(df_face) == 1 and len(imgs) == 1)
    
    anchor_ebd = df_face['ebd'].values[0]
    log(f'anchor_ebd.shape:{anchor_ebd.shape}')
    
    # 디버깅을 위해 그려본다
    log('#########################################')
    #log('# for debugging log df_face')
    #log(df_face)

    x1, y1, x2, y2 = df_face['box'].values[0]
    img = Image.fromarray(
        cv2.rectangle(
            imageio.imread(args.reference_face),
            (x1, y1), (x2, y2), (0, 255, 0), 4)).resize((224, 224))
    img.save('./face.jpg')
    log('# ./face.jpg 에서 얼굴을 잘 골랐는지 확인할 수 있습니다.')
    log('#########################################')
    
    # 모든 동영상에 대해 얼굴 recognize 모듈로 아나운서 얼굴 위치만 저장해 놓는다
    errors = []
    verbose=True
    for i, mp4 in enumerate(mp4s):
        if i % args.JOB_NUM != args.JOB_ID:
            continue
        log(f'# {i}/{len(mp4s)}, {int(i*100/len(mp4s))}% : {mp4}')
        
        pickle_path_1 = os.path.join(args.output, f'df_face_info/{Path(mp4).stem}.pickle')
        pickle_path_2 = os.path.join(args.output, f'df_anchor_i/{Path(mp4).stem}_000.pickle')
        if Path(pickle_path_1).exists() and Path(pickle_path_2).exists():
            log('continue ------------ ', i, pickle_path_1)#, pickle_path_2)
            continue
            
        if Path(pickle_path_1).exists(): os.remove(pickle_path_1)
        if Path(pickle_path_2).exists(): os.remove(pickle_path_2)
        try:
            df_paths = ff.save_face_info3(mp4, anchor_ebd, base=args.output,
                                          stride=args.stride,
                                          callback=None, verbose=verbose)
        except:
            errors.append(mp4)
            log('error!!. ', errors)
            log(traceback.format_exc())
    log('####### complete !!')
    log('\tlen error!!. ', len(errors))
    log('\terrors:', errors)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='video path root')
    parser.add_argument('output', type=str, help='output root')
    parser.add_argument('--gpu', type=str, required=False, default='', help='gpu list')
    parser.add_argument('--JOB_ID', type=int, required=False, default=-1,
                        help='job id')
    parser.add_argument('--JOB_NUM', type=int, required=False, default=1,
                        help='concurrent processs count')
    parser.add_argument('--reference_face', required=False, type=str, 
                        default='./data/face.jpg', help='face image path')
    parser.add_argument('--stride', required=False, type=int, 
                        default=30, help='face image path')
    args = parser.parse_args()
    print('stride:', args.stride)

    # gpu 를 지정하지 않으면, 전체 gpu 를 사용하도록 한다.
    if len(args.gpu) == 0:
        args.gpu = ','.join([str(i) for i in range(torch.cuda.device_count())])
    print('gpu : ', args.gpu)

    # log 에 사용하도록 global variable 에 저장한다.
    g_args = args

    # parameter 확인
    if not os.path.exists(args.reference_face):
        print('face file is not exist:', args.reference_face)
        exit()
    if not os.path.exists(args.input):
        print('input not exist:', args.input)
        exit()

    if args.JOB_NUM == 1:
        print('current process')
        # JOB_NUM 이 1이면 직접한다.
        args.JOB_ID = 0
        args.gpu = args.gpu.split(',')
        args.GPU_NUM = len(args.gpu)
        print(sys.argv)
        main(args)
    else:
        if args.JOB_ID < 0:
            # JOB_NUM 만큼 subprocess 를 띄워서 실행시킨다.
            childs = []
            for job_id in range(args.JOB_NUM):
                cmd = ['python'] + sys.argv[0:3]
                cmd += ['--JOB_ID', str(job_id),
                        '--JOB_NUM', str(args.JOB_NUM),
                        '--gpu', str(args.gpu),
                        '--reference_face', args.reference_face]
                p = subprocess.Popen(cmd, stdin=None)
                childs.append(p)
            # 자식 process가 완료되기를 기다린다.
            _ = [p.wait() for p in childs]

        else:
            # 자식 process 이므로, 실제 작업을 진행한다.
            args.gpu = args.gpu.split(',')
            args.GPU_NUM = len(args.gpu)
            print(sys.argv)
            main(args)

