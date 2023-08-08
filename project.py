from tkinter.filedialog import askdirectory
from multiprocessing import Process
import subprocess
import json
import os
import re
from termcolor import colored
import time


def check_ffmpeg(path='ffmpeg') -> None:
    """
    This function checks if `ffmpeg`, `mkvmerge`, and `mkvpropedit` are present in the `/ffmpeg` folder.
    If not, FileNotFoundError is raised.
    """
    progs = ["ffmpeg", "mkvmerge", "mkvpropedit"]
    for prog in progs:
        if not os.path.exists(f"{path}/{prog}.exe"):
            raise FileNotFoundError(f"{prog}.exe not found. Please download {prog} and place it in the /ffmpeg folder.")

    return True


def mkv_directory() -> dict:
    """
    Opens a dialog window to ask the user for the directory of mkv files.
    Yields a list of mkv files.
    """
    os.system("cls")
    window_title = "Select directory with mkv files"
    path = askdirectory(title=window_title)

    for dirpath, dirname, files in os.walk(path):
        for file in files:
            if file.endswith(".mkv"):
                yield os.path.join(dirpath, file)


def get_mkv_tracks(mkv_file) -> dict:
    """
    This function runs the `mkvmerge -i` command to input mkv file and returns a JSON output containing info about the tracks inside the file.

    :param file: This is the path of the mkv file.
    """
    class Track:
        def __init__(self, track) -> None:
            props = track["properties"]
            self.name = props.get("track_name", "None")
            self.id = props["number"]
            self.language = props["language"]
            self.type = track["type"]
            self.origin = os.path.basename(mkv_file)
            self.path = os.path.dirname(os.path.abspath(mkv_file))
            self.isDefault = 1 if props["default_track"] else 0
            self.isForced = 1 if props["forced_track"] else 0

    try:
        command = ['ffmpeg/mkvmerge', '-i', mkv_file, '-F', 'json']
        mkv_info = json.loads(subprocess.check_output(command))
        tracks = mkv_info["tracks"]
        for track in tracks:
            track["properties"].pop("codec_private_data", None)
        return [Track(t) for t in tracks if t["type"] in ["audio", "subtitles"]]
    except subprocess.CalledProcessError:
        raise subprocess.CalledProcessError(f"Error while getting tracks from {mkv_file}.", command)


def get_tracks_count(tracks):
    """
    This function returns the number of audio and sub tracks inside an mkv file.

    :param tracks: This is the output of `get_mkv_tracks` function.
    """
    try:
        audio_tracks = [track for track in tracks if track.type == "audio"]
        sub_tracks = [track for track in tracks if track.type == "subtitles"]
        return len(audio_tracks), len(sub_tracks)
    except TypeError:
        raise TypeError("The MKV file might be corrupted or is missing tracks. Please check the file.")


def set_audio_track_flag(audio_track: object) -> None:
    """
    This function assigns `flag_default=1` for JAP AUDIO. Otherwise, `flag_default=0`.
    The variable `flag_default` will be used as commandline argument in `mkvpropedit` later.

    :param audio_track: This is a track (of class Track) inside an mkv file.
    """
    if audio_track.language != "jpn":
        audio_track.isDefault = 0
        audio_track.isForced = 0
        return

    is_JAP_audio = audio_track.language == "jpn"
    audio_track.isDefault = 1 if is_JAP_audio else 0
    audio_track.isForced = 1 if is_JAP_audio else 0

    return


def set_sub_track_flag(sub_track: object) -> None:
    """
    This function assigns `flag_default=1` for ENG DIALOG SUBS. Otherwise, `flag_default=0`.
    The variable `flag_default` will be used as commandline argument in `mkvpropedit` later.

    :param sub_track: This is a track (of class Track) inside an mkv file.
    """
    if sub_track.language != 'eng':
        sub_track.isDefault = 0
        sub_track.isForced = 0
        return

    # def count_dialogue_lines(srt):
    #     pattern = r'-->'
    #     lines = re.findall(pattern, srt, flags=re.MULTILINE)
    #     return len(lines)

    # srt_path = os.path.join(sub_track.path, f"{sub_track.origin}_Track_{sub_track.id}_[{sub_track.name}].srt")
    # command = [ "ffmpeg/ffmpeg", "-i", os.path.join(sub_track.path, sub_track.origin), "-map", f"0:{sub_track.id}", srt_path ]
    # subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # with open(srt_path, 'r') as srt:
    #     dialogue_lines = count_dialogue_lines(srt.read())
    # os.remove(srt_path)

    dialog_track_names = ["dialog", "full", "english"]
    lyrics_track_names = ['sign', 'song', 's&s']

    # is_ENG_sub = sub_track.type == "subtitles" and dialogue_lines >= 200 and sub_track.language == "eng"
    is_ENG_dialogue = any(text in sub_track.name.lower() for text in dialog_track_names)
    is_ENG_lyrics = any(text in sub_track.name.lower() for text in lyrics_track_names)

    sub_track.isDefault = 1 if (is_ENG_dialogue and not is_ENG_lyrics) else 0
    sub_track.isForced = 1 if (is_ENG_dialogue and not is_ENG_lyrics) else 0

    return


def generate_mkvpropedit_command(mkv_file, tracks) -> list:
    """
    This function adds all audio and sub tracks as commandline arguments to `mkvpropedit`
    """
    command = ['ffmpeg/mkvpropedit', mkv_file]
    for track in tracks:
        command += ["--edit", f'track:{track.id}']
        command += ['--set', f'flag-default={track.isDefault}']
        command += ['--set', f'flag-forced={track.isForced}']
    return command
    

def yield_terminal_output(mkv_file, tracks) -> str:
    """
    This function generates a prompt message to be displayed in the terminal.
    Information about the tracks' flags inside the mkv file is displayed.
    """
    audio_count, sub_count = get_tracks_count(tracks)
    prompt = f'{mkv_file} \nAudio tracks={audio_count}, Sub tracks={sub_count}\n'

    flag_count = 0
    for track in tracks:
        flag_count += track.isDefault
        color = "dark_grey" * (1 - track.isDefault) + "green" * track.isDefault
        prompt += colored(f" Track:{track.id} Type:{track.type[:3]} Language:{track.language} Name:{track.name}\n", color)
    
    status = 1 if flag_count >= 2 else 0
    color = "yellow" * (1 - status) + "cyan" * status
    status_message = "Check tracks" * (1 - status) + "Pass" * status + '\n'
    prompt += colored(status_message, color)

    return prompt


def change_flags(mkv_file: str) -> None:
    """
    This function changes the flags of audio and sub tracks inside an mkv file,
    specifically, JAP AUDIO and ENG DIALOGUE SUBS. 
    It uses the functions defined above
    """
    tracks = get_mkv_tracks(mkv_file)
    filename = os.path.basename(mkv_file)

    for track in tracks:
        if track.type == "audio":
            set_audio_track_flag(track)
        elif track.type == "subtitles":
            set_sub_track_flag(track)

    command = generate_mkvpropedit_command(mkv_file, tracks)
    subprocess.run(command, stdout=subprocess.DEVNULL)
    print(yield_terminal_output(filename, tracks))

    return


def measure_duration(func):
    """
    This function measures the duration of execution of the child function wrapped herein
    """
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        duration = round(end - start, 2)
        exit_message = f"Conversion complete \nTime elapased: {duration} seconds"
        print(exit_message)

    return wrapper


@measure_duration
def begin_process(directory):
    global processes
    processes = list()

    for mkv_file in directory:
        p = Process(target=change_flags, args=[mkv_file])
        p.start()
        processes.append(p)

    for process in processes:
        process.join()
    
    return


def main():
    if check_ffmpeg():
        directory = mkv_directory()
        begin_process(directory)


if __name__ == '__main__':
    main()