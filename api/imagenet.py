from django.http import JsonResponse

def process(request):
    video_url = request.POST.get('video_url')
    callback_url = request.POST.get('callback_url')
    
    return JsonResponse({'status': 1, 'result': 200})