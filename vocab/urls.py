# vocab/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),          # "/" 首頁
    path("home/", views.home, name="home"),     # 備用 "/home/"

    path("search/", views.search_word, name="search_word"),
    path("history/", views.history, name="history"),
    path("delete/<int:pk>/", views.delete_history, name="delete_history"),
    path("clear/", views.clear_history, name="clear_history"),
    path("add/", views.add_word, name="add_word"),

    # 內建登入/登出/重設密碼等路由（提供 name='login'）
    path("healthz/", views.health, name="healthz"),
    path("accounts/register/", views.register, name="register"),

    # ✅ 先放這裡：覆蓋 Django 內建 logout（允許 GET/POST，直接轉登入）
    path("accounts/logout/", views.logout_and_redirect_login, name="logout"),

    # ⬇️ 最後才 include 內建帳號路由（login、password reset…）
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/activate/<uidb64>/<token>/", views.activate, name="activate"),

]
