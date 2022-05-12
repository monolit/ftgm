import io, os
from PIL import Image, ImageDraw, ImageFont
import random, math, requests
from .. import loader, utils

def register(cb):
    cb(asciiartMod())
class asciiartMod(loader.Module):
    """Да."""
    strings = {
            "name": "asciiart",
            "no_reply": "<b>Reply to png document.</b>",
            "noimg": "<b>Там пиздец, фото нет</b>"
            }

    def __init__(self):
        self.name = self.strings['name']
        self._me = None
        self._ratelimit = []

    async def client_ready(self, client, db):
        self.client = client

    async def artcmd(self, message):
        """yes"""
        name=self.name
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        await message.edit("<i>Какаю Путена ...</i>")
        BACK_COLOR = "BLACK"
        IN_IMG=await prepare(message)
        fontik=requests.get("https://raw.githubusercontent.com/monolit/fonts/main/MiLanProVF.ttf").content
        FNT=ImageFont.truetype(io.BytesIO(fontik), 7)
        im = Image.open(IN_IMG)
        (width, height) = im.size

        line = math.ceil(im.size[0]/50 * 13 * 1.4)
        row = math.ceil(im.size[1]/50 * 6 * 1.4)
        string = ''
        for i in range(row):
            for j in range(line):
                string += str(random.choice([1, 0]))
            string += '\n'

        img = Image.new('RGBA', (im.size[0], im.size[1]), BACK_COLOR)    
        draw_text = ImageDraw.Draw(img)
        draw_text.text((1,1), string, spacing=1, font=FNT, fill=0)
        img2 = Image.open(IN_IMG)

        alphaComposited=Image.alpha_composite(img2, img)
        image = alphaComposited
        new_image = Image.new("RGBA", image.size, BACK_COLOR) 
        new_image.paste(image, (0, 0), image) 
        new_image.convert('RGB').save('RESULT.png', "PNG")
        await reply.reply(file='RESULT.png', force_document=True)
        os.remove('RESULT.png')
        await message.delete()
        await message.edit("Там пиздец, фото нет")

    async def pngcmd(self, message):
        name=self.name
        await message.reply(file=await prepare(message))
        await message.delete()
        
async def getimg(ae):
    if not ae.file:
        return False
    if not "image" in ae.file.mime_type.lower():
        return False
    return True

async def prepare(message):
    if not await getimg(message):
        reply = await message.get_reply_message()
        if not reply or not await getimg(reply):
            return False
        IN_IMG= await fill(reply)
    else:
        IN_IMG= await fill(message)

    return IN_IMG

async def fill(ae):
    if "image" in ae.file.mime_type.lower():
        img = io.BytesIO(await ae.download_media(bytes))
        image = Image.open(img).convert("RGBA")
        ImageDraw.floodfill(image, (20000, 20000), (255, 0, 0, 0), thresh=400)
        output = io.BytesIO()
        output.name = "output.png"
        image.save(output)
        output.seek(0)
        return output
    ext_=ae.document.mime_type.split("/")[-1]
    return await message.edit("""{} <b>extension</b> is not supportrted""".format(ext_))
