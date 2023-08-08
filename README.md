# MKV Batch Set Flag
#### Video Demo:  [MKV Batch Set Flag](https://youtu.be/QFvRN-Czedc)
#### Description:
A Python script that automates the process of setting JPN audio and full ENG subtitles as default tracks for mkv files.
Processes in seconds.
Great for preparing a huge collection of anime series before doing a marathon watch!

[![Watch the video](./preview/thumbnail.png)](https://youtu.be/QFvRN-Czedc)

#### Specifications
- Built with Python 3
- Supports multiprocessing
- Informative prompts

#### Preview
![image](./preview/preview.gif)

#### Use Case
If you run this script once, you won't ever have to manually select your preferred audio and subtitle tracks for each video in your video player. 
Some video players like VLC Media Player on Android don't support choosing a preferred language for audio and subtitles.

#### How does it work?
This program reads all mkv files inside a directory and subdirectories. 
For each mkv file, `mkvmerge` finds what tracks are present. 
We look for four properties: `name`, `number`, `type`, and `language`.
These properties are used to find JPN audio and full ENG subtitles and the program sets them to default tracks.
<details>
<summary><h5>Brief overview about track properties</h5></summary>

- `name` is the label assigned to a track, useful for mkv files that provide subtitles for full dialog and for song lyrics only.
- `number` is the index of the track in the mkv file. Usually, video track always comes first at `number = 1`, followed by an audio track, and so on.
- `type` can be one of these: `video`, `audio`, `subtitles`. Naturally, a complete mkv file should contain at least three different tracks.
- `language` tells what the track's language is. For Japanese, `language=jpn` while for English, `language=eng`. 
Some tracks may not have any assigned language like video tracks, thus `lanuage=und` which means undetermined.
</details>
<details>
<summary><h5>Further explanation</h5></summary>

Because we know each track's properties, we can find tracks with `(type=audio and language=jpn)` or `(type=subtitles and language=eng)` and give these tracks a `flag-default=1` assignment. Otherwise, we give unwanted tracks `flag-default=0`.

The program automates the sending of command-line arguments to `mkvpropedit`. Here is an example of a generated command line effortlessly:
```bat
mkvpropedit "Anime S01E01.mkv" \
--edit track:2 --set flag-default=1 --set flag-forced=1 \ 
--edit track:3 --set flag-default=0 --set flag-forced=0 \
--edit track:4 --set flag-default=1 --set flag-forced=1 \
--edit track:5 --set flag-default=0 --set flag-forced=0 \
```
provided that `track:2` is a JPN audio track and `track:4` is full ENG dialogue subtitles track, while `track:3` is an ENG audio track and `track:5` is a song lyrics track. Remember that `track:1` is the video track so there is no need to modify it.

If there is at least one JPN audio track and at least one ENG dialogue subtitles track set to default after this process, then the program returns a `Pass` indicator.
Below is a sample output after a successful processing of an mkv file:
```bat
Anime S01E01.mkv
 Audio tracks:2 Subtitle tracks:2
 Track:2 Type:aud Language:jap Name:Japanese Dub
 Track:3 Type:aud Language:eng Name:English Dub
 Track:4 Type:sub Language:eng Name:English Sub
 Track:5 Type:sub Language:jap Name:Japanese Sub
Pass
```
</details>

#### Main Components
- `check_ffmpeg(path='ffmpeg')` - This function checks if `ffmpeg`, `mkvmerge`, and `mkvpropedit` are present in the `/ffmpeg` folder. If not, FileNotFoundError is raised.
- `mkv_directory()` - Opens a dialog window to ask the user for the directory of mkv files. Yields a list of mkv files. 
- `get_mkv_tracks(mkv_file)` - This function runs the `mkvmerge -i` command to input mkv file and returns a JSON output containing info about the tracks inside the file.
- `get_tracks_count(tracks):` - This function returns the number of audio and sub tracks inside an mkv file.
- `set_audio_track_flag(audio_track)` - This function assigns `flag_default=1` for JAP AUDIO. Otherwise, `flag_default=0`. The variable `flag_default` will be used as commandline argument in `mkvpropedit` later.
- `set_sub_track_flag(sub_track)` - This function assigns `flag_default=1` for ENG DIALOG SUBS. Otherwise, `flag_default=0`. The variable `flag_default` will be used as commandline argument in `mkvpropedit` later.
- `generate_mkvpropedit_command(mkv_file, tracks)` - This function adds all audio and sub tracks as commandline arguments to `mkvpropedit`
- `yield_terminal_output(mkv_file, tracks)` - This function generates a prompt message to be displayed in the terminal. Information about the tracks' flags inside the mkv file is displayed.
- `change_flags(mkv_file)` - This function changes the flags of audio and sub tracks inside an mkv file, specifically, JAP AUDIO and ENG DIALOGUE SUBS. It uses the functions defined above.
- `measure_duration(func)` - This function measures the duration of execution of the child function wrapped herein.
- `begin_process(directory)` - This function when called feeds each mkv files into the whole batch flag routine under multithreading.
- `main()` - Starts the program with asking the user for the directory of mkv files via `mkv_directory()` when `check_ffmpeg(path='ffmpeg')` passes.

#### Third-party components
- `mkvmerge` - Used to fetch information about the tracks embedded inside the mkv files, including name, language, track id's, and flags for 'default' and 'forced'.
- `mkvpropedit` - Used to edit and set the flags of the tracks of the mkv files. 
- `ffmpeg` - Used to extract subtitle tracks from mkv files and save them in srt file format.