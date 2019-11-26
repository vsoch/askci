from .routers import urlpatterns as router_urls
from .hooks import urlpatterns as hook_urls

urlpatterns = router_urls + hook_urls
