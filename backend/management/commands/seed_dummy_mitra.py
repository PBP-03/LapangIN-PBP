from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from backend.models import Mitra

SVG_PLACEHOLDERS = [
    ('mitra_a.svg', '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="100%" height="100%" fill="#e0f2fe"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="#0369a1">Mitra A</text></svg>'),
    ('mitra_b.svg', '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="100%" height="100%" fill="#fef3c7"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="#92400e">Mitra B</text></svg>'),
    ('mitra_c.svg', '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect width="100%" height="100%" fill="#dcfce7"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-size="20" fill="#166534">Mitra C</text></svg>'),
]

SAMPLE_DATA = [
    {'nama': 'Mitra A', 'email': 'mitra.a@example.com', 'deskripsi': 'Pemilik lapangan futsal modern, lokasi strategis.'},
    {'nama': 'Mitra B', 'email': 'mitra.b@example.com', 'deskripsi': 'Lapangan badminton indoor dengan pendingin ruangan.'},
    {'nama': 'Mitra C', 'email': 'mitra.c@example.com', 'deskripsi': 'Lapangan basket 3x3 dengan lantai kayu.'},
]


class Command(BaseCommand):
    help = 'Seed dummy Mitra entries with placeholder images (for local development)'

    def handle(self, *args, **options):
        created = 0
        for idx, sample in enumerate(SAMPLE_DATA):
            email = sample['email']
            if Mitra.objects.filter(email=email).exists():
                self.stdout.write(f"Mitra with email {email} already exists, skipping.")
                continue

            # save svg to default storage under mitra_gambar/
            filename, svg = SVG_PLACEHOLDERS[idx % len(SVG_PLACEHOLDERS)]
            storage_path = f"mitra_gambar/{filename}"
            if not default_storage.exists(storage_path):
                default_storage.save(storage_path, ContentFile(svg.encode('utf-8')))

            mitra = Mitra.objects.create(
                nama=sample['nama'],
                email=sample['email'],
                deskripsi=sample['deskripsi'],
                status=Mitra.STATUS_PENDING,
            )
            # assign the image path to the ImageField
            mitra.gambar.name = storage_path
            mitra.save()
            created += 1
            self.stdout.write(f"Created Mitra {mitra.nama} ({mitra.email})")

        self.stdout.write(self.style.SUCCESS(f"Seeding complete. {created} mitra created."))
