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
            #model='gemini-2.0-flash',
            #model='gemini-1.5-flash',

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
    print("TOKEN:", settings.MAPILLARY_TOKEN)
    return render(request, "core/route_planner.html", {
        "temples": temples,
        "ORS_KEY": settings.OPENROUTE_API_KEY,
        "MAPILLARY_TOKEN": settings.MAPILLARY_TOKEN,
    })


def about(request):
    total_temples = Temple.objects.count()
    return render(request, 'core/about.html', {'total_temples': total_temples})

@csrf_exempt
def overpass_proxy(request):
    """Server-side proxy for Overpass API to avoid browser CORS restrictions."""
    import urllib.request
    import urllib.parse

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    query = request.POST.get('data', '')
    if not query:
        try:
            from urllib.parse import parse_qs
            parsed = parse_qs(request.body.decode('utf-8'))
            query = parsed.get('data', [''])[0]
        except Exception:
            pass
    if not query:
        try:
            body = json.loads(request.body)
            query = body.get('data', '')
        except Exception:
            pass

    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    try:
        encoded = urllib.parse.urlencode({'data': query}).encode('utf-8')

        OVERPASS_SERVERS = [
            'https://overpass.kumi.systems/api/interpreter',
            'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
            'https://overpass-api.de/api/interpreter',
        ]
        result = None
        for server in OVERPASS_SERVERS:
            try:
                req = urllib.request.Request(
                    server,
                    data=encoded,
                    headers={
                        'User-Agent': 'YatraPath/1.0',
                        'Accept': 'application/json',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                break
            except Exception:
                continue

        if result is None:
            return JsonResponse({'error': 'All Overpass servers failed'}, status=502)
        return JsonResponse(result, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=502)

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
        with open(sw_path, 'r', encoding='utf-8') as f:
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
        with open(offline_path, 'r', encoding='utf-8') as f:
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

        # ── Category-specific persona + headers + instructions ──
        category_config = {
            'temple': {
                'persona':  'a mystical historian of Indian sacred architecture and ancient religion',
                'headers':  ('🔭 The Astronomy', '📜 The Legend', '🤫 The Secret'),
                'points':   [
                    'A surprising astronomical, Vastu, or sacred geometry fact about this temple',
                    'A myth or legend about the presiding deity or founding of this temple',
                    'A ritual, inscription, or architectural detail most visitors completely miss',
                ],
            },
            'mountain': {
                'persona':  'a legendary mountaineer and folklore expert of the Indian subcontinent',
                'headers':  ('🪨 The Geology', '🏔️ The Legend', '🧭 The Secret'),
                'points':   [
                    'A fascinating geological or ecological fact unique to this peak or hill',
                    'A folk tale, tribal legend, or mythological story connected to this mountain',
                    'A hidden viewpoint, rare seasonal phenomenon, or local secret most trekkers never discover',
                ],
            },
            'beach': {
                'persona':  'a coastal historian and marine storyteller of India\'s ancient shorelines',
                'headers':  ('🌊 The Science', '⛵ The Legend', '🐚 The Secret'),
                'points':   [
                    'A surprising marine biology, tidal, or oceanographic fact specific to this coastline',
                    'A maritime legend, sailor\'s tale, or ancient coastal myth from this shore',
                    'The best-kept local secret — a hidden cove, rare tide event, or time most visitors never know',
                ],
            },
            'scenic': {
                'persona':  'a naturalist poet and ecological storyteller of India\'s wild landscapes',
                'headers':  ('🌿 The Ecology', '🌙 The Legend', '✨ The Secret'),
                'points':   [
                    'A rare ecological, botanical, or geological fact about this landscape',
                    'A local legend, tribal story, or ancient myth tied to this natural place',
                    'A rare seasonal event, hidden species, or phenomenon that almost nobody witnesses',
                ],
            },
            'heritage': {
                'persona':  'a forgotten-history archaeologist and cultural detective of the Indian subcontinent',
                'headers':  ('⚙️ The Engineering', '⚔️ The History', '🔍 The Secret'),
                'points':   [
                    'A forgotten construction technique, engineering marvel, or architectural mystery of this site',
                    'A pivotal historical event, dynasty clash, or cultural turning point at this location',
                    'A hidden inscription, buried chamber, or overlooked detail that most visitors walk straight past',
                ],
            },
            'other': {
                'persona':  'a curious travel historian and local lore expert of India',
                'headers':  ('🔬 The Fact', '📖 The Story', '🤫 The Secret'),
                'points':   [
                    'A surprising scientific, historical, or geographical fact about this place',
                    'A local legend, folk tale, or unusual story connected to this destination',
                    'Something remarkable that most visitors never notice or know about',
                ],
            },
        }

        cfg = category_config.get(temple_category, category_config['other'])
        h1, h2, h3 = cfg['headers']
        p1, p2, p3 = cfg['points']

        prompt = f"""You are {cfg['persona']}.

Write a deeply engaging hidden lore passage about **{temple_name}** located in {temple_location}.
Category: {temple_category}
Known info: {temple_desc}

Write exactly 3 short paragraphs using these bold headers:
**{h1}** — {p1}
**{h2}** — {p2}
**{h3}** — {p3}

Rules:
- Keep each paragraph to 3-4 sentences maximum
- Tone: mysterious, poetic, and vivid — like a travel journal entry from a century ago
- Never use generic filler phrases like "this place is beautiful" or "visitors enjoy"
- Total response must be under 260 words
- Do not include any intro or outro — just the 3 paragraphs"""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return JsonResponse({'text': response.text})

    except Exception as e:
        import traceback
        print("LORE ERROR:", traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
def lore_page(request):
    temples = Temple.objects.order_by('-id')
    return render(request, 'core/lore.html', {'temples': temples})
def custom_404(request, exception):
    offline_path = os.path.join(os.path.dirname(__file__), 'static', 'offline.html')
    try:
        with open(offline_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = '<h1>Page not found</h1>'
    return HttpResponse(content, content_type='text/html', status=404)