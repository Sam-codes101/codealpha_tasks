from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds the database with realistic e-commerce categories and products.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting NovaCart seed data generator...")

        # Create demo superuser
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@novacart.com', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Create demo customer
        customer, _ = User.objects.get_or_create(
            username='alex_customer',
            defaults={'email': 'alex@example.com', 'first_name': 'Alex', 'last_name': 'Rivera'}
        )
        customer.set_password('password123')
        customer.save()

        # Categories
        cat_data = [
            {'name': 'Electronics & Audio', 'slug': 'electronics', 'icon': '🎧', 'desc': 'Premium headphones, audio gear, and modern desk gadgets.'},
            {'name': 'Footwear & Sneakers', 'slug': 'footwear', 'icon': '👟', 'desc': 'Streetwear sneakers, runners, and everyday style.'},
            {'name': 'Computers & Accessories', 'slug': 'computers', 'icon': '💻', 'desc': 'Mechanical keyboards, ergonomics, and productivity tools.'},
            {'name': 'Apparel & Streetwear', 'slug': 'apparel', 'icon': '👕', 'desc': 'Heavyweight hoodies, oversized tees, and minimal basics.'},
            {'name': 'Bags & Everyday Carry', 'slug': 'bags', 'icon': '🎒', 'desc': 'Weatherproof backpacks, tech organizers, and slings.'},
        ]

        categories = {}
        for c in cat_data:
            cat_obj, _ = Category.objects.get_or_create(
                slug=c['slug'],
                defaults={'name': c['name'], 'icon': c['icon'], 'description': c['desc']}
            )
            categories[c['slug']] = cat_obj

        # Products
        products_data = [
            {
                'category': 'electronics',
                'name': 'Aura Sound ANC Wireless Headphones',
                'slug': 'aura-sound-anc-headphones',
                'description': 'Active noise-cancelling over-ear headphones with 40-hour battery life, spatial audio, and memory foam ear cushions. Perfect for campus study sessions and travel.',
                'price': Decimal('8999.00'),
                'discount_price': Decimal('6999.00'),
                'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
                'stock': 35,
                'rating': Decimal('4.9'),
                'reviews_count': 128,
                'is_featured': True,
            },
            {
                'category': 'electronics',
                'name': 'Nova Studio Desk Mic with RGB',
                'slug': 'nova-studio-desk-mic',
                'description': 'Cardioid condenser microphone with customizable RGB lighting ring, tap-to-mute sensor, and zero-latency headphone monitoring.',
                'price': Decimal('4499.00'),
                'discount_price': Decimal('3499.00'),
                'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&q=80',
                'stock': 20,
                'rating': Decimal('4.7'),
                'reviews_count': 64,
                'is_featured': False,
            },
            {
                'category': 'footwear',
                'name': 'Pulse Wave Chunky Retro Sneakers',
                'slug': 'pulse-wave-chunky-sneakers',
                'description': '90s-inspired street aesthetic with ultra-cushioned EVA foam midsoles, breathable mesh accents, and high-traction rubber outsoles.',
                'price': Decimal('5999.00'),
                'discount_price': Decimal('4299.00'),
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80',
                'stock': 18,
                'rating': Decimal('4.8'),
                'reviews_count': 92,
                'is_featured': True,
            },
            {
                'category': 'footwear',
                'name': 'Minimalist Monochrome High-Tops',
                'slug': 'minimalist-monochrome-high-tops',
                'description': 'Clean silhouette canvas high-top sneakers with vulcanized rubber sole and reinforced toe cap. Effortless pairing with denim or streetwear.',
                'price': Decimal('3499.00'),
                'discount_price': None,
                'image_url': 'https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=800&q=80',
                'stock': 40,
                'rating': Decimal('4.6'),
                'reviews_count': 45,
                'is_featured': False,
            },
            {
                'category': 'computers',
                'name': 'KeyVibe Custom 75% Mechanical Keyboard',
                'slug': 'keyvibe-custom-mechanical-keyboard',
                'description': 'Hot-swappable tactile switches, frosted polycarbonate casing, south-facing RGB, and factory lubed stabilizers. Bluetooth 5.2 and USB-C.',
                'price': Decimal('7499.00'),
                'discount_price': Decimal('6299.00'),
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80',
                'stock': 25,
                'rating': Decimal('5.0'),
                'reviews_count': 110,
                'is_featured': True,
            },
            {
                'category': 'computers',
                'name': 'ErgoGlider Wireless Precision Mouse',
                'slug': 'ergoglider-wireless-mouse',
                'description': 'Ergonomic vertical design reducing wrist fatigue by 60%, dual Bluetooth/2.4GHz connectivity, silent click switches, and USB-C charging.',
                'price': Decimal('2999.00'),
                'discount_price': Decimal('2199.00'),
                'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&q=80',
                'stock': 50,
                'rating': Decimal('4.7'),
                'reviews_count': 78,
                'is_featured': False,
            },
            {
                'category': 'apparel',
                'name': 'Heavyweight 450GSM Acid Wash Hoodie',
                'slug': 'heavyweight-acid-wash-hoodie',
                'description': 'Ultra-dense 100% French terry cotton with custom vintage acid wash treatment. Oversized boxy fit, dropped shoulders, and double-lined hood.',
                'price': Decimal('3999.00'),
                'discount_price': Decimal('2999.00'),
                'image_url': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&q=80',
                'stock': 30,
                'rating': Decimal('4.9'),
                'reviews_count': 84,
                'is_featured': True,
            },
            {
                'category': 'bags',
                'name': 'Transit Pro Weatherproof 26L Backpack',
                'slug': 'transit-pro-weatherproof-backpack',
                'description': 'Ballistic nylon shell with water-sealed YKK zippers, dedicated padded 16-inch laptop compartment, luggage pass-through strap, and magnetic buckle.',
                'price': Decimal('4999.00'),
                'discount_price': Decimal('3999.00'),
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&q=80',
                'stock': 22,
                'rating': Decimal('4.8'),
                'reviews_count': 56,
                'is_featured': True,
            },
        ]

        for p in products_data:
            cat = categories[p['category']]
            Product.objects.get_or_create(
                slug=p['slug'],
                defaults={
                    'category': cat,
                    'name': p['name'],
                    'description': p['description'],
                    'price': p['price'],
                    'discount_price': p['discount_price'],
                    'image_url': p['image_url'],
                    'stock': p['stock'],
                    'rating': p['rating'],
                    'reviews_count': p['reviews_count'],
                    'is_featured': p['is_featured'],
                }
            )

        self.stdout.write(self.style.SUCCESS("[SUCCESS] NovaCart seeded with 5 categories and 8 premium products!"))
        self.stdout.write(self.style.SUCCESS("Demo credentials: User='alex_customer' | Pass='password123' (Admin: 'admin' | 'admin123')"))
