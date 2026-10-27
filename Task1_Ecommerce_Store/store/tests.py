from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from store.models import Category, Product, Order, OrderItem
from store.cart import Cart


class EcommerceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Tech Gear', slug='tech-gear', icon='🎧')
        self.product = Product.objects.create(
            category=self.category,
            name='Noise Cancelling Headphones',
            slug='noise-cancelling-headphones',
            description='Crisp audio and punchy bass.',
            price=Decimal('5000.00'),
            discount_price=Decimal('4000.00'),
            image_url='https://example.com/headphones.jpg',
            stock=10
        )
        self.user = User.objects.create_user(username='customer1', email='customer@test.com', password='password123')

    def test_catalog_and_detail_views(self):
        """Test product list and detail rendering."""
        res_list = self.client.get(reverse('product_list'))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, 'Noise Cancelling Headphones')

        res_detail = self.client.get(reverse('product_detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, 'Noise Cancelling Headphones')

    def test_cart_operations(self):
        """Test adding, updating, and removing items from the cart."""
        # Add to cart
        res_add = self.client.post(reverse('cart_add', kwargs={'product_id': self.product.id}), {'quantity': 2})
        self.assertEqual(res_add.status_code, 302)

        session = self.client.session
        self.assertIn(str(self.product.id), session['cart'])
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 2)

        # Update cart quantity
        res_update = self.client.post(reverse('cart_update', kwargs={'product_id': self.product.id}), {'quantity': 3})
        self.assertEqual(res_update.status_code, 302)
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 3)

        # Remove item
        res_remove = self.client.post(reverse('cart_remove', kwargs={'product_id': self.product.id}))
        self.assertEqual(res_remove.status_code, 302)
        session = self.client.session
        self.assertNotIn(str(self.product.id), session['cart'])

    def test_order_checkout_flow(self):
        """Test complete checkout and order generation."""
        # Add product to cart
        self.client.post(reverse('cart_add', kwargs={'product_id': self.product.id}), {'quantity': 1})

        # Checkout post
        checkout_data = {
            'full_name': 'Alex Rivera',
            'email': 'alex@test.com',
            'phone': '9876543210',
            'address': '123 Tech Park',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'postal_code': '560001',
            'payment_method': 'Cash on Delivery',
        }
        res_checkout = self.client.post(reverse('checkout'), checkout_data)
        self.assertEqual(res_checkout.status_code, 302)

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.full_name, 'Alex Rivera')
        self.assertEqual(order.items.count(), 1)

        # Verify stock decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)

    def test_user_signup_and_login(self):
        """Test customer registration and login."""
        res_signup = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'new@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        self.assertEqual(res_signup.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
