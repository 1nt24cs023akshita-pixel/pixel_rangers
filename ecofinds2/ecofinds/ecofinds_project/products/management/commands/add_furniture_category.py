from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Add furniture category to the database'

    def handle(self, *args, **options):
        # Check if furniture category already exists
        furniture_category, created = Category.objects.get_or_create(
            name='Furniture',
            defaults={
                'description': 'Home and office furniture including chairs, tables, sofas, desks, and more',
                'icon': 'fas fa-couch',
                'color': 'success',
                'avg_co2_per_kg': 8.5,  # Higher CO2 impact for furniture manufacturing
                'depreciation_rate': 0.15,  # Furniture depreciates slower than electronics
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created Furniture category')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Furniture category already exists')
            )
        
        # Also add some other common categories if they don't exist
        categories_to_add = [
            {
                'name': 'Electronics',
                'description': 'Electronic devices and gadgets',
                'icon': 'fas fa-laptop',
                'color': 'primary',
                'avg_co2_per_kg': 12.0,
                'depreciation_rate': 0.25,
            },
            {
                'name': 'Clothing',
                'description': 'Fashion and apparel items',
                'icon': 'fas fa-tshirt',
                'color': 'info',
                'avg_co2_per_kg': 3.2,
                'depreciation_rate': 0.30,
            },
            {
                'name': 'Books',
                'description': 'Books, magazines, and educational materials',
                'icon': 'fas fa-book',
                'color': 'warning',
                'avg_co2_per_kg': 1.5,
                'depreciation_rate': 0.10,
            },
            {
                'name': 'Sports & Fitness',
                'description': 'Sports equipment and fitness gear',
                'icon': 'fas fa-dumbbell',
                'color': 'danger',
                'avg_co2_per_kg': 5.0,
                'depreciation_rate': 0.20,
            },
            {
                'name': 'Home & Garden',
                'description': 'Home improvement and gardening supplies',
                'icon': 'fas fa-home',
                'color': 'success',
                'avg_co2_per_kg': 4.0,
                'depreciation_rate': 0.15,
            },
        ]
        
        for category_data in categories_to_add:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created {category_data["name"]} category')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'{category_data["name"]} category already exists')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Category setup completed!')
        )

