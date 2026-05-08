from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create default admin group and account"

    def add_arguments(self, parser):
        parser.add_argument("--admin-username", default="admin")
        parser.add_argument("--admin-password", default="admin123456")
        parser.add_argument("--admin-email", default="")

    def handle(self, *args, **options):
        admin_group, _ = Group.objects.get_or_create(name="管理员")
        Group.objects.get_or_create(name="普通用户")

        username = options["admin_username"]
        password = options["admin_password"]
        email = options["admin_email"]

        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
        else:
            self.stdout.write(self.style.WARNING(f"User exists: {username}"))

        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save(update_fields=["is_staff", "is_superuser"])
            self.stdout.write(self.style.SUCCESS("Granted superuser/staff"))

        user.groups.add(admin_group)
        self.stdout.write(self.style.SUCCESS("Bootstrap done"))
