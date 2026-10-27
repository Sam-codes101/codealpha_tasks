from django.urls import path
from . import views

urlpatterns = [
    # Catalog
    path('', views.product_list_view, name='product_list'),
    path('product/<slug:slug>/', views.product_detail_view, name='product_detail'),

    # Cart
    path('cart/', views.cart_detail_view, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add_view, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update_view, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove_view, name='cart_remove'),

    # Checkout & Orders
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('orders/', views.order_history_view, name='order_history'),

    # Auth
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
