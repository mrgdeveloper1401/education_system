import csv
from django.core.management.base import BaseCommand
from accounts.models import State, City
from pathlib import Path

base_dir = Path(__file__).resolve().parent

class Command(BaseCommand):
    help = 'Import Iranian provinces and cities from CSV file'

    def handle(self, *args, **options):
        # خواندن فایل CSV
        get_file = base_dir.joinpath("all.csv")
        with open(get_file, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            # ایجاد یک دیکشنری برای نگهداری استان‌ها و شهرهای آنها
            provinces = {}

            for row in csv_reader:
                if row['type'] == 'province':
                    # اگر رکورد مربوط به استان است
                    province_name = row['name']
                    provinces[province_name] = []
                elif row['type'] in ['county', 'city', 'district', 'rural']:
                    # اگر رکورد مربوط به شهر/بخش/روستا است
                    # پیدا کردن استان مربوطه
                    province_id = row['id'][:3]  # سه رقم اول id مربوط به استان است
                    for province_name in provinces.keys():
                        if province_name.startswith(province_id):
                            provinces[province_name].append(row['name'])
                            break

            # ذخیره استان‌ها و شهرها در دیتابیس
            for province_name, cities in provinces.items():
                # ایجاد یا دریافت استان
                state, created = State.objects.get_or_create(state_name=province_name)

                # اضافه کردن شهرهای مربوط به این استان
                for city_name in cities:
                    City.objects.get_or_create(state=state, city=city_name)

            self.stdout.write(self.style.SUCCESS('Successfully imported provinces and cities'))
