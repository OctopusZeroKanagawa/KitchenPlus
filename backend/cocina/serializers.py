from decimal import Decimal
from rest_framework import serializers

from .models import Mesa, Pedido, ItemPedido, Plato


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ('id', 'numero', 'capacidad')


class ItemPedidoSerializer(serializers.ModelSerializer):
    plato_nombre = serializers.CharField(source='plato.nombre', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ('id', 'pedido', 'plato', 'plato_nombre', 'cantidad', 'precio_unitario', 'estado', 'creado')
        read_only_fields = ('precio_unitario', 'creado', 'plato_nombre')


class PlatoSerializer(serializers.ModelSerializer):
    disponible = serializers.SerializerMethodField()

    class Meta:
        model = Plato
        fields = ('id', 'nombre', 'precio', 'disponible')

    def get_disponible(self, obj):
        return obj.disponible() if callable(obj.disponible) else bool(obj.disponible)


class PedidoSerializer(serializers.ModelSerializer):
    items = ItemPedidoSerializer(many=True, read_only=True)
    items_to_create = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ('id', 'mesa', 'pagado', 'creado', 'items', 'items_to_create', 'subtotal')
        read_only_fields = ('creado', 'items', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal
