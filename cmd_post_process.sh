
root="/data/home/hyejin/dataset/hunet"

echo "root : "$root


####################################
# 학습에 부적합한 비디오를 no로 변경합니다.
####################################
# parameter
# root : 위에 설정한 root
# checked_csv : result.02_crop_with_fan.ipynb 에서 저장한 csv 이름과 동일하게
python set_no_checked_video.py $root check_pwb.csv


####################################
# 전체를 yes 로 변경
# * no 로 세팅한 것이 부적합할 때 다시 되돌리기 위해 사용될 수 있습니다.
####################################
# parameter
# root : 위에 설정한 root
# checked_csv : result.02_crop_with_fan.ipynb 에서 저장한 csv 이름과 동일하게
python set_yes_checked_video.py $root check_pwb.csv