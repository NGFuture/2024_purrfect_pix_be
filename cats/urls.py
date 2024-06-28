from cats.views import CatsViewSet
from django.urls import path

urlpatterns = [
    path('cats/', CatsViewSet.as_view({'get': 'list_cats'}), name='list_cats'),
    path('cats/load-cats/', CatsViewSet.as_view({'get': 'load_initial_cats'}), name='load_cats'),
    path('cats/favorite/', CatsViewSet.as_view({'put': 'favorite_cats'}), name='favorite_cats'),
]


