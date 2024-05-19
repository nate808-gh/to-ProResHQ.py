"""
Copyright 2024 nate808-gh
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
"""
Python Script to convert video files to ProRes 422 HQ format for editing
FFMPEG must be installed
If a single file is specified it will be converted
If a folder is specified all videos in the folder and subfolders will be converted
If the Creation Date is present in the video metadata, the ProRes file will be renamed using the Creation Date and Time (UTC)    
"""

import os
import subprocess
import sys
import shlex
from pathlib import Path

def get_color_primaries(video_path):
    """
    Uses ffprobe to extract the color primaries from the video stream metadata.
    """
    cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=color_primaries -of default=noprint_wrappers=1:nokey=1 {shlex.quote(str(video_path))}"
    try:
        color_primaries = subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        color_primaries = ""
    return color_primaries

def get_creation_time_or_filename(video_path):
    """
    Uses ffprobe to extract the creation time from the video stream metadata.
    If a creation time is not available, uses the original filename as a fallback.
    """
    cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream_tags=creation_time -of default=noprint_wrappers=1:nokey=1 {shlex.quote(str(video_path))}"
    try:
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        if result:
            creation_time = result.replace(':', '').replace('-', '').replace(' ', '_').replace('T', '_').split('.')[0]
        else:
            creation_time = video_path.stem  # Filename without extension
    except subprocess.CalledProcessError:
        creation_time = video_path.stem
    return creation_time

def convert_video_based_on_color_primaries(input_path, output_folder):
    """
    Converts a video file to ProRes HQ format using ffmpeg, selecting the conversion command
    based on the color primaries of the video.
    """
    creation_time_or_filename = get_creation_time_or_filename(input_path)
    color_primaries = get_color_primaries(input_path)

    output_file_name = f"{creation_time_or_filename}_ProResHQ.mov"
    output_path = output_folder / output_file_name

    if color_primaries == "bt709":
        cmd = f"ffmpeg -i {shlex.quote(str(input_path))} -sws_flags print_info+accurate_rnd+bitexact+full_chroma_int -vf zscale=rangein=full:range=limited -c:v prores_ks -profile:v 3 -vendor ap10 -bits_per_mb 8000 -color_primaries bt709 -color_trc bt709 -color_range pc -colorspace bt709  -pix_fmt yuv422p10le -c:a pcm_s24le {shlex.quote(str(output_path))}"
    elif color_primaries == "bt2020":
        cmd = f"ffmpeg -i {shlex.quote(str(input_path))} -sws_flags print_info+accurate_rnd+bitexact+full_chroma_int -vf zscale=rangein=full:range=limited -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -color_primaries bt2020 -color_trc arib-std-b67 -color_range pc -colorspace bt2020nc  -pix_fmt yuv422p10le -c:a pcm_s24le {shlex.quote(str(output_path))}"
    else:
        cmd = f"ffmpeg -i {shlex.quote(str(input_path))} -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le -c:a pcm_s24le {shlex.quote(str(output_path))}"

    subprocess.run(cmd, shell=True)
    print(f"Converted '{input_path}' to ProRes HQ format at '{output_path}', using color primaries: {color_primaries or 'unknown'}")

def process_directory(directory_path, output_folder):
    video_files = [p for p in directory_path.rglob('*') if p.is_file()]
    # Sort the video files by depth, processing deepest nested files first
    video_files.sort(key=lambda x: len(x.parts), reverse=True)
    for video_path in video_files:
        convert_video_based_on_color_primaries(video_path, output_folder)

def main(target_path):
    target_path = Path(target_path)
    # Check if the target path exists
    if not target_path.exists():
        print("The specified path does not exist.")
        return

    if target_path.is_file():
        output_folder = target_path.parent / "converted_videos"
        os.makedirs(output_folder, exist_ok=True)
        convert_video_based_on_color_primaries(target_path, output_folder)
    elif target_path.is_dir():
        output_folder = target_path / "converted_videos"
        os.makedirs(output_folder, exist_ok=True)
        process_directory(target_path, output_folder)
    else:
        print("The specified path is neither a file nor a directory.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_video_or_directory>")
        sys.exit(1)
    main(sys.argv[1])
