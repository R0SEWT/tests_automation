"""
HU Configuration Manager

Manages HU configuration from Excel files and prepares data for matching
with Jira-extracted content.
"""

import pandas as pd
import re
from collections import Counter
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HUConfigurationManager:
    """
    Manages HU configuration extracted from Excel files.

    Handles the relationship between Excel worksheets, HU codes, and Jira links
    to prepare for content matching and correction workflows.
    """

    def __init__(self, excel_path: str):
        """
        Initialize with Excel file path.

        Args:
            excel_path: Path to the Excel file containing HU configuration
        """
        self.excel_path = Path(excel_path)
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")

        self._analysis = None
        self._hu_links = {}
        self._worksheet_mapping = {}

    @property
    def analysis(self) -> Dict:
        """Get the analysis results (cached)."""
        if self._analysis is None:
            self._analysis = self._analyze_excel_structure()
        return self._analysis

    def _analyze_excel_structure(self) -> Dict:
        """Analyze the Excel file structure."""
        excel_file = pd.ExcelFile(self.excel_path)

        # Get all worksheet names
        worksheets = excel_file.sheet_names

        # Analyze patterns in worksheet names (prefix + number)
        pattern = r'^([A-Z]+)(\d+)$'
        matches = []

        for sheet in worksheets:
            sheet_str = str(sheet)
            match = re.match(pattern, sheet_str)
            if match:
                prefix, number = match.groups()
                matches.append((prefix, int(number), sheet_str))

        # Count prefixes
        prefixes = [m[0] for m in matches]
        prefix_counts = Counter(prefixes)

        # Most common prefix
        most_common_prefix = prefix_counts.most_common(1)[0][0] if prefix_counts else None

        # Extract HU links from HUs worksheet
        hu_links = self._extract_hu_links()

        return {
            'total_worksheets': len(worksheets),
            'worksheet_names': worksheets,
            'pattern_matches': matches,
            'prefix_counts': dict(prefix_counts),
            'most_common_prefix': most_common_prefix,
            'hu_links': hu_links,
            'hu_count': len(hu_links)
        }

    def _extract_hu_links(self) -> Dict[str, str]:
        """Extract HU links from the HUs worksheet."""
        hu_links = {}
        try:
            df_hus = pd.read_excel(self.excel_path, sheet_name='HUs')
            if 'HU' in df_hus.columns and 'Link HU' in df_hus.columns:
                for _, row in df_hus.iterrows():
                    hu_code = str(row['HU']).strip()
                    link = str(row['Link HU']).strip()
                    if hu_code and link and link.startswith('http'):
                        # Extract HU code (e.g., "USRNM01" from "USRNM01 - description...")
                        hu_match = re.match(r'^([A-Z]+\d+)', hu_code)
                        if hu_match:
                            clean_hu_code = hu_match.group(1)
                            hu_links[clean_hu_code] = link
        except Exception as e:
            logger.warning(f"Could not extract HU links: {e}")

        return hu_links

    def get_hu_prefix(self) -> Optional[str]:
        """Get the most common HU prefix from worksheet names."""
        return self.analysis['most_common_prefix']

    def get_hu_links(self) -> Dict[str, str]:
        """Get all HU links as a dictionary {HU_CODE: JIRA_LINK}."""
        return self.analysis['hu_links']

    def get_worksheet_mapping(self) -> Dict[str, str]:
        """
        Get mapping of HU codes to worksheet names.

        Returns:
            Dictionary mapping HU codes (e.g., 'USRNM01') to worksheet names
        """
        if not self._worksheet_mapping:
            prefix = self.get_hu_prefix()
            if prefix:
                for match in self.analysis['pattern_matches']:
                    if match[0] == prefix:
                        hu_code = f"{prefix}{match[1]:02d}"  # Ensure 2-digit format
                        self._worksheet_mapping[hu_code] = match[2]

        return self._worksheet_mapping

    def get_available_hu_codes(self) -> List[str]:
        """Get list of all available HU codes from the configuration."""
        return list(self.get_hu_links().keys())

    def get_jira_issue_keys(self) -> List[str]:
        """
        Extract Jira issue keys from HU links.

        Returns:
            List of Jira issue keys (e.g., ['VLPER-91037', 'VLPER-91038', ...])
        """
        issue_keys = []
        for link in self.get_hu_links().values():
            # Extract issue key from URL like https://jira.visma.com/browse/VLPER-91037
            match = re.search(r'/browse/([A-Z]+-\d+)', link)
            if match:
                issue_keys.append(match.group(1))
        return issue_keys

    def prepare_matching_data(self) -> Dict:
        """
        Prepare data structure for future HU content matching.

        Returns:
            Dictionary with all data needed for matching HU codes with content
        """
        return {
            'hu_prefix': self.get_hu_prefix(),
            'hu_links': self.get_hu_links(),
            'worksheet_mapping': self.get_worksheet_mapping(),
            'available_hu_codes': self.get_available_hu_codes(),
            'jira_issue_keys': self.get_jira_issue_keys(),
            'total_hus': len(self.get_available_hu_codes())
        }

    def validate_configuration(self) -> List[str]:
        """
        Validate the HU configuration for consistency.

        Returns:
            List of validation warnings/errors
        """
        warnings = []

        # Check if HU links match worksheet names
        hu_codes = set(self.get_available_hu_codes())
        worksheet_codes = set(self.get_worksheet_mapping().keys())

        missing_worksheets = hu_codes - worksheet_codes
        if missing_worksheets:
            warnings.append(f"HU codes without worksheets: {sorted(missing_worksheets)}")

        extra_worksheets = worksheet_codes - hu_codes
        if extra_worksheets:
            warnings.append(f"Worksheets without HU links: {sorted(extra_worksheets)}")

        # Check prefix consistency
        prefix = self.get_hu_prefix()
        if not prefix:
            warnings.append("No consistent prefix found in worksheet names")

        # Check HU code format consistency
        for hu_code in hu_codes:
            if not re.match(r'^[A-Z]+\d+$', hu_code):
                warnings.append(f"Invalid HU code format: {hu_code}")

        return warnings


def load_hu_configuration(excel_path: str = 'data/USERNAME.xlsx') -> HUConfigurationManager:
    """
    Convenience function to load HU configuration from Excel file.

    Args:
        excel_path: Path to the Excel file

    Returns:
        HUConfigurationManager instance
    """
    return HUConfigurationManager(excel_path)