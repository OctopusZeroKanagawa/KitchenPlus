from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Pedido, ItemPedido, Plato, Mesa
from .serializers import PedidoSerializer, ItemPedidoSerializer, MesaSerializer, PlatoSerializer


class MesaListView(generics.ListAPIView):
    queryset = Mesa.objects.all().order_by('numero')
    serializer_class = MesaSerializer


class PlatoListView(generics.ListAPIView):
    queryset = Plato.objects.all().order_by('nombre')
    serializer_class = PlatoSerializer


class PedidoCreateView(APIView):
    """POST /api/pedidos/ -> create Pedido with items in one request"""

    def post(self, request, *args, **kwargs):
        serializer = PedidoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items_payload = serializer.validated_data.pop('items_to_create', [])

        # Pre-validate item quantities are positive integers before touching DB
        for item in items_payload:
            if 'cantidad' not in item:
                return Response({'detail': 'Each item must include "cantidad".'}, status=status.HTTP_400_BAD_REQUEST)
            cantidad = item.get('cantidad')
            if not isinstance(cantidad, int) or cantidad <= 0:
                return Response({'detail': 'Field "cantidad" must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                pedido = Pedido.objects.create(**serializer.validated_data)
                created_items = []
                for item in items_payload:
                    plato_id = item.get('plato_id') or item.get('plato')
                    cantidad = item.get('cantidad')
                    plato = get_object_or_404(Plato, pk=plato_id)
                    precio = plato.precio
                    ip = ItemPedido(pedido=pedido, plato=plato, cantidad=cantidad, precio_unitario=precio)
                    # Ensure the created item uses the model constant for pending
                    # (avoids accidental hardcoded english values like 'pending')
                    ip.estado = ItemPedido.PENDIENTE
                    # validate model rules (queue limit, etc.) before saving
                    ip.full_clean()
                    ip.save()
                    created_items.append(ip)
        except DjangoValidationError as e:
            # full_clean raised — transaction will be rolled back
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        out = PedidoSerializer(pedido)
        return Response(out.data, status=status.HTTP_201_CREATED)


class PedidoDetailView(generics.RetrieveAPIView):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


class CocinaColaView(generics.ListAPIView):
    serializer_class = ItemPedidoSerializer

    def get_queryset(self):
        return ItemPedido.objects.filter(estado__in=[ItemPedido.PENDIENTE, ItemPedido.EN_PREPARACION]).select_related('pedido', 'plato').order_by('pedido__creado', 'creado')


class ItemEstadoUpdateView(APIView):
    """PATCH /api/items/<id>/estado/ -> update estado, calling full_clean()"""

    def patch(self, request, pk, *args, **kwargs):
        item = get_object_or_404(ItemPedido, pk=pk)
        estado = request.data.get('estado')
        if estado is None:
            return Response({'detail': 'Field "estado" is required.'}, status=status.HTTP_400_BAD_REQUEST)

        item.estado = estado
        try:
            item.full_clean()
            item.save()
        except DjangoValidationError as e:
            return Response({'detail': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ItemPedidoSerializer(item).data)
