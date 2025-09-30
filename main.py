#!/usr/bin/env python3
"""
Main entry point for HU Tests Automation System

This script provides a command-line interface to run the main components
of the HU processing and correction system.
"""

import sys
import argparse
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="HU Tests Automation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --analyze                    # Analyze HU configuration
  python main.py --extract                    # Extract HU content
  python main.py --pipeline                   # Run processing pipeline
  python main.py --integrated                 # Run full integrated pipeline
  python main.py --demo                       # Demo Excel extraction
        """
    )
    
    parser.add_argument('--analyze', action='store_true', 
                       help='Analyze HU configuration from Excel')
    parser.add_argument('--extract', action='store_true',
                       help='Extract HU content from Jira')
    parser.add_argument('--pipeline', action='store_true',
                       help='Run HU processing pipeline')
    parser.add_argument('--integrated', action='store_true',
                       help='Run integrated HU correction pipeline')
    parser.add_argument('--demo', action='store_true',
                       help='Demo Excel test case extraction')
    parser.add_argument('--excel-path', default='data/USERNAME.xlsx',
                       help='Path to Excel configuration file')
    
    args = parser.parse_args()
    
    if not any([args.analyze, args.extract, args.pipeline, args.integrated, args.demo]):
        parser.print_help()
        return
    
    if args.analyze:
        print("🔍 Analyzing HU Configuration...")
        os.system("python examples/analyze_hu_config.py")
    
    elif args.extract:
        print("📥 Extracting HU Content...")
        os.system("python scripts/extract_hu_content.py")
    
    elif args.pipeline:
        print("🔄 Running HU Processing Pipeline...")
        os.system("python scripts/hu_pipeline.py")
    
    elif args.integrated:
        print("🚀 Running Integrated HU Correction Pipeline...")
        os.system("python scripts/integrated_hu_correction_pipeline.py")
    
    elif args.demo:
        print("🎯 Running Excel Extraction Demo...")
        os.system("python examples/demo_excel_extractor.py")


if __name__ == "__main__":
    main()