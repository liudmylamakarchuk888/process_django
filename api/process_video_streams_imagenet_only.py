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

def process_video(vf):
    model_imagenet = MobileNetV2(weights='imagenet')
    video_dict_list = []
    try:
        container = av.open(vf)
        stream = container.streams.video[0]
        stream.codec_context.skip_frame = 'NONKEY'
        folder,filename = os.path.split(vf)
        frames_list = [];frame_times = []
        ts_list = []
        for frame in container.decode(stream):
            frame_img = frame.to_image()
            frame_pil = frame_img.resize((224,224), Image.ANTIALIAS)
            frame_time = frame.pts * stream.time_base
            frame_times.append(float(frame_time))
            x = image.img_to_array(frame_pil)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            frames_list.append(x)
        
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

