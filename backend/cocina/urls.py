from django.urls import path

from .views import (
    PedidoCreateView,
    PedidoDetailView,
    CocinaColaView,
    ItemEstadoUpdateView,
    MesaListView,
    PlatoListView,
)

urlpatterns = [
    path('mesas/', MesaListView.as_view(), name='mesas-list'),
    path('platos/', PlatoListView.as_view(), name='platos-list'),
    path('pedidos/', PedidoCreateView.as_view(), name='pedidos-create'),
    path('pedidos/<int:pk>/', PedidoDetailView.as_view(), name='pedidos-detail'),
    path('cocina/cola/', CocinaColaView.as_view(), name='cocina-cola'),
    path('items/<int:pk>/estado/', ItemEstadoUpdateView.as_view(), name='item-estado-update'),
]
