
root="/data/snowyunee/dataset/pwb/di_split_pwb_tue_blue"
GPUS="2,3,4,5,6,7"
JOB_NUM="24"

echo "root : "$root
ls $root/clip/

####################################
# 1. 얼굴영역을 정장한다. 
####################################

# parameter
# 1 input video 경로
# 2 얼굴 영역 정보 저장될 경로
# 3 --gpu 1,2,3 : gpu 1,2,3 세개를 사용한다.
# 4 --JOB_NUM 3 : 작업 프로세스 개수(동시에 3개가 일을 처리한다. 많으면 좀 더 빨라진다.)
# 5 --reference_face ./hunet/hunet.png : 처리할 얼굴 사진 (png, jpg 관계없음)
# 6 --stride 30 : 몇 프레임 마다 얼굴을 찾을 것인지 (30 이면 매 30프레임마다 얼굴을 찾는다는 뜻이다.)
#python 01-df_anchor_i.py $root/clip  $root/df_info --gpu $GPUS --JOB_NUM $JOB_NUM --reference_face  $root/pwb.jpg --stride 30

####################################
# 2. result.01_df_anchor_i.ipynb 로 결과를 확인한다.
####################################


####################################
# 3. 얼굴 피쳐포인트를 저장하고, 얼굴 영역을 crop한 이미지를 저장한다.
####################################
# parameter
# 1 input video 경로
# 2 얼굴 정보 저장된 위치 (01-df_anchor_i.py 에서 2번째 파라미터 )
# 3 얼굴 피처포인트 저장될 경로
# 4 --gpu 1,2,3 : gpu 1,2,3 세개를 사용한다.
# 5 --JOB_NUM 3 : 작업 프로세스 개수(동시에 3개가 일을 처리한다. 많으면 좀 더 빨라진다.)
python 02-crop_with_fan.py  $root/clip $root/df_info  $root/preprocess --gpu $GPUS --JOB_NUM $JOB_NUM



####################################
# 4. 프리프로세싱된 결과 이미지로 debug.mp4 생성
####################################
# parameter
# 1 input video 경로
# 2 전처리된 위치 정보 (02-crop_with_fan.py 에서 3번째 파라미터 )
python 03-make_debug_mp4.py $root/clip $root/preprocess



####################################
# 5. result.02_crop_with_fan.ipynb 로 결과를 확인한다.
####################################



####################################
# 6. 오디오 audio -> mel
####################################
# parameter
# 1 전처리된 위치 정보 (02-crop_with_fan.py 에서 3번째 파라미터 )
python 04-make_mels.py $root/preprocess

