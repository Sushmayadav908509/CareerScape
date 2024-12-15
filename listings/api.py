 #JobHub\listings\api.py
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from .views import ScrapedDataList

class CustomDefaultRouter(DefaultRouter):
    def get_default_base_name(self, viewset):
        return "custom-default"
    
class CustomDefaultViewset(viewsets.ViewSet):
    queryset = ScrapedDataList.queryset

router = CustomDefaultRouter()
router.register("default", CustomDefaultViewset, basename="custom-default")