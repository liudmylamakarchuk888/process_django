import csv
import datetime
import glob
import json
import os
import sys
import av
import numpy as np  # linear algebra
from keras import backend as K
from keras.applications import MobileNetV2, imagenet_utils
from PIL import Image, ImageFile
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.applications.mobilenet_v2 import (MobileNetV2,
                                                        preprocess_input)
from tensorflow.keras.layers import (Dense, GlobalAveragePooling2D,
                                     GlobalMaxPooling2D, Lambda, Softmax)
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image
from collections import deque
from sklearn.utils.extmath import softmax
from random import shuffle
import time

model_imagenet = MobileNetV2(weights='imagenet')

map_dict = {}
with open("./mapping.csv","r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        map_dict[row["Tier-4"]] = row

def get_dict(sorted_tuples,count):
    _dict = {}
    for tuple in sorted_tuples:
        key = tuple[0]
        val = tuple[1]
        if key not in _dict:
            _dict[key] = 0
        _dict[key] += int(val/count * 100)
    return _dict

def get_video_summary(items_list):
    cat_dict = {};obj_dict={};place_dict={};act_dict = {};subj_dict = {}
    count = len(items_list)
    for item in items_list:
        iab_cat = item["category"] + "-" + item["subcategory"]
        if iab_cat not in cat_dict:
            cat_dict[iab_cat] = 0
        cat_dict[iab_cat] += 1

        object = item["object"] 
        if object != "":
            if object not in obj_dict:
                obj_dict[object] = 0
            obj_dict[object] += 1

        place = item["place"]
        if place != "": 
            if place not in place_dict:
                place_dict[place] = 0
            place_dict[place] += 1

        activity = item["activity"]
        if activity != "": 
            if activity not in act_dict:
                act_dict[activity] = 0
            act_dict[activity] += 1

        subject = item["subject"] 
        if subject != "":
            if subject not in subj_dict:
                subj_dict[subject] = 0
            subj_dict[subject] += 1

    
    sorted_cats = sorted(cat_dict.items(), key=lambda x: x[1],reverse=True)[:5]    
    sorted_objs = sorted(obj_dict.items(), key=lambda x: x[1],reverse=True)[:5]    
    sorted_places = sorted(place_dict.items(), key=lambda x: x[1],reverse=True)[:5]
    sorted_acts = sorted(act_dict.items(), key=lambda x: x[1],reverse=True)[:5] 
    sorted_subjs = sorted(subj_dict.items(), key=lambda x: x[1],reverse=True)[:5]
    
    summary_dict = {}
    summary_dict["places"] = get_dict(sorted_places,count)
    summary_dict["activities"] = get_dict(sorted_acts,count)
    summary_dict["subjects"] = get_dict(sorted_subjs,count)
    summary_dict["objects"] = get_dict(sorted_objs,count)
    summary_dict["iab-categories"] = get_dict(sorted_cats,count)
    
    return summary_dict

def process_stream(video_url):
    try:
        folder,filename = os.path.split(video_url)
        filename_without_ext = filename.split(".")[0]
        start = time.time()

        container = av.open(video_url)
        stream = container.streams.video[0]
        tgt_folder = os.path.join("frames",filename_without_ext)
        if not os.path.isdir(tgt_folder): os.makedirs(tgt_folder)
        v_start = None;v_end = None
        #we only look at key-frames
        stream.codec_context.skip_frame = 'NONKEY'
        frames_json_list = []
        duration = None

        for n,frame in enumerate(container.decode(stream)):
            try:
                frame_time = frame.pts * stream.time_base
                if v_start is None: v_start = frame_time
                v_end = frame_time
                img_pil = frame.to_image()
                #img_pil.thumbnail((480,480))
                #img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                frame_pil = img_pil.resize((224,224), Image.ANTIALIAS)
                x = image.img_to_array(frame_pil)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)

                in_preds = model_imagenet.predict(x)

                P = imagenet_utils.decode_predictions(in_preds)
                tag_dict = {}
                for (i, (imagenetID, label, prob)) in enumerate(P[0]):
                    if prob <= 0.1: break
                    cat = map_dict[label]["Tier-1"]
                    subcat = map_dict[label]["Tier-2"]
                    tag = map_dict[label]["Tier-3"]
                    activity = map_dict[label]["activity"]
                    place = map_dict[label]["place"]
                    actor = map_dict[label]["actor"]
                    if actor != "":
                        display = "{} {} {}".format(actor,activity,tag)
                    else:
                        if place == "":
                            display = "{} {} {}".format(tag,activity,actor)
                        else:
                            display = "{} {} {}".format(tag,activity,place)


                    score = int(prob * 100)
                    tag_dict["timestamp"] = int(frame_time)
                    tag_dict["category"] = cat
                    tag_dict["subcategory"] = subcat
                    tag_dict["object"] = tag
                    tag_dict["score"] = score
                    tag_dict["place"] = place
                    tag_dict["activity"] = activity
                    tag_dict["subject"] = actor

                    frames_json_list.append(tag_dict)

                    break

            except Exception as e:
                print(e)

        summary_dict = get_video_summary(frames_json_list)

    except Exception as e:
        print(e)
    return summary_dict



def main():

    test_url_list = ["http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
                    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
                    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4"]


    for url in test_url_list:
        summary_dict = process_stream(url)
        print("[+] send callback to callback url: ", summary_dict)