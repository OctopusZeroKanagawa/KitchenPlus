from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    unidad_medida = models.CharField(max_length=50)
    cantidad_disponible = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0.000'))

    def __str__(self):
        return self.nombre


class Plato(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    ingredientes = models.ManyToManyField(Ingrediente, through='RecetaPlato', related_name='platos')

    def __str__(self):
        return self.nombre

    def disponible(self):
        for rp in self.recetaplato_set.all():
            if rp.ingrediente.cantidad_disponible < rp.cantidad_requerida:
                return False
        return True


class RecetaPlato(models.Model):
    plato = models.ForeignKey(Plato, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.PROTECT)
    cantidad_requerida = models.DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        unique_together = ('plato', 'ingrediente')

    def __str__(self):
        return f"{self.plato} -> {self.ingrediente}: {self.cantidad_requerida}"


class Mesa(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    capacidad = models.PositiveIntegerField()

    @property
    def total_pendiente(self):
        total = sum((pedido.subtotal for pedido in self.pedidos.filter(pagado=False)), Decimal('0.00'))
        return total

    def __str__(self):
        return f"Mesa {self.numero}"


class Pedido(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='pedidos')
    pagado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.numero}"

    @property
    def subtotal(self):
        items = self.items.all()
        total = sum((i.precio_unitario * i.cantidad) for i in items)
        return total


class MovimientoInventario(models.Model):
    ENTRADA = 'E'
    SALIDA = 'S'
    TIPO_CHOICES = ((ENTRADA, 'Entrada'), (SALIDA, 'Salida'))

    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES)
    cantidad = models.DecimalField(max_digits=12, decimal_places=3)
    fecha = models.DateTimeField(default=timezone.now)
    nota = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_display()} {self.cantidad} {self.ingrediente}"

    def apply_delta(self, delta):
        new = self.ingrediente.cantidad_disponible + Decimal(delta)
        if new < 0:
            raise ValidationError('No hay suficiente stock para esta operación de inventario.')
        self.ingrediente.cantidad_disponible = new
        self.ingrediente.save()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                old = MovimientoInventario.objects.select_for_update().get(pk=self.pk)
                # revert old
                revert = old.cantidad if old.tipo == self.ENTRADA else -old.cantidad
                self.ingrediente = self.ingrediente  # ensure FK instance available
                # revert previous movement
                self.ingrediente.refresh_from_db()
                self.ingrediente.cantidad_disponible -= revert
                if self.ingrediente.cantidad_disponible < 0:
                    raise ValidationError('Actualizar movimiento provocaría stock negativo al revertir anterior.')
                self.ingrediente.save()
            # apply new
            delta = self.cantidad if self.tipo == self.ENTRADA else -self.cantidad
            self.ingrediente.refresh_from_db()
            if (self.ingrediente.cantidad_disponible + Decimal(delta)) < 0:
                raise ValidationError('No hay suficiente stock para esta operación de inventario.')
            super().save(*args, **kwargs)
            # persist the change
            self.ingrediente.cantidad_disponible += Decimal(delta)
            self.ingrediente.save()

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            # revert this movement
            delta = -self.cantidad if self.tipo == self.ENTRADA else self.cantidad
            self.ingrediente.refresh_from_db()
            if (self.ingrediente.cantidad_disponible + Decimal(delta)) < 0:
                raise ValidationError('Eliminar este movimiento provocaría stock negativo.')
            self.ingrediente.cantidad_disponible += Decimal(delta)
            self.ingrediente.save()
            super().delete(*args, **kwargs)


class ItemPedido(models.Model):
    PENDIENTE = 'pendiente'
    EN_PREPARACION = 'en_preparacion'
    LISTO = 'listo'
    ENTREGADO = 'entregado'
    CANCELADO = 'cancelado'

    ESTADO_CHOICES = (
        (PENDIENTE, 'Pendiente'),
        (EN_PREPARACION, 'En preparación'),
        (LISTO, 'Listo'),
        (ENTREGADO, 'Entregado'),
        (CANCELADO, 'Cancelado'),
    )

    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    plato = models.ForeignKey(Plato, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=PENDIENTE)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cantidad} x {self.plato.nombre} ({self.estado})"

    def clean(self):
        # Regla: no se puede cancelar si ya no está en pendiente
        if self.pk:
            old = ItemPedido.objects.get(pk=self.pk)
            if self.estado == self.CANCELADO and old.estado != self.PENDIENTE:
                raise ValidationError('No se puede cancelar un ítem que la cocina ya empezó a preparar.')

        # Validar límite de cola global (pendientes + en_preparacion)
        qs = ItemPedido.objects.filter(estado__in=[self.PENDIENTE, self.EN_PREPARACION])
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        current_count = qs.count()
        will_count = current_count + (1 if self.estado in [self.PENDIENTE, self.EN_PREPARACION] else 0)
        if will_count > 100:
            raise ValidationError('La cola de cocina no puede superar 100 ítems simultáneos.')

    def save(self, *args, **kwargs):
        self.full_clean()
        # rellenar precio_unitario por defecto al crear
        if not self.precio_unitario:
            self.precio_unitario = self.plato.precio

        # detectar cambio de estado para consumir inventario cuando pase a EN_PREPARACION
        old_estado = None
        if self.pk:
            try:
                old_estado = ItemPedido.objects.get(pk=self.pk).estado
            except ItemPedido.DoesNotExist:
                old_estado = None

        super().save(*args, **kwargs)

        if old_estado != self.EN_PREPARACION and self.estado == self.EN_PREPARACION:
            # crear movimientos de salida por cada ingrediente de la receta
            for rp in self.plato.recetaplato_set.select_related('ingrediente').all():
                cantidad_total = rp.cantidad_requerida * Decimal(self.cantidad)
                MovimientoInventario.objects.create(
                    ingrediente=rp.ingrediente,
                    tipo=MovimientoInventario.SALIDA,
                    cantidad=cantidad_total,
                    nota=f'Consumo por ItemPedido {self.pk}'
                )


class Pago(models.Model):
    mesa = models.ForeignKey(Mesa, on_delete=models.CASCADE, related_name='pagos')
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago {self.id} - Mesa {self.mesa.numero}: {self.monto}"
