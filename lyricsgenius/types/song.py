# LyricsGenius
# Copyright 2018 John W. Miller
# See LICENSE for details.

import os
from filecmp import cmp

from ..utils import sanitize_filename
from .base import BaseEntity, Stats
from .artist import Artist


class Song(BaseEntity):
    """A song from the Genius.com database.

    Attributes:
        annotation_count (:obj:`int`)
        api_path (:obj:`str`)
        artist (:obj:`str`):
            Primary artist's name
            (Same as ``Song.primary_artist.name``)
        full_title (:obj:`str`)
        header_image_thumbnail_url (:obj:`str`)
        header_image_url (:obj:`str`)
        id (:obj:`int`)
        lyrics (:obj:`str`)
        lyrics_owner_id (:obj:`int`)
        lyrics_state (:obj:`str`)
        path (:obj:`str`)
        primary_artist (:class:`Artist`)
        pyongs_count (:obj:`int`)
        song_art_image_thumbnail_url (:obj:`str`)
        song_art_image_url (:obj:`str`)
        stats (:class:`Stats`)
        title (:obj:`str`)
        title_with_featured (:obj:`str`)
        url (:obj:`str`)

    """

    def __init__(self, client, json_dict, lyrics=''):
        body = json_dict
        super().__init__(body['id'])
        self._body = body
        self._client = client
        self.artist = body['primary_artist']['name']
        self.lyrics = lyrics
        self.primary_artist = Artist(client, body['primary_artist'])
        self.stats = Stats(body['stats'])

        self.annotation_count = body['annotation_count']
        self.api_path = body['api_path']
        self.full_title = body['full_title']
        self.header_image_thumbnail_url = body['header_image_thumbnail_url']
        self.header_image_url = body['header_image_url']
        self.lyrics_owner_id = body['lyrics_owner_id']
        self.lyrics_state = body['lyrics_state']
        self.path = body['path']
        self.pyongs_count = body['pyongs_count']
        self.song_art_image_thumbnail_url = body['song_art_image_thumbnail_url']
        self.song_art_image_url = body['song_art_image_url']
        self.title = body['title']
        self.title_with_featured = body['title_with_featured']
        self.url = body['url']

    def to_dict(self):
        """Creates a dictionary from the song object.
        Used in :func:`save_lyrics` to create json object.

        Returns:
            :obj:`dict`

        """
        body = super().to_dict()
        body['lyrics'] = self.lyrics
        return body

    def to_json(self,
                filename=None,
                sanitize=True,
                ensure_ascii=True):
        """Converts the Song object to a json string.

        Args:
            filename (:obj:`str`, optional): Output filename, a string.
                If not specified, the result is returned as a string.
            sanitize (:obj:`bool`, optional): Sanitizes the filename if `True`.
            ensure_ascii (:obj:`bool`, optional): If ensure_ascii is true
              (the default), the output is guaranteed to have all incoming
              non-ASCII characters escaped.

        Returns:
            :obj:`str` \\| :obj:`None`: If filename is None, returns the lyrics as
            a plain string, otherwise None.

        Warning:
            If you set :obj:`sanitize` to `False`, the file name may contain
            invalid characters, and thefore cause the saving to fail.

        """
        data = self.to_dict()

        return super().to_json(data=data,
                               filename=filename,
                               sanitize=sanitize,
                               ensure_ascii=ensure_ascii)

    def to_text(self,
                filename=None,
                binary_encoding=False,
                sanitize=True):
        """Saves the song lyrics as a text file.

        Args:
            filename (:obj:`str`, optional): Output filename, a string.
                If not specified, the result is returned as a string.
            binary_encoding (:obj:`bool`, optional): Enables binary encoding
                of text data.
            sanitize (:obj:`bool`, optional): Sanitizes the filename if `True`.

        Returns:
            :obj:`str` \\| :obj:`None`: If :obj:`filename` is
            `None`, returns the lyrics as a plain string, otherwise `None`.

        Warning:
            If you set :obj:`sanitize` to `False`, the file name may contain
            invalid characters, and thefore cause the saving to fail.

        """
        data = self.lyrics

        return super().to_text(data=data,
                               filename=filename,
                               binary_encoding=binary_encoding,
                               sanitize=sanitize)

    def save_lyrics(self,
                    filename=None,
                    extension='json',
                    overwrite=False,
                    binary_encoding=False,
                    ensure_ascii=True,
                    sanitize=True,
                    verbose=True):
        """Save Song lyrics and metadata to a JSON or TXT file.

        If the extension is 'json' (the default), the lyrics will be saved
        alongside the song's information. Take a look at the example below.

        Args:
            filename (:obj:`str`, optional): Output filename, a string.
                If not specified, the result is returned as a string.
            extension (:obj:`str`, optional): Format of the file (`json` or `txt`).
            overwrite (:obj:`bool`, optional): Overwrites preexisting file if `True`.
                Otherwise prompts user for input.
            binary_encoding (:obj:`bool`, optional): Enables binary encoding
                of text data.
            ensure_ascii (:obj:`bool`, optional): If ensure_ascii is true
                (the default), the output is guaranteed to have all incoming
                non-ASCII characters escaped.
            sanitize (:obj:`bool`, optional): Sanitizes the filename if `True`.
            verbose (:obj:`bool`, optional): prints operation result.

        Examples:
            .. code:: python

                # getting songs lyrics from saved JSON file
                import json
                with open('song.json', 'r') as f:
                    data = json.load(f)

                print(data['lyrics'])

        Note:
            If :obj:`full_data` is set to `False`, only the following attributes
            of the song will be available: :obj:`title`, :attr:`album`, :attr:`year`,
            :attr:`lyrics`, and :attr:`song_art_image_url`

        Warning:
            If you set :obj:`sanitize` to `False`, the file name may contain
            invalid characters, and thefore cause the saving to fail.

        """
        extension = extension.lstrip(".").lower()
        msg = "extension must be JSON or TXT"
        assert (extension == 'json') or (extension == 'txt'), msg

        # Determine the filename
        if filename:
            for ext in ["txt", "TXT", "json", "JSON"]:
                filename = filename.replace("." + ext, "")
            filename += "." + extension
        else:
            filename = "Lyrics_{}_{}.{}".format(self.artist.replace(" ", ""),
                                                self.title.replace(" ", ""),
                                                extension).lower()
        filename = sanitize_filename(filename) if sanitize else filename

        # Check if file already exists
        write_file = False
        if overwrite or not os.path.isfile(filename):
            write_file = True
        elif verbose:
            msg = "{} already exists. Overwrite?\n(y/n): ".format(filename)
            if input(msg).lower() == 'y':
                write_file = True

        # Exit if we won't be saving a file
        if not write_file:
            if verbose:
                print('Skipping file save.\n')
            return

        # Save the lyrics to a file
        if extension == 'json':
            self.to_json(filename, ensure_ascii=ensure_ascii, sanitize=sanitize)
        else:
            self.to_text(filename, binary_encoding=binary_encoding, sanitize=sanitize)

        if verbose:
            print('Wrote {} to {}.'.format(self.title, filename))
        return None

    def __str__(self):
        """Return a string representation of the Song object."""
        if len(self.lyrics) > 100:
            lyr = self.lyrics[:100] + "..."
        else:
            lyr = self.lyrics[:100]
        return '"{title}" by {artist}:\n    {lyrics}'.format(
            title=self.title, artist=self.artist, lyrics=lyr.replace('\n', '\n    '))

    def __cmp__(self, other):
        return (cmp(self.title, other.title)
                and cmp(self.artist, other.artist)
                and cmp(self.lyrics, other.lyrics))
