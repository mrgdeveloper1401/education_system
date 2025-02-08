from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views


app_name = 'cart'
router = routers.DefaultRouter()
router.register(r'cart', views.CartViewSet, basename="cart")
cart_router = routers.NestedDefaultRouter(router, r'cart', lookup='cart')

cart_router.register(r'items', views.CartItemViewSet, basename="item")
urlpatterns = [
    path('', include(cart_router.urls)),
]
urlpatterns += router.urls
