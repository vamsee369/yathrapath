from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('temple/<int:id>/', views.temple_detail, name='temple_detail'),
    path('map/', views.map_view, name='map'),   # Map page
    path('temples/', views.temples, name='temples'),  # Temples page
    path('blog/', views.blog, name='blog'),     # Blog page
    path('blog/create/', views.blog_create,
         name='blog_create'),  # Blog create page
    path('blog/<int:id>/', views.blog_detail, name='blog_detail'),
    path('route-planner/', views.route_planner, name='route_planner'),
]
