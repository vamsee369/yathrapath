from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('temple/<int:id>/', views.temple_detail, name='temple_detail'),
    path('map/', views.map_view, name='map'),
    path('temples/', views.temples, name='temples'),
    path('blog/', views.blog, name='blog'),
    path('blog/create/', views.blog_create, name='blog_create'),
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('route-planner/', views.route_planner, name='route_planner'),

    # Service worker (must be at root scope)
    path('sw.js',      views.service_worker, name='service_worker'),
    path('offline.html', views.offline_page, name='offline_page'),

    # Push notification endpoints
    path('push/subscribe/',   views.push_subscribe,   name='push_subscribe'),
    path('push/unsubscribe/', views.push_unsubscribe, name='push_unsubscribe'),
    path('push/vapid-key/',   views.vapid_public_key, name='vapid_public_key'),
]