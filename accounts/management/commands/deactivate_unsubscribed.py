# accounts/management/commands/deactvate_unsubscribed.py

"""
USAGE
Do a dry run:
python manage.py deactivate_unsubscribed path/to/unsubscribed.csv --dry-run
Execute the Actual Update:
python manage.py deactivate_unsubscribed path/to/unsubscribed.csv
Run Production Script with Custom Log Path:
python manage.py deactivate_unsubscribed path/to/unsubscribed.csv --log-file=/var/log/mailchimp_deactivation.log
"""
import csv
import logging
import os
from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Deactivates users based on a Mailchimp unsubscribed CSV, logs operations, and exports unmatched records.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the Mailchimp CSV file')
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without modifying the database',
        )
        parser.add_argument(
            '--log-file',
            type=str,
            default=None,
            help='Optional custom log file path',
        )
        parser.add_argument(
            '--export-unmatched',
            type=str,
            default=None,
            help='Optional path for unmatched CSV output (defaults to unmatched_records_YYYYMMDD_HHMMSS.csv)',
        )

    def handle(self, *args, **options):
        file_path = options['csv_file']
        dry_run = options['dry_run']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Ensure the project-level logs directory exists
        logs_dir = os.path.join(settings.BASE_DIR, 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        # Default log path inside <BASE_DIR>/logs/
        default_log_path = os.path.join(logs_dir, f"deactivate_unsubscribed_{timestamp}.log")
        log_file_path = options['log_file'] or default_log_path

        # Default unmatched export path inside <BASE_DIR>/logs/
        default_unmatched_path = os.path.join(logs_dir, f"unmatched_records_{timestamp}.csv")
        unmatched_csv_path = options['export_unmatched'] or default_unmatched_path

        # Setup dedicated logger
        logger = logging.getLogger('deactivate_unsubscribed')
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        def log_and_print(message, style_func=None, level='info'):
            if level == 'warning':
                logger.warning(message)
            elif level == 'error':
                logger.error(message)
            else:
                logger.info(message)

            if style_func:
                self.stdout.write(style_func(message))
            else:
                self.stdout.write(message)

        log_and_print(f"--- Process started. Target CSV: {file_path} ---")
        if dry_run:
            log_and_print("--- RUNNING IN DRY-RUN MODE (NO DATABASE CHANGES) ---", self.style.WARNING, level='warning')

        updated_count = 0
        not_found_count = 0
        already_inactive_count = 0
        unmatched_rows = []

        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                fieldnames = reader.fieldnames or []

                for row_idx, row in enumerate(reader, start=2):
                    email = row.get('Email Address', '').strip()
                    first_name = row.get('First Name', '').strip()
                    last_name = row.get('Last Name', '').strip()

                    if not email:
                        log_and_print(f"Row {row_idx}: Skipped - Empty email field", self.style.WARNING, level='warning')
                        unmatched_row = dict(row)
                        unmatched_row['Reason'] = 'Empty Email Field'
                        unmatched_rows.append(unmatched_row)
                        not_found_count += 1
                        continue

                    queryset = User.objects.filter(
                        email__iexact=email,
                        first_name__iexact=first_name,
                        last_name__iexact=last_name,
                    )

                    user = queryset.first()

                    if not user:
                        msg = f"Row {row_idx}: [NOT FOUND] No record for email='{email}', name='{first_name} {last_name}'"
                        log_and_print(msg, self.style.WARNING, level='warning')
                        unmatched_row = dict(row)
                        unmatched_row['Reason'] = 'User Not Found in Database'
                        unmatched_rows.append(unmatched_row)
                        not_found_count += 1

                    elif not user.is_active:
                        msg = f"Row {row_idx}: [ALREADY INACTIVE] {user.email} (ID: {user.pk})"
                        log_and_print(msg, level='info')
                        already_inactive_count += 1

                    else:
                        if dry_run:
                            msg = f"Row {row_idx}: [WOULD DEACTIVATE] {user.email} - {user.get_full_name()} (ID: {user.pk})"
                            log_and_print(msg, self.style.SUCCESS, level='info')
                        else:
                            user.is_active = False
                            user.save(update_fields=['is_active'])
                            msg = f"Row {row_idx}: [DEACTIVATED] {user.email} - {user.get_full_name()} (ID: {user.pk})"
                            log_and_print(msg, self.style.SUCCESS, level='info')
                        updated_count += 1

        except Exception as e:
            log_and_print(f"Fatal error reading CSV file: {str(e)}", self.style.ERROR, level='error')
            return

        # Export unmatched records to CSV
        if unmatched_rows:
            export_fieldnames = list(fieldnames)
            if 'Reason' not in export_fieldnames:
                export_fieldnames.append('Reason')

            with open(unmatched_csv_path, mode='w', encoding='utf-8', newline='') as out_file:
                writer = csv.DictWriter(out_file, fieldnames=export_fieldnames)
                writer.writeheader()
                writer.writerows(unmatched_rows)

            log_and_print(f"Exported {len(unmatched_rows)} unmatched record(s) to: {unmatched_csv_path}", self.style.WARNING)

        # Print & Log Summary
        prefix = "WOULD DEACTIVATE" if dry_run else "DEACTIVATED"
        summary_text = (
            f"\n" + "=" * 40 + "\n"
            f"SUMMARY RESULTS:\n"
            f"  - {prefix}: {updated_count}\n"
            f"  - Already Inactive: {already_inactive_count}\n"
            f"  - Not Found / Unmatched: {not_found_count}\n"
            f"  - Log Saved To: {log_file_path}\n"
            f"  - Unmatched Exported To: {unmatched_csv_path if unmatched_rows else 'N/A (0 unmatched)'}\n"
            + "=" * 40
        )

        log_and_print(summary_text, self.style.SUCCESS)