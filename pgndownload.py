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
import utils
import numpy as np

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
#download_file_from_google_drive(file_id, zippath)



#RELEASE THE UNZIPPER
#with ZipFile(zippath, 'r') as zippy:
#    zippy.extractall(scriptdir)


pgndir = os.path.join(scriptdir,zipname.split(".")[0])
pgnslist = os.listdir(pgndir)
processed_out = pgndir+"_processed"
try:
    os.mkdir(processed_out)
except:
    pass


for i,pgn in enumerate(pgnslist):
    print("beginning")
    fpath = os.path.join(pgndir,pgn)
    print(fpath)
    data = utils.Training_Data_From_PGN(fpath,count_reads=True)
    data.produce_record_data(watch_progress=True)
    new_fname_base = pgn.split(".")[0]
    np.savetxt(os.path.join(processed_out,new_fname_base+"_data"),data.record_meta_array)
    np.savetxt(os.path.join(processed_out,new_fname_base+"_labels"),data.result_meta_list)
    if i == 0:
        mega_data = data.record_meta_array
        mega_labels = data.result_meta_list
    else:
        mega_data = np.concatenate((mega_data,data.record_meta_array),axis=1)
        mega_labels += data.result_meta_list
np.savetxt(os.path.join(processed_out,"mega_data"),mega_data)
np.savetxt(os.path.join(processed_out,"mega_labels"),mega_data)
