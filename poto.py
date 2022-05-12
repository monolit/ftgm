import os
from .. import loader, utils
class GetPPMod(loader.Module):
	"""Description for module"""
	strings = {
	"name": "Profile Photos",
	"err": "<code>ID number you entered is invalid</code>",
	"uerr": "infvalid query",
	"iderr": "<code>No photo found with that id</code>"
	}
	async def client_ready(self, client, db):
		self.client = client
		self.db = db
	async def potocmd(self, message):
		"""Gets the profile photos of replied or queried users, channels or chats"""
		args=utils.get_args_raw(message).strip().split()
		lst=["doc", "nolimit", "count"]
		doc=False
		chat = message.to_id

		reply=await message.get_reply_message()
		limit=69
		if not args and reply:
			if not reply.fwd_from:
				u=await self.client.get_entity(reply.from_id)
				await getpfp(self,message,u, limit)
			else:
				fwd=reply.fwd_from.from_id
				entity=await self.client.get_entity(fwd)
				await getpfp(self,message,entity, limit)

		if len(args)>1:
			try:
				id=int(args[1])-1
			except:
				return await message.edit("not integer")
			entity=await self.client.get_entity(int(args[0])if str(args[0]).isdigit() else str(args[0]))
			limit=None if id>limit else limit
			a=self.client.iter_profile_photos(entity,limit=limit);b=[];f=[]
			async for _ in a:
				b.append(_)
			if id>len(b):
				await message.edit('found in goolag')
				return
			g=b[id].video_sizes
			tr=b[id]
			if g:
				pfp=await self.client.download_media(tr, "in.mp4")
				name=f"{entity.id}_{tr.date}.mp4"
				os.system(f'ffmpeg -y -i "{pfp}" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
	-c:v copy -shortest "{name}"')
				f.append(name)
			else:
				pfp=await self.client.download_media(tr, f"{entity.id}_{tr.date}")
				f.append(pfp)
			await self.client.send_file(message.to_id, file=f, force_document=doc)

		elif len(args)==1:
			entity=await self.client.get_entity(int(args[0])if str(args[0]).isdigit() else str(args[0]))
			try:
				await getpfp(self,message,entity,limit)
			except:
				await message.edit('serch in goolag')

####
async def gete(self,u):
	entity=await self.client.get_entity(u)
	return entity
####
async def getpfp(self,message,entity,limit):
	doc=False
	a=self.client.iter_profile_photos(entity, limit=limit);b=[];f=[]
	async for _ in a:
		b.append(_)
	async for _ in a:
		g=_.video_sizes
		if g:
			pfp=await self.client.download_media(_, "in.mp4")
			name=f"{entity.id}_{_.date}.mp4"
			os.system(f'ffmpeg -y -i "{pfp}" -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 \
	-c:v copy -shortest "{name}"')
			f.append(name)
		else:
			pfp=await self.client.download_media(_, f"{entity.id}_{_.date}")
			f.append(pfp)

	await self.client.send_file(message.to_id, file=f, force_document=doc)
	#os.system("cd && rm -rf *.jpg && rm -rf *.mp*")
