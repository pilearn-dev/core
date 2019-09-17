#!/usr/bin/env python

# From: https://gist.github.com/ihercowitz/642650/f01986c0b1ebd04be588b196eb3ffefe9853e113

import PIL.Image
import os, sys

def resizeImage(infile, output_dir="", size=(512,384)):
    outfile = os.path.splitext(infile.split("\\")[-1].split("/")[-1])[0]
    extension = os.path.splitext(infile)[1]

    if (cmp(extension, ".jpg")):
        return
        

    if infile != outfile:
     
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
     
        try :
            im = PIL.Image.open(infile)
            im.thumbnail(size, PIL.Image.ANTIALIAS)
            im.save(os.path.join(output_dir,outfile+extension),"JPEG")
        except IOError:
            print "cannot reduce image for ", infile


if __name__=="__main__":
    output_dir = "main/static/CourseStockImages_small"
    dir = "main/static/CourseStockImages"

    for directory in os.listdir(dir):
        for file in os.listdir(os.path.join(dir, directory)):
            resizeImage(os.path.join(dir, directory,file), os.path.join(output_dir, directory))