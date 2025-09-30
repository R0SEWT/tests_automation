#!/usr/bin/env python3
"""
Demo: Excel Corrector with Mocked API Calls

This script demonstrates how to use the ExcelCorrector to generate corrected
copies of Excel files containing test cases and expected results.

The demo creates a sample Excel file, processes it with mocked corrections,
and generates a highlighted corrected version.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import logging
from src.excel_parser.excel_corrector import ExcelCorrector, generate_corrected_excel_file
from src.core.utils import Logger

# Setup logging
logger = Logger.setup_logger(__name__)


def create_sample_excel_file(output_path: str) -> str:
    """
    Create a sample Excel file with test cases for demonstration.
    
    Args:
        output_path: Path where to create the sample file
        
    Returns:
        Path to the created sample file
    """
    logger.info("Creating sample Excel file for demonstration...")
    
    # Sample test cases with intentional errors for correction
    sample_data = {
        'Test Case ID': [
            'USRNM01 - CP01',
            'USRNM01 - CP02', 
            'USRNM01 - CP03',
            'USRNM01 - CP04',
            'USRNM01 - CP05'
        ],
        'Description': [
            'Como superadmin, En el formulario de creacion de una empresa, Se añadira un card',
            'Como superadmin, En el formulario de creacion de una empresa, el card tendra nombre "Management"',
            'Como superadmin, En el formulario de creacion, verificar que el switch estara activado',
            'Como superadmin, validar que el modal aparecera cuando se active el switch',
            'Como BP, verificar que en la importacion se guardaran los datos'
        ],
        'Expected Result': [
            'Se añade un card que se encontrara debajo de Correos',
            'el card tiene nombre "Management"',
            'el switch estara activado por default',
            'cuando se active el switch, aparecera un modal de confirmacion',
            'Se guardan los datos correspondientes a la accion'
        ],
        'Test Step': [
            'Estar en el formulario de creación de empresa',
            'Estar en el formulario de creación de empresa',  
            'Estar en el formulario de creación',
            'Estar en el formulario de edición',
            'Importar colaborador'
        ],
        'Test Data': [
            'Verificar en google chrome',
            'Verificar en google chrome',
            'Verificar en google chrome', 
            'Verificar en google chrome',
            'Verificar en Google Chrome'
        ],
        'Epic Link': [
            'VLPER-89221',
            'VLPER-89221',
            'VLPER-89221',
            'VLPER-89221', 
            'VLPER-89221'
        ],
        'Estado Qa': [
            'Conforme',
            'Conforme',
            'Conforme',
            'Conforme',
            'Conforme'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(sample_data)
    
    # Create Excel file with multiple worksheets
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with pd.ExcelWriter(str(output_file), engine='openpyxl') as writer:
        # Create multiple worksheets with variations
        df.to_excel(writer, sheet_name='USRNM01', index=False)
        
        # Create a second worksheet with more sample data
        df2 = df.copy()
        df2['Test Case ID'] = df2['Test Case ID'].str.replace('USRNM01', 'USRNM02')
        df2['Description'] = df2['Description'].str.replace('USRNM01', 'USRNM02')
        df2.to_excel(writer, sheet_name='USRNM02', index=False)
        
        # Create a third worksheet
        df3 = df.copy()
        df3['Test Case ID'] = df3['Test Case ID'].str.replace('USRNM01', 'USRNM03')
        df3['Description'] = df3['Description'].str.replace('USRNM01', 'USRNM03')
        df3.to_excel(writer, sheet_name='USRNM03', index=False)
    
    logger.info("Sample Excel file created: %s", output_file)
    return str(output_file)


def demonstrate_excel_correction():
    """Demonstrate the Excel correction functionality."""
    logger.info("🚀 Starting Excel Correction Demo")
    logger.info("=" * 50)
    
    # Create output directory
    demo_dir = Path("output/excel_correction_demo")
    demo_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Create sample Excel file
        logger.info("📊 Step 1: Creating sample Excel file with test cases...")
        sample_file = create_sample_excel_file(str(demo_dir / "sample_test_cases.xlsx"))
        
        # Step 2: Initialize Excel Corrector
        logger.info("🔧 Step 2: Initializing Excel Corrector with mocked API...")
        corrector = ExcelCorrector(sample_file, use_mock=True)
        
        # Step 3: Process corrections
        logger.info("⚡ Step 3: Processing corrections for all worksheets...")
        correction_results = corrector.process_corrections()
        
        # Display results summary
        logger.info("📈 Correction Results Summary:")
        logger.info(f"  • Total worksheets processed: {correction_results['total_worksheets']}")
        logger.info(f"  • Total test cases processed: {correction_results['total_test_cases']}")
        logger.info(f"  • Total corrections applied: {correction_results['total_corrections']}")
        
        # Step 4: Generate corrected Excel file
        logger.info("📝 Step 4: Generating corrected Excel file with highlighting...")
        corrected_file_path = corrector.generate_corrected_excel(
            output_path=str(demo_dir / "sample_test_cases_corrected.xlsx"),
            highlight_changes=True
        )
        
        logger.info("✅ Corrected Excel file generated: %s", corrected_file_path)
        
        # Step 5: Display detailed correction information
        logger.info("🔍 Step 5: Detailed correction breakdown:")
        for worksheet_name, worksheet_data in correction_results['corrections_by_worksheet'].items():
            logger.info(f"  📋 Worksheet: {worksheet_name}")
            logger.info(f"    • Original test cases: {worksheet_data['original_count']}")
            logger.info(f"    • Corrections applied: {worksheet_data['corrections_applied']}")
            
            # Show sample corrections
            sample_corrections = []
            for tc in worksheet_data['corrected_test_cases'][:2]:  # Show first 2
                if tc.get('description_original') != tc.get('description'):
                    sample_corrections.append({
                        'type': 'Description',
                        'original': tc.get('description_original', '')[:60] + "...",
                        'corrected': tc.get('description', '')[:60] + "..."
                    })
                if tc.get('expected_result_original') != tc.get('expected_result'):
                    sample_corrections.append({
                        'type': 'Expected Result', 
                        'original': tc.get('expected_result_original', '')[:60] + "...",
                        'corrected': tc.get('expected_result', '')[:60] + "..."
                    })
            
            if sample_corrections:
                logger.info("    📝 Sample corrections:")
                for correction in sample_corrections[:2]:  # Show max 2 samples
                    logger.info(f"      • {correction['type']}:")
                    logger.info(f"        Before: {correction['original']}")
                    logger.info(f"        After:  {correction['corrected']}")
        
        # Step 6: Demonstrate convenience function
        logger.info("🎯 Step 6: Demonstrating convenience function...")
        convenience_corrected_file, convenience_results = generate_corrected_excel_file(
            original_file_path=sample_file,
            output_path=str(demo_dir / "convenience_corrected.xlsx"),
            highlight_changes=True,
            use_mock=True
        )
        
        logger.info("✅ Convenience function completed: %s", convenience_corrected_file)
        
        # Step 7: Show generated files
        logger.info("📁 Generated files:")
        for file_path in demo_dir.iterdir():
            if file_path.is_file():
                logger.info(f"  • {file_path.name} ({file_path.stat().st_size} bytes)")
        
        logger.info("=" * 50)
        logger.info("🎉 Excel Correction Demo completed successfully!")
        logger.info("📂 Check the output directory: %s", demo_dir.absolute())
        
        return True
        
    except Exception as e:
        logger.error("❌ Demo failed with error: %s", e)
        import traceback
        logger.error("Traceback:\n%s", traceback.format_exc())
        return False


def demonstrate_with_real_file(file_path: str):
    """
    Demonstrate Excel correction with a real file.
    
    Args:
        file_path: Path to the real Excel file to process
    """
    logger.info("🎯 Processing real Excel file: %s", file_path)
    
    if not Path(file_path).exists():
        logger.error("❌ File not found: %s", file_path)
        return False
    
    try:
        output_dir = Path("output/real_file_correction")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate corrected file
        corrected_file, results = generate_corrected_excel_file(
            original_file_path=file_path,
            output_path=str(output_dir / f"{Path(file_path).stem}_corrected.xlsx"),
            highlight_changes=True,
            use_mock=True
        )
        
        logger.info("✅ Real file correction completed!")
        logger.info("📊 Results: %d worksheets, %d test cases, %d corrections", 
                   results['total_worksheets'], 
                   results['total_test_cases'], 
                   results['total_corrections'])
        logger.info("📝 Corrected file: %s", corrected_file)
        
        return True
        
    except Exception as e:
        logger.error("❌ Real file processing failed: %s", e)
        return False


if __name__ == "__main__":
    print("🔧 Excel Corrector Demo")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        # Process real file if provided as argument
        real_file_path = sys.argv[1]
        print(f"Processing real file: {real_file_path}")
        success = demonstrate_with_real_file(real_file_path)
    else:
        # Run demonstration with sample data
        print("Running demonstration with sample data...")
        success = demonstrate_excel_correction()
    
    if success:
        print("\n✅ Demo completed successfully!")
        print("📂 Check the 'output' directory for generated files.")
    else:
        print("\n❌ Demo failed. Check the logs for details.")
        sys.exit(1)