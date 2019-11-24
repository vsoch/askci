from .base import urlpatterns as baseurls
from .search import urlpatterns as searchurls

urlpatterns = baseurls + searchurls
