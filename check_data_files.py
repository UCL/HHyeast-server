import os
import glob
import nameProcessing as np

def clean_files():
    filelist = glob.glob(os.path.expanduser('~/data/*.ssw11.hhr'))
    for f in filelist:
        name = os.path.basename(f).split('.')[0].upper()
        if not np.is_systematic_name(name):
            print(f)
            # os.remove(f)

def download_files():
    for name in np.name_maps.std:
        filepath = os.path.join(os.path.expanduser('~/data'),name+'.0.ssw11.hhr')
        if not os.path.isfile(filepath):
            print(name+'.0.ssw11.hhr')
            # for f in `python3 -c 'import check_data_files as ch; ch.download_files()'`; do scp cceaiac@legion.rc.ucl.ac.uk:/scratch/scratch/ucbtaut/Levine/results/$f ~/data; done
