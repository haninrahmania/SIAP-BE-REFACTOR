from django.contrib import admin
from django.urls import path
from .views import klien_list, klien_create, klien_detail, klien_update, klien_delete

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', klien_list, name='klien_list'),
    path('create/', klien_create, name='klien_create'),
    path('<int:id>/', klien_detail, name='klien_detail'),
    path('<int:id>/update/', klien_update, name='klien_update'),
    path('<int:id>/delete/', klien_delete, name='klien_delete'),
]
