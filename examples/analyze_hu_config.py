#!/usr/bin/env python3
"""
HU Configuration Analyzer

Analyzes the USERNAME.xlsx file to:
1. Extract Jira links from HUs worksheet
2. Identify the most common prefix from worksheet names
3. Update HU_CODE environment variable if needed
4. Prepare for future HU content matching
"""

import pandas as pd
import re
from collections import Counter
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_excel_structure(excel_path: str) -> dict:
    """
    Analyze the Excel file structure and return configuration data.

    Args:
        excel_path: Path to the Excel file

    Returns:
        Dictionary with analysis results
    """
    excel_file = pd.ExcelFile(excel_path)

    # Get all worksheet names
    worksheets = excel_file.sheet_names

    # Analyze patterns in worksheet names (prefix + number)
    pattern = r'^([A-Z]+)(\d+)$'
    matches = []

    for sheet in worksheets:
        sheet_str = str(sheet)  # Ensure it's a string
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
    hu_links = {}
    try:
        df_hus = pd.read_excel(excel_path, sheet_name='HUs')
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

    return {
        'total_worksheets': len(worksheets),
        'worksheet_names': worksheets,
        'pattern_matches': matches,
        'prefix_counts': dict(prefix_counts),
        'most_common_prefix': most_common_prefix,
        'hu_links': hu_links,
        'hu_count': len(hu_links)
    }


def update_hu_code_if_needed(analysis: dict, env_file: str = '.env'):
    """
    Update HU_CODE in environment file if the most common prefix is different.

    Args:
        analysis: Analysis results from analyze_excel_structure
        env_file: Path to environment file
    """
    most_common_prefix = analysis['most_common_prefix']

    if not most_common_prefix:
        logger.warning("No common prefix found in worksheet names")
        return

    # Read current .env file
    env_path = Path(env_file)
    if not env_path.exists():
        logger.warning(f"Environment file {env_file} not found")
        return

    with open(env_path, 'r') as f:
        env_content = f.read()

    # Check current HU_CODE
    current_hu_code = None
    for line in env_content.split('\n'):
        if line.startswith('HU_CODE='):
            current_hu_code = line.split('=', 1)[1].strip()
            break

    if current_hu_code == most_common_prefix:
        logger.info(f"HU_CODE is already correctly set to: {current_hu_code}")
        return

    # Update HU_CODE
    if current_hu_code:
        new_content = env_content.replace(f'HU_CODE={current_hu_code}', f'HU_CODE={most_common_prefix}')
    else:
        new_content = env_content + f'\nHU_CODE={most_common_prefix}'

    with open(env_path, 'w') as f:
        f.write(new_content)

    logger.info(f"Updated HU_CODE from '{current_hu_code}' to '{most_common_prefix}'")


def print_analysis_report(analysis: dict):
    """Print a comprehensive analysis report."""
    print("=" * 60)
    print("HU CONFIGURATION ANALYSIS REPORT")
    print("=" * 60)

    print(f"\n📊 GENERAL INFO:")
    print(f"   Total worksheets: {analysis['total_worksheets']}")
    print(f"   HU links found: {analysis['hu_count']}")

    print(f"\n🏷️  WORKSHEET PREFIX ANALYSIS:")
    print(f"   Most common prefix: {analysis['most_common_prefix']}")
    print(f"   Prefix distribution:")
    for prefix, count in sorted(analysis['prefix_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"     {prefix}: {count} worksheets")

    print(f"\n📋 SAMPLE WORKSHEETS WITH PREFIX {analysis['most_common_prefix']}:")
    prefix_sheets = [m[2] for m in analysis['pattern_matches'] if m[0] == analysis['most_common_prefix']]
    for sheet in prefix_sheets[:10]:  # Show first 10
        print(f"   {sheet}")
    if len(prefix_sheets) > 10:
        print(f"   ... and {len(prefix_sheets) - 10} more")

    print(f"\n🔗 HU LINKS SAMPLE (first 5):")
    for i, (hu_code, link) in enumerate(list(analysis['hu_links'].items())[:5]):
        print(f"   {hu_code}: {link}")

    print(f"\n📈 NUMBER RANGE FOR {analysis['most_common_prefix']}:")
    numbers = [m[1] for m in analysis['pattern_matches'] if m[0] == analysis['most_common_prefix']]
    if numbers:
        print(f"   Range: {min(numbers)} - {max(numbers)}")
        print(f"   Total in range: {len(numbers)}")

    print("\n" + "=" * 60)


def main():
    """Main function to run the HU configuration analysis."""
    excel_path = 'data/USERNAME.xlsx'

    if not Path(excel_path).exists():
        logger.error(f"Excel file not found: {excel_path}")
        return

    # Analyze Excel structure
    analysis = analyze_excel_structure(excel_path)

    # Print report
    print_analysis_report(analysis)

    # Update HU_CODE if needed
    update_hu_code_if_needed(analysis)

    # Summary
    print("✅ ANALYSIS COMPLETE")
    print(f"   Found {analysis['hu_count']} HU links")
    print(f"   Identified prefix: {analysis['most_common_prefix']}")
    print("   HU_CODE updated in .env file if necessary")

if __name__ == "__main__":
    main()