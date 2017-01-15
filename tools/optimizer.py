from PIL import Image
import sys
import time
from os.path import basename

file = sys.argv[1]
im = Image.open(file)

def strip_exif(image):
    dat = list(image.getdata())
    final = Image.new(image.mode, image.size)
    final.putdata(dat)
    return final

start = time.time()
print basename(file) + '-stripped.jpg'
strip_exif(im).save(file + '-stripped.jpg', "JPEG", quality=60)
end = time.time()
print 'done {0}ms'.format(str(end - start))
