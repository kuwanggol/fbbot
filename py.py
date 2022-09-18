import string
import random
from gtts import gTTS
import os

mytext = """Downloading"""
language = 'tl'
myobj = gTTS(text=mytext, lang=language, slow=False)
res = ''.join(random.choices(string.ascii_lowercase + string.ascii_lowercase, k=10))
mikey = res + ".mp3"
myobj.save(mikey)
# print result
