
root="/data/home/gomthing/dataset/pwb/mon_front"
#root="/data/snowyunee/dataset/pwb/pwb_tue_blue"

echo "root : "$root


####################################
# 학습에 부적합한 비디오를 no로 변경합니다.
####################################
# parameter
# root : 위에 설정한 root
# checked_csv : result.02_crop_with_fan.ipynb 에서 저장한 csv 이름과 동일하게
#python set_no_checked_video.py $root check_pwb.csv


####################################
# check_csv 에 'no'로 설정한 비디오에 대해서,
#  처음, 마지막 30개frame 을 no 로 변경함
# 맨 앞과 뒤에만 이상한 경우가 자주 발생하므로 기능을 추가함.
####################################
# parameter
# root : 위에 설정한 root
# checked_csv : result.02_crop_with_fan.ipynb 에서 저장한 csv 이름과 동일하게
# --frame_count : no 로 설정할 frame 갯수 (예: 30 이면 앞뒤 30 개씩 총 60개를 no로 만든다.)
python set_no_first_last_secs.py $root check_pwb_tue_blue_all-start-end.csv --frame_count 30


####################################
# 전체를 yes 로 변경
# * no 로 세팅한 것이 부적합할 때 다시 되돌리기 위해 사용될 수 있습니다.
####################################
# parameter
# root : 위에 설정한 root
# checked_csv : result.02_crop_with_fan.ipynb 에서 저장한 csv 이름과 동일하게
#python set_yes_checked_video.py $root check_pwb.csv
