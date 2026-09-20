from decimal import Decimal
from rest_framework import serializers

from .models import Mesa, Pedido, ItemPedido, Plato, Pago


class MesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mesa
        fields = ('id', 'numero', 'capacidad')


class ItemPedidoSerializer(serializers.ModelSerializer):
    plato_nombre = serializers.CharField(source='plato.nombre', read_only=True)
    mesa_numero = serializers.IntegerField(source='pedido.mesa.numero', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ('id', 'pedido', 'plato', 'plato_nombre', 'mesa_numero', 'cantidad', 'precio_unitario', 'estado', 'creado')
        read_only_fields = ('precio_unitario', 'creado', 'plato_nombre', 'mesa_numero')


class PlatoSerializer(serializers.ModelSerializer):
    disponible = serializers.SerializerMethodField()

    class Meta:
        model = Plato
        fields = ('id', 'nombre', 'precio', 'disponible')

    def get_disponible(self, obj):
        return bool(obj.disponible)


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


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ('id', 'mesa', 'pedido', 'monto', 'fecha')
        read_only_fields = ('id', 'fecha')


class PedidoCuentaSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = ('id', 'subtotal')

    def get_subtotal(self, obj):
        return obj.subtotal


class MesaCuentaSerializer(serializers.ModelSerializer):
    pedidos = serializers.SerializerMethodField()
    total_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = Mesa
        fields = ('numero', 'pedidos', 'total_pendiente')

    def get_pedidos(self, obj):
        pedidos = obj.pedidos.filter(pagado=False).order_by('creado')
        return PedidoCuentaSerializer(pedidos, many=True).data

    def get_total_pendiente(self, obj):
        return obj.total_pendiente
