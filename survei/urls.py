from django.urls import path
from .views import *

urlpatterns=[
    path("get-list-survei",get_list_survei),
    path("get-survei-detail/<str:id>/",get_survei_detail),
    path("add-survei/",add_survei),
    path("update-survei/<str:id>/",update_survei),
    path("delete-survei/<str:id>/",delete_survei),
    path('init_data/', survei_init_data, name='survei-init-data'),
    # path('count-by-region/', get_survei_count_by_region),
    # path('count-dashboard/', get_survei_count_dashboard),
]