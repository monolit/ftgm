# requires: yt-dlp Pillow cryptg wget
from pathlib import Path
import os, wget
from .. import loader, utils
from telethon.tl.types import DocumentAttributeAudio
from yt_dlp import YoutubeDL
from PIL import Image


@loader.tds
class YTDLMod(loader.Module):
    """media downlod module with yt-dlp
    usage:
    .ytv +- thumb + reply
    .ytv url +- thumb
    same with yta
    subscribe t.me/uwun3ss plox"""
    strings = {
        "name": "YTDL"
    }
    def __init__(self):
        self.name = self.strings['name']

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def ytvcmd(self, message):
        """.ytv - dowmload video media"""
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        await ses(self, message, args, reply, 'v')

    async def ytacmd(self, message):
        """.ytv - dowmload audio media"""
        args = utils.get_args(message)
        reply = await message.get_reply_message()
        await ses(self, message, args, reply, 'a')


async def ses(self, message, args, reply, type_):
    # greet https://stackoverflow.com/a/38667103
    opts = {
        'embed-thumbnail': True,
        'no-check-format': True,
        #'convert-thumbnail': 'png',
        'writethumbnail': True,
        'postprocessors': [
            {'key': 'SponsorBlock'},
            {'key': 'EmbedThumbnail'},
            {
                'key':
                    'ModifyChapters',
                    'remove_sponsor_segments': [
                        'sponsor',
                        'intro',
                        'outro',
                        'interaction',
                        'selfpromo',
                        'preview',
                        'music_offtopic'
                    ]
            }
        ],
        #'no-check-certificate': True,
        'prefer_ffmpeg': True,
        'geo_bypass': True,
        'outtmpl': '%(title)s.%(ext)s',
        'add-metadata': True
    }
    text = reply.message if reply else None
    if args:
        thumb_ = 'thumb' in args
        if uri := args[0]:
            if 'http' in uri: pass
            else: uri = text
    else:
        thumb_ = False
        uri = text
    message = await utils.answer(message, "loading")

    if type_ == 'a':
        try:
            opts.update({
                'format': 'bestaudio[ext=m4a]/best'
            })
            a, nama = await gget(uri, opts)
        except Exception as e:
            print(e)
            #del opts['format']
            opts['format'] = 'bestaudio[ext=m4a]/best'
            opts['postprocessors'].pop(0); opts['postprocessors'].pop(1)
            #del opts['embed-thumbnail']
            #del opts['writethumbnail']
            #opts['format'] = 'ba'
            opts['postprocessors'].append({'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'})
            a, nama = await gget(uri, opts)

            #nama = ''.join(nama.split('.')[:-1]) + '.mp3'
        _ = a['uploader'] if 'uploader' in a else None#'umknown'

        th, thumb = await get_thumb(a, message)
        if thumb_: await self.client.send_file(
            message.chat_id,
            th,
            force_document=False)

        await self.client.send_file(
            message.chat_id,
            nama,
            supports_streaming=True,
            reply_to=reply.id if reply else None,
            thumb=th,
            attributes=[
            DocumentAttributeAudio(duration=int(a['duration']),
                title=str(a['title']),
                performer=_)],
            caption=await readable(a, type_))

    elif type_ == 'v':
        try:
            opts.update({
                'format': 'bestvideo[ext=mp4][height<=?1080]+bestaudio[ext=m4a]/best' # 'bestvideo[ext^=mp4][height<1400]+ba'#[fps>30]+ba'#'[ext^=m4a]'
            })
            a, nama = await gget(uri, opts)
        except Exception as e:
            print(e)
            opts['postprocessors'].pop(0); opts['postprocessors'].pop(1)

            opts['format'] = 'bestvideo[ext=mp4][height<=?1080]+bestaudio[ext=m4a]/best'#'bestvideo[ext^=mp4][height<1400]+bestaudio/bestvideo'
            a, nama = await gget(uri, opts)

        th, thumb = await get_thumb(a, message)
        if thumb_: await self.client.send_file(
            message.chat_id,
            th,
            force_document=False)

        await self.client.send_file(
            message.chat_id,
            nama,
            thumb=th,
            force_document=False,
            reply_to=reply.id if reply else None,
            supports_streaming=True,
            caption=await readable(a, type_))

    for i in [nama, th, thumb]:
        try: Path(i).unlink(missing_ok=True)
        except Exception: pass
    if message.out: await message.delete()


async def gget(uri, opts):
    import yt_dlp.utils
    #yt_dlp.utils.std_headers['User-Agent'] = ""
    #yt_dlp.utils.std_headers['User-Agent'] = 'facebookexternalhit/1.1'
    yt_dlp.utils.std_headers['User-Agent'] = "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.115"

    with YoutubeDL(opts) as ydl:
        a = ydl.extract_info(uri, download=True)
        nama = ydl.prepare_filename(a)
    return a, nama

async def get_thumb(a, m):
    try:
        thumb = a['thumbnails'][-1]['url']
        thumb_ = wget.download(thumb)
        th = f"{a['id']}.jpg"
        Image.open(thumb_).save(th, quality=100)
        await m.edit('uplowing')
        return th, thumb_
    except Exception: return False, False


async def readable(a, type_):
    _ = f"""<a href={a['original_url']}>{a['title']}</a>
ext:{a.get('ext', None)} """

    if type_ == 'a': _ += f"""bitrate:{a['abr']}Kb """
    else:
        try: fps = a['fps']
        except: fps = None
        _ += f"res:{a.get('resolution', None)} "
        _ += f"fps:{fps} " if fps else ''
    return _
