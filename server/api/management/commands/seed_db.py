from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Ping, User

# Seed MI6 agents (see .project/SPEC.md - User model requirements)
agents = [
    {
        "email": "bond@james.bond",
        "name": "James Bond",
        "code_name": "007",
        "password": "shakenNotStirred",
    },
    {
        "email": "eve@money.penny",
        "name": "Eve Moneypenny",
        "code_name": "MONEYPENNY",
        "password": "moneypennySecure",
    },
    {
        "email": "q@branch.q",
        "name": "Q",
        "code_name": "Q",
        "password": "gadgets4days",
    },
]


class Command(BaseCommand):
    help = "Seed the database with initial data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding database..."))
        self.stdout.write(
            self.style.NOTICE("This will create a superuser and several agents.")
        )
        self.stdout.write(self.style.NOTICE("It will also create some initial pings."))
        self.seed_superuser()
        self.seed_agents()
        self.seed_pings()

    def seed_superuser(self):
        # Seed MI6 supervisor "M" as a superuser
        superuser_email = "m@mi6.gov"
        superuser_name = "M"
        superuser_code_name = "M"
        superuser_password = "topSecretM"

        if not User.objects.filter(email=superuser_email).exists():
            User.objects.create_superuser(
                email=superuser_email,
                password=superuser_password,
                name=superuser_name,
                code_name=superuser_code_name,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Superuser {superuser_email} created.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Superuser {superuser_email} already exists.")
            )

    def seed_agents(self):
        users = []
        for agent in agents:
            user, created = User.objects.get_or_create(
                email=agent["email"],
                defaults={"name": agent["name"], "code_name": agent["code_name"]},
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Agent {agent['code_name']} created.")
                )
                user.set_password(agent["password"])
                user.save()
            users.append(user)

    def seed_pings(self):
        # Fetch users by code_name for clarity
        users = {
            u.code_name: u
            for u in User.objects.filter(code_name__in=[a["code_name"] for a in agents])
        }

        # Standalone pings
        Ping.objects.get_or_create(
            user=users["007"],
            latitude=51.5074,
            longitude=-0.1278,  # London
            timestamp=timezone.now(),
        )
        Ping.objects.get_or_create(
            user=users["MONEYPENNY"],
            latitude=9.0578,
            longitude=7.4951,  # Abuja (Nigeria)
            timestamp=timezone.now(),
        )
        Ping.objects.get_or_create(
            user=users["Q"],
            latitude=35.6895,
            longitude=139.6917,  # Tokyo
            timestamp=timezone.now(),
        )

        # Ping chain 1
        ping1 = Ping.objects.create(
            user=users["007"],
            latitude=55.7558,
            longitude=37.6173,  # Moscow
            timestamp=timezone.now(),
        )
        ping2 = Ping.objects.create(
            user=users["MONEYPENNY"],
            latitude=-33.8688,
            longitude=151.2093,  # Sydney
            timestamp=timezone.now(),
            parent_ping=ping1,
        )
        Ping.objects.create(
            user=users["Q"],
            latitude=-18.8792,
            longitude=47.5079,  # Antananarivo (Madagascar)
            timestamp=timezone.now(),
            parent_ping=ping2,
        )

        # Ping chain 2
        ping4 = Ping.objects.create(
            user=users["Q"],
            latitude=52.52,
            longitude=13.4050,  # Berlin
            timestamp=timezone.now(),
        )
        ping5 = Ping.objects.create(
            user=users["007"],
            latitude=34.0522,
            longitude=-118.2437,  # Los Angeles
            timestamp=timezone.now(),
            parent_ping=ping4,
        )

        ping6 = Ping.objects.create(
            user=users["Q"],
            latitude=-34.6037,
            longitude=-58.3816,  # Buenos Aires
            timestamp=timezone.now(),
            parent_ping=ping5,
        )

        Ping.objects.create(
            user=users["MONEYPENNY"],
            latitude=-33.9249,
            longitude=18.4241,  # Cape Town
            timestamp=timezone.now(),
            parent_ping=ping6,
        )
