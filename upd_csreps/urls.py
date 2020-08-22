"""upd_csreps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import include,path

urlpatterns = [
    ## path('admin/', admin.site.urls),
    path('admin/', include('main.admin_urls')),
    path('', include('main.urls')),
    path('codex/', include('codex.urls')),
    path('troubleshooter/', include('troubleshooter.urls')),
]

handler400 = 'main.views.wip'
handler403 = 'main.views.wip'
handler404 = 'main.views.wip'
handler500 = 'main.views.wip'