"""
Django management command to seed database from CSV file.

Reads healthcare fraud detection results from a CSV file and creates
Transaction and Alert objects in the database.

Usage:
    python manage.py seed_db [--csv-path /path/to/file.csv] [--clear]

Options:
    --csv-path: Path to CSV file (default: hcfd_xai_final_results.csv)
    --clear: Clear all transactions before loading (use with caution)
"""

import os
import sys
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction as db_transaction
import pandas as pd

from models import Transaction, Alert


class Command(BaseCommand):
    """Django management command for seeding the database from CSV."""

    help = 'Seed database with fraud detection results from CSV file'

    def add_arguments(self, parser):
        """Define command arguments."""
        parser.add_argument(
            '--csv-path',
            type=str,
            default='hcfd_xai_final_results.csv',
            help='Path to CSV file (default: hcfd_xai_final_results.csv)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all transactions before loading (use with caution)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of rows to load (for testing)',
        )

    def handle(self, *args, **options):
        """Execute the seeding command."""
        csv_path = options['csv_path']
        clear_db = options['clear']
        limit = options['limit']

        try:
            # Validate CSV file exists
            if not os.path.exists(csv_path):
                raise CommandError(f'CSV file not found: {csv_path}')

            self.stdout.write(self.style.SUCCESS(f'Reading CSV file: {csv_path}'))

            # Clear existing data if requested
            if clear_db:
                self.stdout.write(self.style.WARNING('Clearing existing transactions...'))
                Transaction.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Cleared {Transaction.objects.count()} transactions')
                )

            # Read CSV file
            try:
                df = pd.read_csv(csv_path)
            except Exception as e:
                raise CommandError(f'Error reading CSV file: {str(e)}')

            # Validate required columns
            required_columns = [
                'caseid',
                'age',
                'wealth_idx',
                'education',
                'residence',
                'has_diabetes',
                'has_htn',
                'DVS',
                'TNS',
                'ICS',
                'CCS',
                'HCFD_score',
                'rule_score',
                'anomaly_score',
                'final_risk',
                'risk_tier',
                'explanation',
            ]

            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise CommandError(f'CSV missing required columns: {", ".join(missing_columns)}')

            self.stdout.write(self.style.SUCCESS(f'CSV has {len(df)} rows'))

            if limit:
                df = df.head(limit)
                self.stdout.write(self.style.WARNING(f'Limited to first {limit} rows'))

            # Seed database
            stats = self._seed_transactions(df)

            # Print summary
            self._print_summary(stats)

        except CommandError as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            sys.exit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Unexpected error: {str(e)}'))
            sys.exit(1)

    def _seed_transactions(self, df):
        """Seed transactions from DataFrame."""
        stats = {
            'total_rows': len(df),
            'created': 0,
            'skipped': 0,
            'alerts_created': 0,
            'errors': 0,
        }

        with db_transaction.atomic():
            for index, row in df.iterrows():
                try:
                    caseid = str(row['caseid']).strip()

                    # Check if transaction already exists (idempotent)
                    if Transaction.objects.filter(caseid=caseid).exists():
                        stats['skipped'] += 1
                        if (index + 1) % 1000 == 0:
                            self.stdout.write(
                                f'Progress: {index + 1}/{stats["total_rows"]} '
                                f'(Created: {stats["created"]}, Skipped: {stats["skipped"]}, '
                                f'Alerts: {stats["alerts_created"]})'
                            )
                        continue

                    # Parse boolean fields
                    has_diabetes = self._parse_bool(row['has_diabetes'])
                    has_htn = self._parse_bool(row['has_htn'])

                    # Create Transaction object
                    transaction = Transaction.objects.create(
                        caseid=caseid,
                        age=int(row['age']),
                        wealth_idx=float(row['wealth_idx']),
                        education=str(row.get('education', '')).strip(),
                        residence=str(row.get('residence', '')).strip(),
                        has_diabetes=has_diabetes,
                        has_htn=has_htn,
                        DVS=float(row['DVS']),
                        TNS=float(row['TNS']),
                        ICS=float(row['ICS']),
                        CCS=float(row['CCS']),
                        HCFD_score=float(row['HCFD_score']),
                        rule_score=float(row['rule_score']),
                        anomaly_score=float(row['anomaly_score']),
                        final_risk=float(row['final_risk']),
                        risk_tier=self._parse_risk_tier(row['risk_tier']),
                        explanation=str(row.get('explanation', '')).strip(),
                    )

                    stats['created'] += 1

                    # Create Alert if risk is critical
                    final_risk = float(row['final_risk'])
                    if final_risk > 0.75:
                        alert = Alert.objects.create(
                            transaction=transaction,
                            risk_tier=self._parse_risk_tier(row['risk_tier']),
                            final_risk=final_risk,
                            message=f"Critical fraud risk detected: {final_risk:.3f}",
                            is_resolved=False,
                        )
                        stats['alerts_created'] += 1

                    # Show progress every 1000 rows
                    if (index + 1) % 1000 == 0:
                        self.stdout.write(
                            f'Progress: {index + 1}/{stats["total_rows"]} '
                            f'(Created: {stats["created"]}, Skipped: {stats["skipped"]}, '
                            f'Alerts: {stats["alerts_created"]})'
                        )

                except Exception as e:
                    stats['errors'] += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error processing row {index + 1} (caseid={row.get("caseid")}): {str(e)}'
                        )
                    )
                    continue

        return stats

    @staticmethod
    def _parse_bool(value):
        """Parse boolean value from various formats."""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'y', 'on')
        return False

    @staticmethod
    def _parse_risk_tier(value):
        """Parse and normalize risk tier value."""
        tier_map = {
            'low': 'low',
            'medium': 'medium',
            'high': 'high',
            'critical': 'critical',
            'low risk': 'low',
            'medium risk': 'medium',
            'high risk': 'high',
            'critical risk': 'critical',
        }

        normalized = str(value).lower().strip()
        return tier_map.get(normalized, 'low')

    def _print_summary(self, stats):
        """Print database seeding summary."""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('DATABASE SEEDING COMPLETE'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'Total rows in CSV:     {stats["total_rows"]:>10}')
        self.stdout.write(f'Transactions created:  {stats["created"]:>10}')
        self.stdout.write(f'Transactions skipped:  {stats["skipped"]:>10}')
        self.stdout.write(f'Alerts created:        {stats["alerts_created"]:>10}')
        if stats['errors'] > 0:
            self.stdout.write(
                self.style.WARNING(f'Errors encountered:   {stats["errors"]:>10}')
            )
        self.stdout.write('=' * 70 + '\n')

        if stats['created'] == 0 and stats['skipped'] == 0:
            self.stdout.write(self.style.WARNING('No new transactions were loaded.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully loaded {stats["created"]} transactions '
                    f'and created {stats["alerts_created"]} alerts.'
                )
            )
