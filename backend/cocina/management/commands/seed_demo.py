from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from cocina.models import Ingrediente, Mesa, Plato, RecetaPlato


class Command(BaseCommand):
    help = 'Seeds the development database with realistic demo data for the kitchen flow.'

    @transaction.atomic
    def handle(self, *args, **options):
        RecetaPlato.objects.all().delete()
        Plato.objects.all().delete()
        Ingrediente.objects.all().delete()
        Mesa.objects.all().delete()

        mesas = [
            (1, 2),
            (2, 4),
            (3, 4),
            (4, 6),
        ]
        for numero, capacidad in mesas:
            Mesa.objects.create(numero=numero, capacidad=capacidad)

        ingredientes = {
            'Carne de res': {'unidad': 'g', 'cantidad': Decimal('5000')},
            'Pollo': {'unidad': 'g', 'cantidad': Decimal('3000')},
            'Arroz': {'unidad': 'g', 'cantidad': Decimal('10000')},
            'Camarones': {'unidad': 'g', 'cantidad': Decimal('0')},
        }
        ingrediente_obj = {}
        for nombre, data in ingredientes.items():
            ingrediente_obj[nombre] = Ingrediente.objects.create(
                nombre=nombre,
                unidad_medida=data['unidad'],
                cantidad_disponible=data['cantidad'],
            )

        platos = [
            ('Lomo Saltado', Decimal('34.90'), {
                'Carne de res': Decimal('250'),
                'Arroz': Decimal('300'),
            }),
            ('Pollo al ají', Decimal('28.50'), {
                'Pollo': Decimal('220'),
                'Arroz': Decimal('250'),
            }),
            ('Causa a la huancaína', Decimal('26.00'), {
                'Pollo': Decimal('180'),
                'Arroz': Decimal('200'),
            }),
            ('Paella de camarones', Decimal('39.90'), {
                'Camarones': Decimal('300'),
                'Arroz': Decimal('400'),
            }),
        ]

        for nombre, precio, receta in platos:
            plato = Plato.objects.create(nombre=nombre, precio=precio)
            for ing_nombre, cantidad in receta.items():
                RecetaPlato.objects.create(
                    plato=plato,
                    ingrediente=ingrediente_obj[ing_nombre],
                    cantidad_requerida=cantidad,
                )

        Plato.objects.create(nombre='Ensalada Mixta', precio=Decimal('18.50'))

        self.stdout.write(self.style.SUCCESS('Demo seed created successfully.'))
        self.stdout.write('Mesas: 4')
        self.stdout.write('Ingredientes: 4')
        self.stdout.write('Platos: 5')
