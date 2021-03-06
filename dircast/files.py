import math
from logging import getLogger
import hashlib
from datetime import timedelta, datetime
from urllib.parse import quote, urljoin

import magic
import yaml
import mutagen
import dateutil
import pytz


AUDIO_MIMETYPES = {"audio/mpeg", "audio/mp4", "video/mp4", "audio/x-hx-aac-adts"}


class FileMetadata(object):
    def __init__(self, id, title, link, mimetype):
        self.id = id
        self.title = title
        self.link = link
        self.mimetype = mimetype
        self.length = 0
        self.duration = None
        self.date = None
        self.description = None

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


def guess_mimetype(path):
    magic_mimetype = magic.from_file(str(path), mime=True)
    if magic_mimetype == "audio/x-m4a":
        return "audio/mp4"
    else:
        return magic_mimetype


def load_channel_file(path):
    path = str(path / "channel.yml")
    getLogger(__name__).info("loading %s", path)
    with open(path) as channel_file:
        return {
            key.lstrip(":"): value
            for key, value in yaml.safe_load(channel_file).items()
        }


def get_file_metadata(channel_url, mimetype, path):
    tag_info = mutagen.File(str(path), easy=True)
    try:
        title = tag_info["title"][0]
    except KeyError:
        title = path.stem
    md = FileMetadata(
        id=hashlib.sha1(title.encode()).hexdigest(),
        title=title,
        link=urljoin(channel_url, quote(str(path))),
        mimetype=mimetype
    )
    md.length = path.stat().st_size
    md.duration = timedelta(seconds=round(tag_info.info.length))
    
    try: 
        md.description = tag_info["description"][0]
    except KeyError:
        pass

    try:
        md.date = dateutil.parser.parse(tag_info["date"][0])
    except KeyError: 
        md.date = datetime.utcfromtimestamp(path.stat().st_mtime)

    # just in case
    md.date = pytz.utc.localize(md.date)

    return md


def find_files(channel_url, path):
    files = []
    for child in sorted([x for x in path.glob('**/*') if not x.is_dir()]):
        getLogger(__name__).info("checking %s of type %s", child, str(type(child)))
        mimetype = guess_mimetype(child)
        is_audio = mimetype in AUDIO_MIMETYPES
        getLogger(__name__).info(
            "%s is of type %s - %s",
            child,
            mimetype,
            "is audio" if is_audio else "not audio"
        )

        if is_audio:
            files.append(get_file_metadata(channel_url, mimetype, child))
    return files
