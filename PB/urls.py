"""PB URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.template.defaulttags import url
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="309 API",
        default_version='1.0.0',
        description='API document of the APP'
    ),
    public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),
    path('studio/', include('studio.urls')),
    path('account/', include('account.urls')),
    path('swagger/schema/', schema_view.with_ui('swagger', cache_timeout=0),
         name="swagger-schema")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
