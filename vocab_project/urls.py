"""
URL configuration for vocab_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from vocab import views as vocab_views  # 加入這行

urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ 首頁直接跳 home 頁面
    path('', vocab_views.home, name='home'),

    # ✅ 你自定義的 register 等視圖
    path('accounts/', include('accounts.urls')),

    # ✅ 查單字功能（vocab app）
    path('search/', vocab_views.search_word, name='search_word'),
    path('history/', vocab_views.history, name='history'),

    path('', include('vocab.urls')),

]





