from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('web.urls', namespace='web')),
    path('doctor/', include('doctor.urls', namespace='doctor')),
    path('patient/', include('patient.urls', namespace='patient')),
    path('user/', include('user.urls', namespace='user')),
    path('', include('inventory.urls', namespace='inventory')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
