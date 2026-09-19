from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from cocina.models import Mesa, Plato, ItemPedido
import time


class CocinaAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.mesa = Mesa.objects.create(numero=1, capacidad=4)
        self.plato = Plato.objects.create(nombre='Prueba', precio='9.90')

    def _create_pedido(self, cantidad=1):
        payload = {
            'mesa': self.mesa.id,
            'items_to_create': [
                {'plato_id': self.plato.id, 'cantidad': cantidad}
            ]
        }
        return self.client.post('/api/pedidos/', payload, format='json')

    def test_crear_pedido_ok(self):
        resp = self._create_pedido()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.json()
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)
        estado = data['items'][0]['estado']
        self.assertEqual(estado, ItemPedido.PENDIENTE)

    def test_no_se_puede_cancelar_item_en_preparacion(self):
        # create
        resp = self._create_pedido()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.json()['items'][0]['id']

        # move to en_preparacion
        r = self.client.patch(f'/api/items/{item_id}/estado/', {'estado': ItemPedido.EN_PREPARACION}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # try cancel -> should be 400
        r2 = self.client.patch(f'/api/items/{item_id}/estado/', {'estado': ItemPedido.CANCELADO}, format='json')
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)

        # verify DB still en_preparacion
        item = ItemPedido.objects.get(pk=item_id)
        self.assertEqual(item.estado, ItemPedido.EN_PREPARACION)

    def test_si_se_puede_cancelar_item_pendiente(self):
        resp = self._create_pedido()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        item_id = resp.json()['items'][0]['id']

        r = self.client.patch(f'/api/items/{item_id}/estado/', {'estado': ItemPedido.CANCELADO}, format='json')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        item = ItemPedido.objects.get(pk=item_id)
        self.assertEqual(item.estado, ItemPedido.CANCELADO)

    def test_limite_cola_cocina(self):
        # create 100 items
        for i in range(100):
            r = self._create_pedido()
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        # confirm there are 100 pending/in_preparacion items
        count = ItemPedido.objects.filter(estado__in=[ItemPedido.PENDIENTE, ItemPedido.EN_PREPARACION]).count()
        self.assertEqual(count, 100)

        # attempt 101st -> should return 400
        r101 = self._create_pedido()
        self.assertEqual(r101.status_code, status.HTTP_400_BAD_REQUEST)

        count_after = ItemPedido.objects.filter(estado__in=[ItemPedido.PENDIENTE, ItemPedido.EN_PREPARACION]).count()
        self.assertEqual(count_after, 100)

    def test_cola_ordenada_por_antiguedad(self):
        ids = []
        for _ in range(3):
            r = self._create_pedido()
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            ids.append(r.json()['items'][0]['id'])
            time.sleep(0.01)

        q = self.client.get('/api/cocina/cola/')
        self.assertEqual(q.status_code, status.HTTP_200_OK)
        data = q.json()
        returned_ids = [it['id'] for it in data]
        # earliest first
        self.assertEqual(returned_ids[:3], ids)
