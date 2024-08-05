from django.shortcuts import render
from django.views import generic
from django.db.models import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
from django.conf import settings
from cats.models import Cat, Breed

# Create your views here.
class CatsViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[AllowAny],
        url_path="list-cats",
    )
    def list_cats(self, request):
        skip = int(request.query_params.get('skip', 0))
        limit = int(request.query_params.get('limit', 12))
        favorite = request.query_params.get('favorite', None)
        breeds_filter = request.query_params.get('breeds', None)
        all_breeds = Breed.objects.all()

        # Prepare filters
        q_objects = Q()

        if favorite is not None:
            q_objects_fav = Q(favorite=(favorite.lower() == "true"))
            q_objects &= q_objects_fav # Add AND condition for favorite

        if breeds_filter is not None:
            breeds_ids = breeds_filter.split(",")
            q_objects_breeds = Q()
            filter_exists = False

            if "unknown" in breeds_ids:
                q_objects_breeds = Q(breeds__isnull=True)  # Add OR condition for breeds__isnull
                breeds_ids.remove("unknown")
                filter_exists = True

            if breeds_ids:
                if filter_exists:
                    q_objects_breeds |= Q(breeds__id__in=breeds_ids)  # Add OR condition for breeds__id__in
                else:
                    q_objects_breeds = Q(breeds__id__in=breeds_ids)  # Add OR condition for breeds__id__in

            q_objects &= q_objects_breeds


        # Fetch filtered cats
        cats = Cat.objects.filter(q_objects)[skip:skip+limit]
        count = Cat.objects.filter(q_objects).count()
        data = {
            'count': count,
            'items': [
                {
                    'id': cat.id,
                    'url': cat.url,
                    'width': cat.width,
                    'height': cat.height,
                    'name': cat.name,
                    'description': cat.description,
                    'favorite': cat.favorite,
                    'breeds': [
                        {
                            'id': breed.id,
                            'name': breed.name,
                            'temperament': breed.temperament,
                            'origin': breed.origin,
                            'description': breed.description,
                            'life_span': breed.life_span,
                        }
                        for breed in cat.breeds.all()
                    ]
                } for cat in cats
            ],
            'breeds': [
                {
                    'id': breed.id,
                    'name': breed.name,
                } for breed in all_breeds
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[AllowAny],
        url_path="reset",
    )
    def load_initial_cats(self, request):
        Cat.objects.all().delete()
        Breed.objects.all().delete()
        url = f"https://api.thecatapi.com/v1/images/search?limit=100&api_key={settings.CAT_API_KEY}"
        response = requests.get(url)
        data = response.json()
        items = []
        for cat in data:
            breeds = []
            for breed in cat["breeds"]:
                breed_data = {
                    "id": breed["id"],
                    "name": breed["name"],
                    "temperament": breed["temperament"],
                    "origin": breed["origin"],
                    "description": breed["description"],
                    "life_span": breed["life_span"],
                }
                breeds.append(breed_data)
                breed_obj = Breed(
                    id=breed["id"],
                    name=breed["name"],
                    temperament=breed["temperament"],
                    origin=breed["origin"],
                    description=breed["description"],
                    life_span=breed["life_span"],
                )
                existed_breed = Breed.objects.filter(id=breed["id"])
                if not existed_breed:
                    breed_obj.save()
            items.append({
                "id": cat["id"],
                "url": cat["url"],
                "width": cat["width"],
                "height": cat["height"],
                "name": "",
                "description": "",
                "breeds": breeds,
            })
            cat_obj = Cat(
                id=cat["id"],
                url=cat["url"],
                width=cat["width"],
                height=cat["height"],
            )
            existed_cat = Cat.objects.filter(id=cat["id"])
            if not existed_cat:
                cat_obj.save()
                for breed in breeds:
                    cat_obj.breeds.add(breed["id"])
        return Response(
            {
                "items": items
            },
            status=status.HTTP_200_OK,
        )
    @action(
        detail=True,
        methods=["put"],
        permission_classes=[AllowAny],
        url_path="favorite",
    )
    def update_favorite(self, request, pk):
        print(pk)
        cat = Cat.objects.get(pk=pk)
        cat.favorite = not cat.favorite
        cat.save()
        return Response(
            {
                "id": cat.id,
                "favorite": cat.favorite
            },
            status=status.HTTP_200_OK,
        )
    @action(
        detail=True,
        methods=["put"],
        permission_classes=[AllowAny],
        url_path="update-cat",
    )
    def update_cat(self, request, pk):
        data = request.data
        cat = Cat.objects.get(pk=pk)
        name = data.get("name", "")
        description = data.get("description", "")
        if name:
            cat.name = name
        if description:
            cat.description = description
        cat.save()
        return Response(
            {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description
            },
            status=status.HTTP_200_OK,
       )