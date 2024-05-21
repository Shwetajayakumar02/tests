# tests/factories.py

import factory
from factory.fuzzy import FuzzyChoice
from your_application.models import Product

class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('word')
    category = factory.Faker('word')
    available = FuzzyChoice(choices=[True, False])
    price = factory.Faker('random_number', digits=2)

# tests/test_models.py

import unittest
from your_application.models import Product, db

class TestProductModel(unittest.TestCase):
    
    def setUp(self):
        db.create_all()
        self.product = Product(name="Test Product", category="Test Category", available=True, price=10)
        db.session.add(self.product)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_read_product(self):
        product = Product.query.get(self.product.id)
        self.assertEqual(product.name, "Test Product")
    
    def test_update_product(self):
        self.product.name = "Updated Product"
        db.session.commit()
        product = Product.query.get(self.product.id)
        self.assertEqual(product.name, "Updated Product")
    
    def test_delete_product(self):
        db.session.delete(self.product)
        db.session.commit()
        product = Product.query.get(self.product.id)
        self.assertIsNone(product)
    
    def test_list_all_products(self):
        products = Product.query.all()
        self.assertGreaterEqual(len(products), 1)
    
    def test_find_by_name(self):
        product = Product.query.filter_by(name="Test Product").first()
        self.assertIsNotNone(product)
    
    def test_find_by_category(self):
        products = Product.query.filter_by(category="Test Category").all()
        self.assertGreaterEqual(len(products), 1)
    
    def test_find_by_availability(self):
        products = Product.query.filter_by(available=True).all()
        self.assertGreaterEqual(len(products), 1)


# tests/test_routes.py

import unittest
from your_application import app, db
from your_application.models import Product

class TestProductRoutes(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.product = Product(name="Test Product", category="Test Category", available=True, price=10)
        db.session.add(self.product)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_read_product(self):
        response = self.app.get(f'/products/{self.product.id}')
        self.assertEqual(response.status_code, 200)
    
    def test_update_product(self):
        response = self.app.put(f'/products/{self.product.id}', json={"name": "Updated Product"})
        self.assertEqual(response.status_code, 200)
    
    def test_delete_product(self):
        response = self.app.delete(f'/products/{self.product.id}')
        self.assertEqual(response.status_code, 204)
    
    def test_list_all_products(self):
        response = self.app.get('/products')
        self.assertEqual(response.status_code, 200)
    
    def test_list_by_name(self):
        response = self.app.get('/products', query_string={"name": "Test Product"})
        self.assertEqual(response.status_code, 200)
    
    def test_list_by_category(self):
        response = self.app.get('/products', query_string={"category": "Test Category"})
        self.assertEqual(response.status_code, 200)
    
    def test_list_by_availability(self):
        response = self.app.get('/products', query_string={"available": True})
        self.assertEqual(response.status_code, 200)



# service/routes.py

from flask import Flask, jsonify, request, abort
from your_application.models import Product, db

app = Flask(__name__)

@app.route('/products/<int:product_id>', methods=['GET'])
def read_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404)
    return jsonify(product.serialize())

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404)
    data = request.get_json()
    product.name = data.get('name', product.name)
    db.session.commit()
    return jsonify(product.serialize())

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404)
    db.session.delete(product)
    db.session.commit()
    return '', 204

@app.route('/products', methods=['GET'])
def list_all_products():
    products = Product.query.all()
    return jsonify([product.serialize() for product in products])

@app.route('/products', methods=['GET'])
def list_by_name():
    name = request.args.get('name')
    products = Product.query.filter_by(name=name).all()
    return jsonify([product.serialize() for product in products])

@app.route('/products', methods=['GET'])
def list_by_category():
    category = request.args.get('category')
    products = Product.query.filter_by(category=category).all()
    return jsonify([product.serialize() for product in products])

@app.route('/products', methods=['GET'])
def list_by_availability():
    available = request.args.get('available') == 'True'
    products = Product.query.filter_by(available=available).all()
    return jsonify([product.serialize() for product in products])



# features/steps/load_steps.py

from behave import given
from your_application.models import db, Product

@given('the following products')
def step_impl(context):
    for row in context.table:
        product = Product(name=row['name'], category=row['category'], available=row['available'] == 'True', price=row['price'])
        db.session.add(product)
    db.session.commit()




# features/products.feature

Feature: Product Management

  Scenario: Read a product
    Given the following products
      | name         | category      | available | price |
      | Test Product | Test Category | True      | 10    |
    When I visit the product "1"
    Then I should see the product name "Test Product"

  Scenario: Update a product
    Given the following products
      | name         | category      | available | price |
      | Test Product | Test Category | True      | 10    |
    When I update the product "1" with name "Updated Product"
    Then I should see the product name "Updated Product"

  Scenario: Delete a product
    Given the following products
      | name         | category      | available | price |
      | Test Product | Test Category | True      | 10    |
    When I delete the product "1"
    Then I should not see the product "1"

  Scenario: List all products
    Given the following products
      | name         | category      | available | price |
      | Test Product | Test Category | True      | 10    |
    When I list all products
    Then I should see the product name "Test Product"

  Scenario: Search products by name
    Given the following products
      | name         | category      | available | price |
      | Test Product | Test Category | True      | 10    |
    When I search for products by name "Test Product"





  




