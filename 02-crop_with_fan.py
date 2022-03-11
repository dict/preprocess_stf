#!/usr/bin/env python
# coding: utf-8

##########################################
# FAN 랜드마크 기반으로 크롭한다.
##########################################


import torch
from glob import glob
from pathlib import Path
from tqdm.auto import tqdm
from utils import crop_with_fan as cwf
import os
from collections import Counter
import pdb
import argparse
import sys
import torch
import subprocess


g_args = None


def log(*args):
    print(g_args.JOB_ID, ':', *args)


def main(args):
    cuda = f'cuda:{args.gpu[args.JOB_ID%args.GPU_NUM]}'
    log('GPU_NUM:', args.GPU_NUM, ', GPU:', cuda)

    cwf.init_fan(cuda)
    
    mp4s = sorted(glob(os.path.join(args.video, '*')))
    mp4s += sorted(glob(os.path.join(args.video, '**/*')))
    mp4s = [f for f in mp4s if os.path.isfile(f)]
    log('*** video count : ', len(mp4s))

    # video 가 있는 anchor 파일만 고른다.
    anchors = sorted(glob(os.path.join(args.df_info, 'df_anchor_i', '*.pickle')))
    mp4s = {Path(e).stem:e for e in mp4s}
    anchors = [(Path(e).stem[:-4], e) for e in anchors]
    # video, anchor 개수를 로그로 남긴다.
    log(f'anchors:{len(anchors)}, mp4s:{len(mp4s)}')
    anchors = [(k,v) for k, v in anchors if k in mp4s.keys()]
    log('len(anchors)', len(anchors))
    
    # 전처리에 에러가 난 파일이 있을 수 잇으므로 개수가 같지 않을 수 있다.
    # 로그를 남겨서 상황을 알 수 있게 한다.
    if len(anchors) != len(mp4s):
        log('!!!! len(anchors) != len(mp4s)')
        anchors_keys = set([k for k, v in anchors])
        mp4_keys = set([k for k, v in mp4s.items()])
        log(len(anchors_keys - mp4_keys))
        log(anchors_keys - mp4_keys)
        log(len(mp4_keys - anchors_keys))
        log(mp4_keys - anchors_keys)
    
    anchors = sorted(anchors)
    errors = []
    pass_files = []
    for i, (name, df_path) in enumerate(tqdm(anchors)):
        if i % args.JOB_NUM != args.JOB_ID:
            continue
        
        clip_dir = Path(args.output)/Path(df_path).stem
        #if Path(f'{clip_dir}/df_fan.txt').exists():
        # 뭔가 안되는게 있어서 한번 해봤던 놈이면 건너뛰게 해둔다. 임시코드
        if Path(f'{clip_dir}/audio.wav').exists():
            continue
        if any([f in df_path for f in pass_files]):
            log('pass : ', df_path)
            continue
        
        try:
            log(i, ':', df_path, mp4s[name])
            crop_path = cwf.save_crop_info2(df_path, mp4s[name], args.output,
                                         crop_offset_y = 0.08, # + box를 내리는걸까? yes, 즉 얼굴이 올라간다.
                                         crop_margin = 0.35,
                                         verbose=True,
                                        )
            assert crop_path is not None
        except Exception as ex:
            errors.append((df_path, ex))
            log('errror!', df_path, ex)

    log('####### complete !!')
    log('errors: ', errors)
    log('pass_files : ', pass_files)
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    parser.add_argument('video', type=str, help='video path root')
    parser.add_argument('df_info', type=str, help='df_info path root')
    parser.add_argument('output', type=str, help='output root')
    parser.add_argument('--gpu', type=str, required=False, default='', help='gpu list')
    parser.add_argument('--JOB_ID', type=int, required=False, default=-1,
                        help='job id')
    parser.add_argument('--JOB_NUM', type=int, required=False, default=1,
                        help='concurrent processs count')
    args = parser.parse_args()

    # gpu 를 지정하지 않으면, 전체 gpu 를 사용하도록 한다.
    if len(args.gpu) == 0:
        args.gpu = ','.join([str(i) for i in range(torch.cuda.device_count())])
    print('gpu : ', args.gpu)

    # log 에 사용하도록 global variable 에 저장한다.
    g_args = args

    # parameter 확인
    if not os.path.exists(args.video):
        print('video path not exist:', args.video)
        exit()
    if not os.path.exists(args.df_info):
        print('df_info path not exist:', args.df_info)
        exit()

    if args.JOB_ID < 0:
        # JOB_NUM 만큼 subprocess 를 띄워서 실행시킨다.
        childs = []
        for job_id in range(args.JOB_NUM):
            cmd = ['python'] + sys.argv[0:4]
            cmd += ['--JOB_ID', str(job_id),
                    '--JOB_NUM', str(args.JOB_NUM),
                    '--gpu', str(args.gpu)]
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

