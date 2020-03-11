import csv
import json
import os
import av
import numpy as np  # linear algebra

from keras import backend as K
from keras.applications import MobileNetV2, imagenet_utils
from PIL import Image, ImageFile
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.extmath import softmax
from tensorflow.keras.applications.mobilenet_v2 import (MobileNetV2,
                                                        preprocess_input)
from tensorflow.keras.layers import (Dense, GlobalAveragePooling2D,
                                     GlobalMaxPooling2D, Lambda, Softmax)
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image

model_imagenet = MobileNetV2(weights='imagenet')


def process_video(vf):
    video_dict_list = []
    try:
        container = av.open(vf)
        stream = container.streams.video[0]
        stream.codec_context.skip_frame = 'NONKEY'
        folder,filename = os.path.split(vf)
        #fn = filename.replace(".mp4","").strip()
        frames_list = [];frame_times = []
        ts_list = []
        for frame in container.decode(stream):
            # try:
            frame_img = frame.to_image()
            frame_pil = frame_img.resize((224,224), Image.ANTIALIAS)
            frame_time = frame.pts * stream.time_base
            frame_times.append(float(frame_time))
            x = image.img_to_array(frame_pil)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            frames_list.append(x)
                #temp = datetime.datetime.fromtimestamp(ts / 1000).strftime('%H:%M:%S')
                #ts_list.append(temp)
            # except Exception as e:
            #     print(e)
        
        preds_list = model_imagenet.predict(np.vstack(frames_list),batch_size=256)
        
        P = imagenet_utils.decode_predictions(preds_list)

        for pred,time in zip(P,frame_times):
            final_dict= {}
            final_dict["video_url"] = vf
            final_dict[time] = pred
            video_dict_list.append(final_dict)
    
    except Exception as e:
        print(e)
    return video_dict_list
    


def main():

    test_url_list = ["http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4",
                    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/VolkswagenGTIReview.mp4",
                    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4",
                    "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4"]
    total_play = 0
    total_process = 0
    #shuffle(url_list)
    for url in test_url_list:
        vid_dict = process_video(url)
        print("[+] send callback to callback url: ", vid_dict)


if __name__ == '__main__':
    main()
