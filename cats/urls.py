from cats.views import CatsViewSet
from django.urls import path

urlpatterns = [
    path('cats/', CatsViewSet.as_view({'get': 'list_cats'}), name='list_cats'),
    path('cats/reset/', CatsViewSet.as_view({'post': 'load_initial_cats'}), name='reset'),
    path('cats/<str:pk>/favorite/', CatsViewSet.as_view({'put': 'update_favorite'}), name='update_favorite'),
    path('cats/<str:pk>/', CatsViewSet.as_view({'put': 'update_cat'}), name='update_cat'),
]


