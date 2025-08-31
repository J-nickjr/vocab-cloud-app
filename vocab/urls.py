from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),                      # ⬅️ "/" 首頁
    path("home/", views.home, name="home"),                 # 備用 "/home/"
    path("search/", views.search_word, name="search_word"),
    path("history/", views.history, name="history"),
    path("delete/<int:pk>/", views.delete_history, name="delete_history"),
    path("clear/", views.clear_history, name="clear_history"),
    path("add/", views.add_word, name="add_word"),

]
