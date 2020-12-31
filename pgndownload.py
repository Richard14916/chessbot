# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 00:52:44 2020

@author: kblax
"""

#Script to download all the pgns for training and put them into a folder

import os
import requests
scriptdir = os.path.dirname(os.path.realpath(__file__))
from zipfile import ZipFile

#making file name

zipname = "PGNS.rar"
#putting them in a folder created where the script was run
zippath = os.path.join(scriptdir, zipname)
#link for google drive
file_id = '1Kn09Pta4IdKGqO31_z4W1JcYoNrb6QwO'
#####################################################################################
#https://stackoverflow.com/questions/38511444/python-download-files-from-google-drive-using-url
#if it works dont change it
def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                
#download file
download_file_from_google_drive(file_id, zippath)


#RELEASE THE UNZIPPER
with ZipFile(zipname, 'r') as zippy:
    zippy.extractall(scriptdir)


