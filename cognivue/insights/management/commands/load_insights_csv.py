import csv
from django.core.management.base import BaseCommand
from cognivue.insights.models import Factoid, LifestyleTip

def _norm(row):
    return { (k or "").strip().lower(): (v or "").strip() for k, v in row.items() }

class Command(BaseCommand):
    help = "Load CSVs into Factoid and LifestyleTip from simple CSVs."

    def add_arguments(self, p):
        p.add_argument('--factoids', type=str, help='Path to factoids.csv (title,description,source,...)')
        p.add_argument('--cards', type=str, help='Path to cards.csv (title,description,...)')
        p.add_argument('--truncate', action='store_true', help='Delete existing data before loading')

    def handle(self, *args, **o):
        if o.get('truncate'):
            Factoid.objects.all().delete()
            LifestyleTip.objects.all().delete()
            self.stdout.write(self.style.WARNING("Truncated existing data."))

        if o.get('factoids'):
            self._load_factoids(o['factoids'])
        if o.get('cards'):
            self._load_cards(o['cards'])

        self.stdout.write(self.style.SUCCESS("Done."))

    def _load_factoids(self, path):
        created = 0
        with open(path, encoding='utf-8', newline='') as f:
            r = csv.DictReader(f)
            for i, raw in enumerate(r):
                row = _norm(raw)
                title = row.get('title')
                description  = row.get('description') or row.get('text')
                if not title or not description:
                    continue
                source_plain = row.get('source') or row.get('source_name') or ""

                try:
                    order_index = int(row.get('order', row.get('order_index', i)))
                except ValueError:
                    order_index = i
                is_active = (row.get('active', 'true').lower() in ('1','true','yes','y'))

                Factoid.objects.create(
                    title=title,
                    text=description,
                    badge=row.get('badge',''),
                    source_name=source_plain,   # plain text only
                    source_url="",              # keep empty
                    icon=row.get('icon',''),
                    order_index=order_index,
                    is_active=is_active,
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Loaded {created} factoid(s) from {path}"))

    def _load_cards(self, path):
        created = 0
        with open(path, encoding='utf-8', newline='') as f:
            r = csv.DictReader(f)
            for i, raw in enumerate(r):
                row = _norm(raw)
                title = row.get('title')
                description  = row.get('description') or row.get('front_summary')
                if not title or not description:
                    continue

                impact = (row.get('impact') or 'beneficial').lower()
                if impact not in ('beneficial','concerning'):
                    impact = 'beneficial'
                try:
                    order_index = int(row.get('order', row.get('order_index', i)))
                except ValueError:
                    order_index = i
                is_active = (row.get('active','true').lower() in ('1','true','yes','y'))

                LifestyleTip.objects.create(
                    title=title,
                    impact=impact,
                    front_summary=description[:120],
                    back_detail=row.get('back_detail', description),
                    icon=row.get('icon',''),
                    order_index=order_index,
                    is_active=is_active,
                )
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Loaded {created} lifestyle tip(s) from {path}"))
