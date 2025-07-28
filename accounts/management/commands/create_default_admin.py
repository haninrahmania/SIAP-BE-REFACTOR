from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create default admin if not exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_user(
                username='admin',
                password='password123',
                email='admin@example.com',
                first_name='Admin',
                last_name='Sistem',
                role='Admin Sistem'  
            )
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS('Admin user "admin" created'))
        else:
            self.stdout.write('Admin user already exists')
