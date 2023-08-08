import project as p
import subprocess
import pytest


def test_check_ffmpeg():
    assert p.check_ffmpeg() == True
    with pytest.raises(FileNotFoundError):
        p.check_ffmpeg('fmpeg')


def test_mkv_directory():
    generator = p.mkv_directory()
    for value in generator:
        assert isinstance(value, str)
    with pytest.raises(StopIteration):
        next(generator)


def test_get_mkv_tracks():
    with pytest.raises(TypeError):
        p.get_mkv_tracks(None)
    with pytest.raises(subprocess.CalledProcessError):
        file = 'null.mkv'
        p.get_mkv_tracks(file)


def test_get_tracks_count():
    with pytest.raises(TypeError):
        tracks = None
        p.get_tracks_count(tracks)


def test_set_audio_track_flag():
    with pytest.raises(AttributeError):
        tracks = None
        p.set_audio_track_flag(tracks)


def test_set_sub_track_flag():
    with pytest.raises(AttributeError):
        tracks = None
        p.set_sub_track_flag(tracks)


def test_generate_mkvpropedit_command():
    with pytest.raises(TypeError):
        file = 'null.mkv'
        tracks = None
        p.generate_mkvpropedit_command(file, tracks)


def test_yield_terminal_output():
    with pytest.raises(TypeError):
        file = 'null.mkv'
        tracks = None
        p.yield_terminal_output(file, tracks)


def test_change_flags():
    with pytest.raises(subprocess.CalledProcessError):
        file = 'null.mkv'
        p.change_flags(file)


def test_begin_process():
    with pytest.raises(TypeError):
        directory = None
        p.begin_process(directory)
