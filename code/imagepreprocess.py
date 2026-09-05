import os
from PIL import Image
import numpy as np

pixelAspectRatio = 1.25
maxSize = (130/pixelAspectRatio, 60)
maxW, maxH = maxSize

im = Image.open(os.path.dirname(os.path.abspath(__file__))+'/images/smile-inv.webp').convert('L')
print ("input image:",im.format, im.size, im.mode)
(inW, inH) = im.size

scale = min(maxW/inW, maxH/inH)
#print(scale)

newW = int(inW*scale*pixelAspectRatio)
newH = int(inH*scale)
print("output dimensions:",(newW, newH))
#im.thumbnail(maxSize)
im = im.resize((newW, newH))
im.save(os.path.dirname(os.path.abspath(__file__))+"/images/small.jpg", "JPEG") #save sample image (8 bit greyscale)
print("8-bit preview saved to /images/small.jpg")
#im.show()
arr = np.asarray(im) >> 6  # convert to 2 bit greyscale that the glowclock framebuffer uses

np.set_printoptions(threshold=np.inf)
#print(np.array2string(arr, separator=', '))

with open (os.path.dirname(os.path.abspath(__file__))+'/lib/image.py','w', encoding='utf-8') as f:
	f.write("img = "+np.array2string(arr, separator=', ')) 

print("image saved to /lib/image.py")
print("copy image.py to glowclock's filesystem to use")