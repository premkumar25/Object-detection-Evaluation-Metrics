import os
import shutil

det_loc = 'D:\metrics\de'
src_loc = 'D:\metrics\gd'
dest_loc = 'D:\metrics\groundtruths'
d = os.listdir(det_loc)

for file in d:
    try:
        shutil.copy(src_loc+'\\'+str(file), dest_loc)
    # print(src_loc+'\\'+str(file))
    # break
    except:
        print(file)