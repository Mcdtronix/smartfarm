from django.core.management.base import BaseCommand
from main.models import UserProfile

class Command(BaseCommand):
    help = 'Manage expert verification status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verify',
            type=str,
            help='Verify expert by username',
        )
        parser.add_argument(
            '--unverify',
            type=str,
            help='Unverify expert by username',
        )
        parser.add_argument(
            '--list-pending',
            action='store_true',
            help='List all pending expert verifications',
        )
        parser.add_argument(
            '--list-verified',
            action='store_true',
            help='List all verified experts',
        )

    def handle(self, *args, **options):
        if options['verify']:
            self.verify_expert(options['verify'])
        elif options['unverify']:
            self.unverify_expert(options['unverify'])
        elif options['list_pending']:
            self.list_pending_experts()
        elif options['list_verified']:
            self.list_verified_experts()
        else:
            self.stdout.write(
                self.style.WARNING('Please specify an action. Use --help for options.')
            )

    def verify_expert(self, username):
        try:
            profile = UserProfile.objects.get(
                user__username=username,
                account_type='expert'
            )
            profile.is_verified = True
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully verified expert: {username}')
            )
        except UserProfile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Expert profile not found for username: {username}')
            )

    def unverify_expert(self, username):
        try:
            profile = UserProfile.objects.get(
                user__username=username,
                account_type='expert'
            )
            profile.is_verified = False
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully unverified expert: {username}')
            )
        except UserProfile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Expert profile not found for username: {username}')
            )

    def list_pending_experts(self):
        pending_experts = UserProfile.objects.filter(
            account_type='expert',
            is_verified=False
        ).select_related('user')
        
        if pending_experts:
            self.stdout.write(
                self.style.WARNING(f'Found {pending_experts.count()} pending expert(s):')
            )
            for profile in pending_experts:
                self.stdout.write(f'  • {profile.user.username} ({profile.user.get_full_name()})')
                self.stdout.write(f'    Specialization: {profile.specialization or "Not specified"}')
                self.stdout.write(f'    Experience: {profile.experience_years} years')
                self.stdout.write(f'    Location: {profile.location or "Not specified"}')
                if profile.certificate_of_practice:
                    self.stdout.write(f'    Certificate: ✓ Uploaded')
                else:
                    self.stdout.write(f'    Certificate: ✗ Not uploaded')
                if profile.id_document:
                    self.stdout.write(f'    ID Document: ✓ Uploaded')
                else:
                    self.stdout.write(f'    ID Document: ✗ Not uploaded')
                self.stdout.write('')
        else:
            self.stdout.write(
                self.style.SUCCESS('No pending expert verifications found.')
            )

    def list_verified_experts(self):
        verified_experts = UserProfile.objects.filter(
            account_type='expert',
            is_verified=True
        ).select_related('user')
        
        if verified_experts:
            self.stdout.write(
                self.style.SUCCESS(f'Found {verified_experts.count()} verified expert(s):')
            )
            for profile in verified_experts:
                self.stdout.write(f'  • {profile.user.username} ({profile.user.get_full_name()})')
                self.stdout.write(f'    Specialization: {profile.specialization or "Not specified"}')
                self.stdout.write(f'    Experience: {profile.experience_years} years')
                self.stdout.write(f'    Location: {profile.location or "Not specified"}')
                self.stdout.write('')
        else:
            self.stdout.write(
                self.style.WARNING('No verified experts found.')
            )
