from shopping_list.conf.urls import url
from . import views


urlpatterns = [
    url('/', views.index)
]
