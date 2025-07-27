from products.models import Product

from products.serializers import ProductSerializer
import pytest
import logging


logger = logging.getLogger(__name__)

PRODUCT_LIST_CREATE_URL = 'products:product-list-create'
PRODUCT_RETRIEVE_UPDATE_DESTROY_URL = 'products:product-detail'


@pytest.mark.django_db
def test_create_product(
    client
):
    url = PRODUCT_LIST_CREATE_URL
    data = {
        'name': 'Test Product',
        'quantity': 999,
    }
    response = client(
        url=url,
        method='post',
        data=data,
    )

    assert response.status_code == 201
    assert Product.objects.count() == 1

    product = Product.objects.first()
    assert response.data['id'] == product.id
    assert response.data['name'] == 'Test Product'
    assert response.data['name'] == product.name
    assert response.data['quantity'] == 999
    assert response.data['quantity'] == product.quantity
    assert response.data['unique_id'] == product.unique_id


@pytest.mark.django_db
def test_get_products(
    client,
    create_product,
):
    product_1 = create_product(name='product 1', quantity=1)
    product_2 = create_product(name='product 2', quantity=2)
    product_3 = create_product(name='product 3', quantity=3)

    url = PRODUCT_LIST_CREATE_URL
    response = client(url=url, method='get')
    assert response.status_code == 200
    assert len(response.data) == 3

    expected_data = ProductSerializer([product_1, product_2, product_3], many=True).data
    assert response.data == expected_data

@pytest.mark.django_db
def test_get_product(
    client,
    create_product,
):
    url = PRODUCT_RETRIEVE_UPDATE_DESTROY_URL
    product = create_product(name='Test Product', quantity=200)

    response = client(
        url=url,
        method='get',
        kwargs={'pk': product.id},
    )
    assert response.status_code == 200
    assert response.data['id'] == product.id
    assert response.data['name'] == 'Test Product'
    assert response.data['quantity'] == 200
    assert response.data['unique_id'] == str(product.unique_id)

@pytest.mark.django_db
def test_update_product(
    client,
    create_product,
):
    url = PRODUCT_RETRIEVE_UPDATE_DESTROY_URL
    product = create_product(name='Test Product', quantity=200)

    data = {
        'name': 'Updated Test Product',
        'quantity': 100
    }
    response = client(
        url=url,
        data=data,
        method='patch',
        kwargs={'pk': product.id},
    )

    assert response.status_code == 200
    assert response.data['id'] == product.id
    assert response.data['name'] == 'Updated Test Product'
    assert response.data['quantity'] == 100
    assert response.data['unique_id'] == str(product.unique_id)
