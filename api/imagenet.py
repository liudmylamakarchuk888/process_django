from django.http import JsonResponse
import requests
import json
from api.process_videos import process_stream


def process(request):
    video_url = request.GET.get('video_url')
    callback_url = request.GET.get('callback_url')
    
    vid_dict = []
    # try:
    vid_dict = process_stream(video_url)
    # except:
    #     return JsonResponse({'status': '0', 'result':"Process Video error"}, status=500)
    print(vid_dict)    
    try:
        r = requests.get(callback_url, params=vid_dict)
        print(r.url)
    except:
        return JsonResponse({'status': '0', 'result': "ConnectionError"}, status=500)
    return JsonResponse({'status': 1, 'result': 200}, status=200)
