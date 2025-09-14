# claims/management/commands/import_claims.py

import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from claims.models import Claim, ClaimDetail

class Command(BaseCommand):
    help = 'Loads claim data from claim_list_data.csv and claim_detail_data.csv'

    def handle(self, *args, **options):
        # --- File Paths (assuming CSVs are in the project root) ---
        claim_list_path = 'claim_list_data.csv'
        claim_detail_path = 'claim_detail_data.csv'

        try:
            with transaction.atomic():
                self.stdout.write(self.style.WARNING('Clearing existing claim data...'))
                ClaimDetail.objects.all().delete()
                Claim.objects.all().delete()
                self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

                # --- Load claim_list_data.csv ---
                self.stdout.write(f"Loading claims from {claim_list_path}...")
                claims_to_create = []
                with open(claim_list_path, mode='r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter='|')
                    for row in reader:
                        try:
                            claims_to_create.append(Claim(
                                id=int(row['id']),
                                patient_name=row['patient_name'],
                                billed_amount=Decimal(row['billed_amount']),
                                paid_amount=Decimal(row['paid_amount']),
                                status=row['status'],
                                insurer_name=row['insurer_name'],
                                discharge_date=datetime.strptime(row['discharge_date'], '%Y-%m-%d').date()
                            ))
                        except (ValueError, InvalidOperation, KeyError) as e:
                            self.stderr.write(self.style.ERROR(f"Skipping claim row due to error: {e} | Data: {row}"))
                            continue
                
                Claim.objects.bulk_create(claims_to_create, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(claims_to_create)} claims.'))

                # --- Load claim_detail_data.csv ---
                self.stdout.write(f"Loading claim details from {claim_detail_path}...")
                details_to_create = []
                with open(claim_detail_path, mode='r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter='|')
                    for row in reader:
                        try:
                            # We can create the ClaimDetail object directly using the claim_id
                            details_to_create.append(ClaimDetail(
                                claim_id=int(row['claim_id']),
                                denial_reason=row.get('denial_reason', ''),
                                cpt_codes=row.get('cpt_codes', '')
                            ))
                        except (ValueError, KeyError) as e:
                            self.stderr.write(self.style.ERROR(f"Skipping detail row due to error: {e} | Data: {row}"))
                            continue
                
                ClaimDetail.objects.bulk_create(details_to_create, batch_size=1000)
                self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(details_to_create)} claim details.'))

        except FileNotFoundError as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}. Make sure the CSV files are in the project's root directory."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))