# requires: yt-dlp Pillow cryptg wget
import os, wget
from .. import loader, utils
from telethon.tl.types import DocumentAttributeAudio
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
		await ses(self, message, args, reply, '')

	async def ytacmd(self, message):
		args=utils.get_args(message)
		reply=await message.get_reply_message()
		await ses(self, message, args, reply, 'a')

async def ses(self, message, args, reply, type_):
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
		'outtmpl': '%(title)s.%(ext)s',
		'add-metadata': True
		}

	uri=args[0] if args else reply.message
	await message.edit("loading")

	if type_=='a':
		try:
			opts.update({'format':'ba[ext^=m4a]'})
			a, nama=await gget(uri,opts)
		except Exception as e:
			print(e)
			opts['format']='ba[ext^=mp3]'
			a, nama=await gget(uri,opts)

		_ = a['uploader'] if 'uploader' in a else 'umknown'
		th, thumb_=await get_thumb(a, message)
		await self.client.send_file(
			message.to_id,
			nama,
			supports_streaming=True,
			reply_to=reply.id if reply else None,
			thumb=th,
			attributes=[
			DocumentAttributeAudio(duration=int(a['duration']),
				title=str(a['title']),
				performer=_)],
			caption=await readable(a, type_))

	else:
		try:
			opts.update({'format': 'bestvideo[ext^=mp4][height<1400][fps>30]+ba[ext^=m4a]'})
			a, nama=await gget(uri,opts)
		except Exception as e:
			print(e)
			opts['format']='best[ext^=mp4][height<1400]'
			a, nama=await gget(uri,opts)

		th, thumb_=await get_thumb(a, message)
		await self.client.send_file(message.to_id, th, force_document=False)

		await self.client.send_file(
			message.to_id,
			nama,
			thumb=th,
			force_document=False,
			reply_to=reply.id if reply else None,
			supports_streaming=True,
			caption=await readable(a, type_))

	[os.remove(i) for i in [nama, th, thumb_]]
	await message.delete()

async def gget(uri, opts):
	with YoutubeDL(opts) as ydl:
		a=ydl.extract_info(uri, download=True)
		nama=ydl.prepare_filename(a)
	return a, nama
async def get_thumb(a, m):
	thumb=a['thumbnails'][-1]['url']
	thumb_=wget.download(thumb)
	th=f"{a['id']}.jpg"
	Image.open(thumb_).save(th, quality=100)
	await m.edit('uplowing')
	return th, thumb_
async def readable(a, type_):
	_=f"""<a href={a['original_url']}>{a['title']}</a>
bitrate:{a['abr']}Kb ext:{a['ext']}"""
	if type_!='a':
		try:fps=a['fps']
		except:fps=None
		_+=f""" res:{a['resolution']} fps:{fps}"""
	return _
