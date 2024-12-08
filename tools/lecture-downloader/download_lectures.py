import os
import re
import requests
from tqdm import tqdm
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('lecture_downloads.log')
    ]
)


class LectureMaterial:
    def __init__(self, week: int, title: str, file_id: str):
        self.week = week
        self.title = title
        self.file_id = file_id
        self.filename = f"week{week}_{self._sanitize_title(title)}.pdf"

    @staticmethod
    def _sanitize_title(title: str) -> str:
        """Convert Korean title to English filename-safe string"""
        title_map = {
            'DevOps & MLOps 개요': 'devops_mlops_overview',
            '컨테이너화': 'containerization',
            '지속적 배포(CD)': 'continuous_deployment',
            'IaC, 모니터링': 'iac_monitoring',
            '웹서비스 개발 기초': 'web_service_basics',
            '지속적 통합(CI), Git 협업': 'ci_git_collaboration',
            '모델 서비스 구축': 'model_service_building',
            '지속적 학습(CT)': 'continuous_training',
            '실험 추적 및 모델 관리': 'experiment_tracking',
            '데이터 관리': 'data_management',
            '인프라 관리': 'infrastructure_management',
            '클라우드 플랫폼별 MLOps': 'cloud_platform_mlops'
        }
        return title_map.get(title, title.lower().replace(' ', '_'))


def fetch_github_content() -> Optional[str]:
    """Fetch README.md content from GitHub repository"""
    url = "https://raw.githubusercontent.com/jaeyoi-classroom/devops-to-mlops-course/main/README.md"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Failed to fetch GitHub content: {str(e)}")
        return None


def extract_lecture_materials(content: str) -> List[LectureMaterial]:
    """Extract lecture materials from markdown table"""
    materials = []

    # Regular expression to match table rows
    pattern = r'\|\s*(\d+)\s*\|\s*[\d/]+\s*\|\s*([^|]+)\s*\|[^|]+\|\s*(?:\[받기\]\((https://drive\.google\.com/file/d/([^/]+)/[^)]+)\))?\s*\|'

    matches = re.finditer(pattern, content)
    for match in matches:
        week = int(match.group(1))
        title = match.group(2).strip()
        file_id = match.group(4) if match.group(4) else None

        if file_id:
            materials.append(LectureMaterial(week, title, file_id))

    return materials


def download_file(material: LectureMaterial, output_dir: str) -> bool:
    """Download a file from Google Drive using the file ID"""
    output_path = os.path.join(output_dir, material.filename)

    # Skip if file already exists
    if os.path.exists(output_path):
        logging.info(f"File already exists: {material.filename}")
        return True

    url = f"https://drive.google.com/uc?export=download&id={material.file_id}"

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        file_size = int(response.headers.get('content-length', 0))

        progress = tqdm(total=file_size, unit='iB', unit_scale=True,
                        desc=f'Downloading {material.filename}')

        with open(output_path, 'wb') as f:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                progress.update(size)

        progress.close()
        logging.info(f"Successfully downloaded: {material.filename}")
        return True

    except Exception as e:
        logging.error(f"Error downloading {material.filename}: {str(e)}")
        return False


def main():
    """Main function to download lecture materials"""
    logging.info("Starting lecture materials download process...")

    # Create directory if it doesn't exist
    output_dir = 'downloads'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created output directory: {output_dir}")

    # Fetch and parse GitHub content
    content = fetch_github_content()
    if not content:
        logging.error("Failed to fetch content from GitHub. Exiting.")
        return

    # Extract lecture materials
    materials = extract_lecture_materials(content)
    if not materials:
        logging.warning("No lecture materials found in the content.")
        return

    logging.info(f"Found {len(materials)} lecture materials")

    # Download each file
    successful = 0
    failed = 0

    for material in materials:
        if download_file(material, output_dir):
            successful += 1
        else:
            failed += 1

    # Print summary
    logging.info("\nDownload Summary:")
    logging.info(f"Successfully downloaded: {successful} files")
    logging.info(f"Failed downloads: {failed} files")
    logging.info(f"Total materials found: {len(materials)} files")


if __name__ == "__main__":
    main()
