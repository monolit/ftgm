# requires: yt-dlp Pillow cryptg wget
import os, wget
from .. import loader, utils
from telethon import events
from telethon.tl.types import Message, Channel
from yt_dlp import YoutubeDL
from PIL import Image
@loader.tds
class ytdlMod(loader.Module):
	"""media downlod module"""
	strings = {
		"name": "ytdl"}
	def __init__(self):
		self.name = self.strings['name']
	async def client_ready(self, client, db):
		self.client = client
		self.db = db

	async def ytvcmd(self, message):
		""".ytv - dowmload media"""
		args=utils.get_args(message)
		reply=await message.get_reply_message()
		await ses(self, message, args, reply)

async def ses(self, message, args, reply):
	opts={
		'postprocessors':[
		#{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
		{'key': 'SponsorBlock'},
		{'key': 'ModifyChapters',
		'remove_sponsor_segments':[
		'sponsor', 'intro', 'outro', 'interaction', 'selfpromo', 'preview', 'music_offtopic']}],

		#'no-check-certificate': True, 'writethumbnail': True,
		'prefer_ffmpeg': True,
		'geo_bypass': True,
		'outtmpl': '%(title)s.%(resolution)s.%(ext)s',
		'add-metadata': True
		}
	uri=args[0] if args else reply.message
	try:
		opts.update({'format': 'best[ext^=mp4][height<1400][fps>30]'})
		a, nama=await gget(uri,opts)
	except Exception as e:
		print(e)
		opts['format']='best[height<1400]'
		a, nama=await gget(uri,opts)

	thumb=a['thumbnails'][-1]['url']
	thumb_=wget.download(thumb)

	await message.edit('uplowing')
	th=f"{a['id']}.jpg"
	Image.open(thumb_).save(th, quality=100)
	await self.client.send_file(message.to_id, thumb_, force_document=False)
	await self.client.send_file(
		message.to_id,
		nama,
		thumb=th,
		force_document=False,
		reply_to=reply.id if reply else None,
		supports_streaming=True,
		caption=f"""<a href={a['original_url']}>{a['title']}</a>
<b>res:{a['resolution']}\tfps:{a['fps']}\text:{a['ext']}</b>""")
	os.remove(nama)
	os.remove(thumb_)
	await message.delete()

async def gget(uri, opts):
	with YoutubeDL(opts) as ydl:
		a=ydl.extract_info(uri, download=True)
		nama=ydl.prepare_filename(a)
	return a, nama

async def get_thumb(a):
	1==1