import collections
import glob
import logging
import os

import eyed3

ROOT_DIR = '/home/dante_gates/music/Music'
OUTPUT_DIR = '/home/dante_gates/music/clean'

SKIP_FILE = 'moved.log'
FAIL_FILE = 'failed.log'


def list_files(dir_):
    return list(glob.glob('{}/**/*mp3'.format(dir_), recursive=True))


class CouldNotReadMetaData(ValueError):
    def __init__(self, file):
        super().__init__('could not read metadata on %s' % file)


Tag = collections.namedtuple('Tag', 'artist,album,title,track_num')
def get_tag(f):
    try:
        metadata = eyed3.load(f).tag
    except Exception as err:
        raise CouldNotReadMetaData(f) from err
    return Tag(metadata.artist, metadata.album, metadata.title, metadata.track_num[0])


def rename(f):
    tag = get_tag(f)
    try:
        return os.path.join(tag.artist, tag.album, f'{tag.track_num:02d} {tag.title}.mp3')
    except TypeError:
        pass


def move(mp3_file, target_dir):
    renamed = rename(mp3_file)
    if renamed is None:
        return False
    destination = os.path.join(target_dir, renamed)
    os.makedirs(destination, exist_ok=True)
    os.link(mp3_file, destination)
    print('moved {mp3_file} to {destination}')
    return True


def log_processed(filename, log_file):
    with open(log_file, 'a') as f:
        f.write(f'{filename}\n')


def main(src_dir, target_dir):
    files = list_files(src_dir)
    print('found %s files' % len(files))
    for filename in files:
        try:
            success = move(filename, target_dir)
            log_processed(filename, SKIP_FILE)
        except FileExistsError:
            pass
        except Exception as err:
            print(err)


if __name__ == '__main__':
    main(ROOT_DIR, OUTPUT_DIR)
