import pandas as pd
from datetime import datetime
from pathlib import Path
import jinja2
import pdfkit
import uuid
import logging
import random
from typing import List, Dict, Optional, Union

class InspectionReportEngine:
    def __init__(self, config: dict):
        self.config = config
        self.logger = self._setup_logging()
        self.pdf_config = self._configure_pdfkit()
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(config['TEMPLATES_DIR']),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._register_template_filters()

    def _setup_logging(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _configure_pdfkit(self):
        try:
            possible_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                '/usr/local/bin/wkhtmltopdf',
                '/usr/bin/wkhtmltopdf'
            ]
            for path in possible_paths:
                if Path(path).exists():
                    return pdfkit.configuration(wkhtmltopdf=path)
            return pdfkit.configuration()
        except Exception as e:
            self.logger.error(f"PDFKit configuration failed: {e}")
            raise RuntimeError("Could not configure PDF generator. Please install wkhtmltopdf.")

    def _register_template_filters(self):
        def format_date(value, fmt='%B %d, %Y'):
            if pd.isna(value):
                return "N/A"
            try:
                return datetime.strptime(str(value), '%Y-%m-%d').strftime(fmt)
            except (ValueError, TypeError):
                return str(value)
        self.template_env.filters['format_date'] = format_date

    def process_claims(self, data_file: Union[str, Path], output_dir: Union[str, Path], 
                      photos_dir: Optional[Union[str, Path]] = None) -> List[Path]:
        try:
            claims = self._load_data(data_file)
            reports_generated = []
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            for idx, claim in enumerate(claims, 1):
                try:
                    claim_data = self._prepare_claim_data(claim, photos_dir)
                    report_path = self._generate_report(claim_data, output_dir)
                    reports_generated.append(report_path)
                    self.logger.info(f"Generated report {idx}/{len(claims)}: {report_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to process claim {idx}: {e}")
                    continue
            return reports_generated
        except Exception as e:
            self.logger.error(f"Fatal error processing claims: {e}")
            raise

    def _prepare_claim_data(self, claim: Dict, photos_dir: Optional[Path]) -> Dict:
        claim_data = claim.copy()
        claim_data['report_id'] = f"FIR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        if photos_dir:
            photos_path = Path(photos_dir)
            if photos_path.exists():
                claim_data['header_image'] = self._find_special_image(photos_path, 'header')
                claim_data['footer_image'] = self._find_special_image(photos_path, 'footer')
                claim_data['front_photo'] = self._find_special_image(photos_path, ['front', 'facade'])
                claim_data['photos'] = self._organize_room_photos(photos_path, claim_data)
            else:
                self.logger.warning(f"Photos directory not found: {photos_path}")
                claim_data.update({
                    'header_image': None,
                    'footer_image': None,
                    'front_photo': None,
                    'photos': []
                })
        else:
            claim_data.update({
                'header_image': None,
                'footer_image': None,
                'front_photo': None,
                'photos': []
            })

        claim_data['indemnity_amount'] = f"{random.randint(20000, 30000):,}.00"
        claim_data['expense_reserve'] = f"{random.randint(3000, 6000):,}.00"
        claim_data['total_reserve'] = f"{random.randint(8000, 12000):,}.00"

        if 'SCOPE OF WORK' in claim_data:
            scope_items = [item.strip() for item in str(claim_data['SCOPE OF WORK']).split('\n') if item.strip()]
            claim_data['SCOPE OF WORK'] = scope_items

        return claim_data

    def _find_special_image(self, photos_path: Path, keywords: Union[str, List[str]]) -> Optional[str]:
        if isinstance(keywords, str):
            keywords = [keywords]
        for photo in photos_path.rglob('*.*'):
            if photo.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                continue
            lower_name = photo.name.lower()
            if any(kw.lower() in lower_name for kw in keywords):
                return str(photo)
        return None

    def _organize_room_photos(self, photos_path: Path, claim: Dict) -> List[Dict]:
        room_types = [
            ('BEDROOM1', ['bedroom1', 'master']),
            ('BEDROOM2', ['bedroom2', 'second']),
            ('KITCHEN', ['kitchen']),
            ('LIVING', ['living', 'lounge']),
            ('STORAGE', ['storage', 'basement'])
        ]

        photo_data = []
        special_images = [
            claim.get('header_image', ''),
            claim.get('footer_image', ''),
            claim.get('front_photo', '')
        ]

        for room_name, keywords in room_types:
            room_photos = []
            for photo in photos_path.rglob('*.*'):
                if photo.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                    continue
                if str(photo) in special_images:
                    continue
                photo_name = photo.name.lower()
                photo_parent = photo.parent.name.lower()
                if (any(kw in photo_name for kw in keywords) or 
                    any(kw in photo_parent for kw in keywords)):
                    room_photos.append(str(photo))
            if room_photos:
                photo_data.append({
                    'room': room_name,
                    'images': sorted(room_photos)[:4]
                })

        return photo_data

    def _generate_report(self, claim: Dict, output_dir: Path) -> Path:
        try:
            template = self.template_env.get_template('inspection_template.html')
            html_content = template.render(
                claim=claim,
                config=self.config,
                now=datetime.now().strftime('%Y-%m-%d %H:%M')
            )

            output_path = output_dir / f"FIRST INSPECTION REPORT - CLAIM# {claim['CLAIM #']} - {claim['INSURED/POLICYHOLDER'].split()[0].upper()} - {claim['ADDRESS'].replace(',', '').replace(' ', '_')}.pdf"
            
            options = {
                'enable-local-file-access': '',
                'margin-top': '3cm',
                'margin-bottom': '2cm',
                'encoding': 'UTF-8',
                'quiet': '',
                'header-spacing': '5',
                'footer-spacing': '5',
                'disable-smart-shrinking': ''
            }

            pdfkit.from_string(
                html_content,
                str(output_path),
                configuration=self.pdf_config,
                options=options
            )

            return output_path
        except jinja2.TemplateError as e:
            raise ValueError(f"Template error: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate PDF: {e}")

    def _load_data(self, data_file: Union[str, Path]) -> List[Dict]:
        file_path = Path(data_file)

        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8-sig')
            else:
                df = pd.read_excel(file_path, engine='openpyxl')

            if df.empty:
                raise ValueError("Input file contains no data")

            df = df.replace({pd.NA: None, "": None})
            df = df.applymap(lambda x: None if isinstance(x, str) and x.strip() == "" else x)

            return df.to_dict('records')

        except Exception as e:
            raise ValueError(f"Failed to load data file: {e}")
