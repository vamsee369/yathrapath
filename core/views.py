from django.conf import settings
from django.shortcuts import render, redirect
from .forms import BlogForm  # we’ll create this next
from .models import Blog
from .models import Blog  # ← import the Blog model
from django.shortcuts import render, get_object_or_404
from .models import Temple


def home(request):
    temples = Temple.objects.order_by('-id')[:6]   # Only first 6 cards
    all_temples = Temple.objects.order_by('-id')    # All temples for map pins
    total_temples = Temple.objects.count()

    return render(request, 'core/home.html', {
        'temples': temples,
        'all_temples': all_temples,   # ✅ add this
        'total_temples': total_temples
    })


def temple_detail(request, id):
    temple = get_object_or_404(Temple, id=id)
    temples = Temple.objects.all()   # add this
    return render(request, 'core/temple_detail.html', {
        'temple': temple,
        'temples': temples
    })


def map_view(request):
    all_temples = Temple.objects.order_by('-id')

    return render(request, 'core/map.html', {
        'all_temples': all_temples
    })


def temples(request):
    temples = Temple.objects.order_by('-id')   # ✅ IMPORTANT
    return render(request, 'core/temples.html', {'temples': temples})


def blog(request):
    blogs = Blog.objects.all().order_by('-created_at')  # latest first
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
    return render(request, 'core/blog_detail.html', {'blog': blog})


def route_planner(request):

    temples = Temple.objects.all()

    return render(request, "core/route_planner.html", {
        "temples": temples,
        "ORS_KEY": settings.OPENROUTE_API_KEY
    })


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import PushSubscription

# ── Push Notification endpoints ──────────────────────

@csrf_exempt
@require_POST
def push_subscribe(request):
    """Save a browser push subscription."""
    try:
        data = json.loads(request.body)
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
    """Remove a push subscription."""
    try:
        data = json.loads(request.body)
        PushSubscription.objects.filter(endpoint=data.get('endpoint')).delete()
        return JsonResponse({'status': 'unsubscribed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def vapid_public_key(request):
    """Return the VAPID public key for the frontend."""
    from django.conf import settings
    return JsonResponse({'publicKey': getattr(settings, 'VAPID_PUBLIC_KEY', '')})


from django.templatetags.static import static
from django.http import HttpResponse
import os

def service_worker(request):
    """Serve the service worker JS from the site root for full-scope coverage."""
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'sw.js')
    try:
        with open(sw_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = '// sw not found'
    return HttpResponse(content, content_type='application/javascript')


def offline_page(request):
    """Serve the offline fallback page."""
    offline_path = os.path.join(os.path.dirname(__file__), 'static', 'offline.html')
    try:
        with open(offline_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        content = '<h1>Offline</h1>'
    return HttpResponse(content, content_type='text/html')
