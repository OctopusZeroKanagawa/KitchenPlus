from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ingrediente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('unidad_medida', models.CharField(max_length=50)),
                ('cantidad_disponible', models.DecimalField(decimal_places=3, default='0.000', max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='Plato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200, unique=True)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Mesa',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.PositiveIntegerField(unique=True)),
                ('capacidad', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pagado', models.BooleanField(default=False)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('mesa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='cocina.Mesa')),
            ],
        ),
        migrations.CreateModel(
            name='MovimientoInventario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('E', 'Entrada'), ('S', 'Salida')], max_length=1)),
                ('cantidad', models.DecimalField(decimal_places=3, max_digits=12)),
                ('fecha', models.DateTimeField()),
                ('nota', models.CharField(blank=True, max_length=255, null=True)),
                ('ingrediente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='movimientos', to='cocina.Ingrediente')),
            ],
        ),
        migrations.CreateModel(
            name='RecetaPlato',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_requerida', models.DecimalField(decimal_places=3, max_digits=10)),
                ('ingrediente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cocina.Ingrediente')),
                ('plato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cocina.Plato')),
            ],
            options={
                'unique_together': {('plato', 'ingrediente')},
            },
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('en_preparacion', 'En preparación'), ('listo', 'Listo'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20)),
                ('creado', models.DateTimeField(auto_now_add=True)),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='cocina.Pedido')),
                ('plato', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='cocina.Plato')),
            ],
        ),
        migrations.CreateModel(
            name='Pago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monto', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('mesa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='cocina.Mesa')),
                ('pedido', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pagos', to='cocina.Pedido')),
            ],
        ),
        migrations.AddField(
            model_name='plato',
            name='ingredientes',
            field=models.ManyToManyField(related_name='platos', through='cocina.RecetaPlato', to='cocina.Ingrediente'),
        ),
    ]
