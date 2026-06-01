from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .forms import BlogForm
from .models import Blog, Temple, PushSubscription
import json
import math
import os


def home(request):
    temples       = Temple.objects.order_by('-id')[:6]
    all_temples   = Temple.objects.order_by('-id')
    total_temples = Temple.objects.count()
    return render(request, 'core/home.html', {
        'temples': temples,
        'all_temples': all_temples,
        'total_temples': total_temples,
    })


def temple_detail(request, id):
    temple     = get_object_or_404(Temple, id=id)
    all_others = Temple.objects.exclude(id=id)
    nearby = []
    for t in all_others:
        dist = math.sqrt((t.latitude - temple.latitude)**2 + (t.longitude - temple.longitude)**2)
        if dist < 2.0:
            nearby.append(t)
    nearby = nearby[:3]
    return render(request, 'core/temple_detail.html', {
        'temple': temple,
        'nearby_temples': nearby,
    })


def map_view(request):
    all_temples = Temple.objects.order_by('-id')
    return render(request, 'core/map.html', {'all_temples': all_temples})


def temples(request):
    temples = Temple.objects.order_by('-id')
    return render(request, 'core/temples.html', {'temples': temples})


def blog(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'core/blog.html', {'blogs': blogs})


def blog_create(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog')
    else:
        form = BlogForm()
    return render(request, 'core/blog_create.html', {'form': form})


def blog_detail(request, id):
    blog = get_object_or_404(Blog, id=id)
    # increment view counter safely
    Blog.objects.filter(pk=id).update(views=blog.views + 1)
    blog.views += 1
    return render(request, 'core/blog_detail.html', {'blog': blog})


def route_planner(request):
    temples = Temple.objects.all()
    return render(request, "core/route_planner.html", {
        "temples": temples,
        "ORS_KEY": settings.OPENROUTE_API_KEY,
    })


def about(request):
    total_temples = Temple.objects.count()
    return render(request, 'core/about.html', {'total_temples': total_temples})


# ── Push Notification endpoints ───────────────────────────────────────────────

@csrf_exempt
@require_POST
def push_subscribe(request):
    try:
        data     = json.loads(request.body)
        endpoint = data.get('endpoint')
        p256dh   = data['keys']['p256dh']
        auth     = data['keys']['auth']
        PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={'p256dh': p256dh, 'auth': auth}
        )
        return JsonResponse({'status': 'subscribed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_POST
def push_unsubscribe(request):
    try:
        data = json.loads(request.body)
        PushSubscription.objects.filter(endpoint=data.get('endpoint')).delete()
        return JsonResponse({'status': 'unsubscribed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def vapid_public_key(request):
    return JsonResponse({'publicKey': getattr(settings, 'VAPID_PUBLIC_KEY', '')})


def service_worker(request):
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'sw.js')
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = '// sw not found'
    response = HttpResponse(content, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


def offline_page(request):
    offline_path = os.path.join(os.path.dirname(__file__), 'static', 'offline.html')
    try:
        with open(offline_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = '<h1>Offline</h1>'
    return HttpResponse(content, content_type='text/html')


# ── Lore Engine (Gemini) ──────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def lore_engine(request):
    try:
        from google import genai

        data            = json.loads(request.body)
        temple_name     = data.get('name', '')
        temple_location = data.get('location', '')
        temple_desc     = data.get('description', '')
        temple_category = data.get('category', '')

        client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

        prompt_extras = {
            'Temple / Religious': "Include: 1) A surprising astronomical or Vastu fact. 2) A myth or legend about the deity. 3) A ritual detail most tourists miss.",
            'Mountain / Hill':    "Include: 1) A geological wonder about this peak. 2) A legend or folk tale about the mountain. 3) A hidden trail or secret viewpoint most trekkers miss.",
            'Beach / Coastal':    "Include: 1) A marine biology or tidal fact unique to this beach. 2) A maritime legend or local story. 3) The best-kept secret time to visit.",
            'Scenic / Nature':    "Include: 1) An ecological or geological fact about this landscape. 2) A local legend connected to this natural site. 3) A rare seasonal phenomenon few people witness.",
            'Heritage / Historical': "Include: 1) A forgotten engineering or construction secret. 2) A historical event that changed this place. 3) A hidden inscription or detail most visitors walk past.",
        }
        extra = prompt_extras.get(temple_category, "Include: 1) A surprising fact. 2) A local legend. 3) Something most visitors never notice.")

        prompt = f"""You are a mystical historian specializing in Indian sacred places. Write a deeply engaging hidden lore passage about {temple_name} in {temple_location}.

Category: {temple_category}
Known info: {temple_desc}

{extra}

Format as 3 short paragraphs with bold headers like **🔬 The Science**, **📜 The Legend**, **🤫 The Secret**. Keep it mysterious and poetic. Max 250 words."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return JsonResponse({'text': response.text})

    except Exception as e:
        import traceback
        print("LORE ERROR:", traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
