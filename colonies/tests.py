from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cats.models import Cat

from .models import Colony
from .serializers import ColonySerializer


class ColonyModelTests(TestCase):
    def setUp(self):
        self.colony = Colony.objects.create(
            name='Parque Norte', address='Calle Mayor 1', city='Madrid'
        )

    def test_str_returns_name(self):
        self.assertEqual(str(self.colony), 'Parque Norte')

    def test_defaults(self):
        self.assertTrue(self.colony.is_active)
        self.assertEqual(self.colony.estimated_cat_count, 0)
        self.assertIsNone(self.colony.latitude)
        self.assertIsNone(self.colony.longitude)

    def test_colony_has_many_cats(self):
        Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)
        Cat.objects.create(name='Tom', sex=Cat.Sex.MALE, colony=self.colony)

        self.assertEqual(self.colony.cats.count(), 2)

    def test_deleting_colony_keeps_cats(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        self.colony.delete()

        cat.refresh_from_db()
        self.assertIsNone(cat.colony)


class ColonySerializerTests(TestCase):
    def test_required_fields(self):
        serializer = ColonySerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('address', serializer.errors)
        self.assertIn('city', serializer.errors)

    def test_invalid_latitude(self):
        serializer = ColonySerializer(
            data={'name': 'A', 'address': 'B', 'city': 'C', 'latitude': '91'}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)

    def test_negative_estimated_cat_count(self):
        serializer = ColonySerializer(
            data={'name': 'A', 'address': 'B', 'city': 'C', 'estimated_cat_count': -1}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('estimated_cat_count', serializer.errors)


class ColonyAPITests(APITestCase):
    def setUp(self):
        self.colony = Colony.objects.create(
            name='Parque Norte', address='Calle Mayor 1', city='Madrid'
        )
        self.list_url = reverse('colony-list')
        self.detail_url = reverse('colony-detail', args=[self.colony.pk])

    def test_list_includes_cat_count(self):
        Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['cat_count'], 1)

    def test_create(self):
        response = self.client.post(
            self.list_url,
            {
                'name': 'Puerto',
                'address': 'Muelle 3',
                'city': 'Bilbao',
                'estimated_cat_count': 12,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['cat_count'], 0)
        self.assertTrue(Colony.objects.filter(name='Puerto').exists())

    def test_retrieve(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Parque Norte')

    def test_partial_update(self):
        response = self.client.patch(self.detail_url, {'is_active': False})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.colony.refresh_from_db()
        self.assertFalse(self.colony.is_active)

    def test_delete(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Colony.objects.filter(pk=self.colony.pk).exists())

    def test_cats_action_lists_only_colony_cats(self):
        other = Colony.objects.create(name='Otra', address='X', city='Y')
        Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)
        Cat.objects.create(name='Tom', sex=Cat.Sex.MALE, colony=other)

        response = self.client.get(reverse('colony-cats', args=[self.colony.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Misi')

    def test_assign_cat_to_colony(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)

        response = self.client.patch(
            reverse('cat-detail', args=[cat.pk]), {'colony': self.colony.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.colony, self.colony)


class EstimatedCatCountSyncTests(TestCase):
    def setUp(self):
        self.colony = Colony.objects.create(
            name='Parque Norte', address='Calle Mayor 1', city='Madrid'
        )
        self.other = Colony.objects.create(name='Puerto', address='X', city='Y')

    def assertCount(self, colony, expected):
        colony.refresh_from_db()
        self.assertEqual(colony.estimated_cat_count, expected)

    def test_creating_cat_in_colony_increments(self):
        Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        self.assertCount(self.colony, 1)

    def test_creating_cat_without_colony_changes_nothing(self):
        Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)

        self.assertCount(self.colony, 0)

    def test_assigning_cat_increments(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)

        cat.colony = self.colony
        cat.save()

        self.assertCount(self.colony, 1)

    def test_removing_cat_from_colony_decrements(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        cat.colony = None
        cat.save()

        self.assertCount(self.colony, 0)

    def test_moving_cat_updates_both_colonies(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        cat.colony = self.other
        cat.save()

        self.assertCount(self.colony, 0)
        self.assertCount(self.other, 1)

    def test_saving_without_colony_change_keeps_count(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        cat.name = 'Misifú'
        cat.save()

        self.assertCount(self.colony, 1)

    def test_deleting_cat_decrements(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        cat.delete()

        self.assertCount(self.colony, 0)

    def test_count_never_goes_below_zero(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)
        Colony.objects.filter(pk=self.colony.pk).update(estimated_cat_count=0)

        cat.delete()

        self.assertCount(self.colony, 0)

    def test_estimate_keeps_unregistered_cats(self):
        Colony.objects.filter(pk=self.colony.pk).update(estimated_cat_count=10)

        Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE, colony=self.colony)

        self.assertCount(self.colony, 11)
