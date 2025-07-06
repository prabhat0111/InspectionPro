import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG = {
    'TEMPLATES_DIR': 'path/to/templates',
    'ASSETS_DIR': 'assets',  # Folder containing header/footer images
    'DEFAULT_INDEMNITY': '25,000.00',
    'DEFAULT_EXPENSE_RESERVE': '3,500.00',
    'DEFAULT_TOTAL_RESERVE': '10,000.00',
    'APP_NAME': 'Inspection Pro',
    'VERSION': '1.0.0',
    'TEMPLATES_DIR': os.path.join(BASE_DIR, 'app/templates'),
    'ASSETS_DIR': os.path.join(BASE_DIR, 'assets'),
    'OUTPUT_DIR': os.path.join(BASE_DIR, 'outputs'),
    'COMPANY_INFO': {
        'name': 'Your Company',
        'logo': 'company_logo.png',
        'contact': {
            'email': 'reports@yourcompany.com',
            'phone': '(123) 456-7890'
        }
    },
    'REPORT_SETTINGS': {
        'default_margins': '15mm',
        'header_height': '20mm',
        'footer_height': '10mm'
    }
}