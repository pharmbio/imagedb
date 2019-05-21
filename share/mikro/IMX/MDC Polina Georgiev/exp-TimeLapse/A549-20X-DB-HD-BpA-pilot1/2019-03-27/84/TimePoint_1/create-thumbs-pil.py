#!/usr/local/bin/python3

import glob
from PIL import Image

sizes = [(120,120)]
files = glob.glob('*.tif')

N=0
for image in files:
    for size in sizes:
      im=Image.open(image)
      im.thumbnail(size)
      im.save("t-%d-%s.png" % (N,size[0]))

    N=N+1
