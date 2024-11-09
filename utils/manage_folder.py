import shutil
import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/opt/homebrew/Cellar/ffmpeg/7.1_2/bin/ffmpeg"
import moviepy.editor as moviepy

def clean_files_extensions_in_folder(folder_path):
    for i, filename in enumerate(os.listdir(folder_path), 1):
        new_name = f"x{i}.mp4"
        in_path = os.path.join(folder_path, filename)
        out_path = os.path.join(folder_path, new_name)
        
        if ".avi" in filename:
            out_path = os.path.join(folder_path, f"{filename[:-4]}.mp4")
            clip = moviepy.VideoFileClip(in_path)
            clip.write_videofile(out_path, codec='libx264')
            os.remove(in_path)
        else:
            shutil.move(in_path, out_path)

def rename_and_order_files(folder_path, prefix):
    clean_files_extensions_in_folder(folder_path)
    for i, filename in enumerate(os.listdir(folder_path), 1):
        new_name = f"{prefix}{i}.mp4"
        in_path = os.path.join(folder_path, filename)
        out_path = os.path.join(folder_path, new_name)
        
        shutil.move(in_path, out_path)