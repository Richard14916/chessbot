# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 00:52:44 2020

@author: kblax
"""

#Script to download all the pgns for training and put them into a folder

import os
from google_drive_downloader import GoogleDriveDownloader as gdd
scriptdir = os.path.dirname(os.path.realpath(__file__))

#making folder and file name
folder = "PGNS"
zipname = "PGNS.zip"
#putting them in a folder created where the script was run
pgnpath = os.path.join(scriptdir, folder)
zippath = os.path.join(pgnpath, zipname)
#make folder
os.mkdir(pgnpath)
#link for google drive
pgns = "https://drive.google.com/drive/folders/1vmoo9lbzJsJ9nA0dwYB5KhupIoBCesxw?usp=sharing"
#download script
gdd.download_file_from_google_drive(file_id='1vmoo9lbzJsJ9nA0dwYB5KhupIoBCesxw',
                                    dest_path=zippath,
                                    unzip=False)


