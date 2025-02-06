import glob
import shutil
from random import shuffle

folders=['train/person', 'train/operario', 'train/experto']

percent_to_move = 0.1
for folder in folders:
    print(f"Moving files from {folder}")
    files = glob.glob(folder + '/*')
    n_files = len(files)
    n_files_to_move = int(n_files * percent_to_move)
    shuffle(files)
    shuffle(files)
    files = files[:n_files_to_move]
    
    for i, file in enumerate(files):
        print(f"Moving {i+1}/{n_files_to_move} files", end='\r')
        new_path = file.replace('train', 'val')
        shutil.move(file, new_path)
    print()