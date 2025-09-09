from django.core.management.base import BaseCommand
from vitamin_d_helper.models import SkinType

class Command(BaseCommand):
    help = 'Populate skin type data'
    
    def handle(self, *args, **options):
        skin_types = [
            {'type': 'I-II', 'min_exposure_minutes': 8, 'max_exposure_minutes': 12},
            {'type': 'III-IV', 'min_exposure_minutes': 15, 'max_exposure_minutes': 20},
            {'type': 'V-VI', 'min_exposure_minutes': 25, 'max_exposure_minutes': 30},
        ]
        
        for skin_type_data in skin_types:
            skin_type, created = SkinType.objects.get_or_create(
                type=skin_type_data['type'],
                defaults={
                    'min_exposure_minutes': skin_type_data['min_exposure_minutes'],
                    'max_exposure_minutes': skin_type_data['max_exposure_minutes']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created skin type: {skin_type}'))
            else:
                self.stdout.write(self.style.WARNING(f'Skin type already exists: {skin_type}'))