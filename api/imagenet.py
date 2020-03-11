from django.http import JsonResponse
import requests
import json
from api.process_video_streams_imagenet_only import process_video

def process(request):
    video_url = request.GET.get('video_url')
    callback_url = request.GET.get('callback_url')
    vid_dict = []
    try:
        vid_dict = process_video(video_url)
        # vid_dict = []
    except:
        return JsonResponse({'status': '0', 'result':"Process Video error"}, status=500)
    # vid_dict = [{'video_url': "https", 'time': "02:00"}, {'video_url': "https", 'time': "02:00"}, {'video_url': "https", 'time': "02:00"}]
    try:
        r = requests.get(callback_url, params=json.dumps(vid_dict))
    except:
        return JsonResponse({'status': '0', 'result':"ConnectionError"}, status=500)
    return JsonResponse({'status': 1, 'result': 200}, status=200)