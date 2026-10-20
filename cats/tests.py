from datetime import date

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cat
from .serializers import CatSerializer


class CatModelTests(TestCase):
    def test_str_returns_name(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)

        self.assertEqual(str(cat), 'Misi')

    def test_defaults(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)

        self.assertFalse(cat.is_adopted)
        self.assertEqual(cat.breed, '')
        self.assertEqual(cat.description, '')
        self.assertIsNone(cat.birth_date)
        self.assertIsNotNone(cat.created_at)
        self.assertIsNotNone(cat.updated_at)

    def test_ordering_is_newest_first(self):
        first = Cat.objects.create(name='First', sex=Cat.Sex.MALE)
        second = Cat.objects.create(name='Second', sex=Cat.Sex.FEMALE)

        self.assertEqual(list(Cat.objects.all()), [second, first])

    def test_updated_at_changes_on_save(self):
        cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)
        previous = cat.updated_at

        cat.name = 'Misifú'
        cat.save()

        self.assertGreater(cat.updated_at, previous)


class CatSerializerTests(TestCase):
    def test_valid_data(self):
        serializer = CatSerializer(
            data={'name': 'Misi', 'sex': 'F', 'birth_date': '2024-05-01'}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        cat = serializer.save()
        self.assertEqual(cat.birth_date, date(2024, 5, 1))

    def test_name_and_sex_are_required(self):
        serializer = CatSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)
        self.assertIn('sex', serializer.errors)

    def test_invalid_sex_choice(self):
        serializer = CatSerializer(data={'name': 'Misi', 'sex': 'X'})

        self.assertFalse(serializer.is_valid())
        self.assertIn('sex', serializer.errors)

    def test_name_max_length(self):
        serializer = CatSerializer(data={'name': 'a' * 101, 'sex': 'F'})

        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_timestamps_are_read_only(self):
        serializer = CatSerializer(
            data={
                'name': 'Misi',
                'sex': 'F',
                'created_at': '2000-01-01T00:00:00Z',
                'updated_at': '2000-01-01T00:00:00Z',
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn('created_at', serializer.validated_data)
        self.assertNotIn('updated_at', serializer.validated_data)


class CatAPITests(APITestCase):
    def setUp(self):
        self.cat = Cat.objects.create(name='Misi', sex=Cat.Sex.FEMALE)
        self.list_url = reverse('cat-list')
        self.detail_url = reverse('cat-detail', args=[self.cat.pk])

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], 'Misi')

    def test_list_is_paginated(self):
        Cat.objects.bulk_create(
            Cat(name=f'Cat {i}', sex=Cat.Sex.MALE) for i in range(25)
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.data['count'], 26)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])

    def test_create(self):
        response = self.client.post(
            self.list_url, {'name': 'Garfield', 'sex': 'M', 'breed': 'Persian'}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Garfield')
        self.assertTrue(Cat.objects.filter(name='Garfield').exists())

    def test_create_invalid(self):
        response = self.client.post(self.list_url, {'name': ''})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('sex', response.data)
        self.assertEqual(Cat.objects.count(), 1)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.cat.pk)
        self.assertEqual(response.data['name'], 'Misi')

    def test_retrieve_not_found(self):
        response = self.client.get(reverse('cat-detail', args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        response = self.client.put(
            self.detail_url, {'name': 'Misi', 'sex': 'F', 'is_adopted': True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cat.refresh_from_db()
        self.assertTrue(self.cat.is_adopted)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url, {'breed': 'Siamese'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.breed, 'Siamese')
        self.assertEqual(self.cat.name, 'Misi')

    def test_delete(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cat.objects.filter(pk=self.cat.pk).exists())
