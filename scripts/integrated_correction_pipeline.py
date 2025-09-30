#!/usr/bin/env python3
"""
Integrated Correction Pipeline

Complete pipeline that combines HU extraction, test case processing, corrections,
and Excel file generation with mocked API calls.

This script demonstrates the full workflow:
1. Extract HU content and test cases from Excel
2. Process corrections using mocked API calls
3. Generate corrected Excel file with highlighting
4. Provide comprehensive reporting

Usage:
    python scripts/integrated_correction_pipeline.py [excel_file_path]
"""

import sys
import asyncio
from pathlib import Path
import json
import logging
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.excel_parser.excel_corrector import ExcelCorrector, generate_corrected_excel_file
from src.excel_parser.excel_extractor import ExcelTestExtractor
from src.core.utils import Logger
from scripts.integrated_hu_correction_pipeline import IntegratedHUCorrectionPipeline

logger = Logger.setup_logger(__name__)


class FullIntegratedCorrectionPipeline:
    """
    Complete integrated pipeline for Excel test case correction.
    
    Combines HU extraction, test case processing, AI-powered corrections,
    and corrected Excel file generation in a single workflow.
    """
    
    def __init__(self, excel_path: str = 'data/USERNAME.xlsx'):
        """
        Initialize the integrated pipeline.
        
        Args:
            excel_path: Path to the Excel file containing test cases
        """
        self.excel_path = Path(excel_path)
        self.logger = logger
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        # Initialize components
        self.hu_pipeline = IntegratedHUCorrectionPipeline(str(excel_path))
        self.excel_corrector = ExcelCorrector(str(excel_path), use_mock=True)
        self.extractor = ExcelTestExtractor(str(excel_path))
    
    async def run_complete_pipeline(self, output_dir: str = 'output/integrated_correction') -> dict:
        """
        Execute the complete integrated correction pipeline.
        
        Args:
            output_dir: Directory to save all output files
            
        Returns:
            Dictionary containing comprehensive results from all pipeline stages
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("🚀 Starting Full Integrated Correction Pipeline")
        self.logger.info("=" * 60)
        
        pipeline_results = {
            'success': False,
            'excel_file': str(self.excel_path),
            'output_directory': str(output_path),
            'stages': {}
        }
        
        try:
            # Stage 1: HU Content Extraction and Processing
            self.logger.info("📊 Stage 1: HU Content Extraction and Processing")
            hu_results = await self.hu_pipeline.run_hu_extraction_pipeline(batch_size=5)
            pipeline_results['stages']['hu_extraction'] = hu_results
            
            self.logger.info("✅ HU extraction completed:")
            self.logger.info(f"  • HUs configured: {hu_results.get('config_analysis', {}).get('total_hus', 0)}")
            self.logger.info(f"  • Test cases extracted: {hu_results.get('test_cases_extracted', 0)}")
            self.logger.info(f"  • HUs with content: {hu_results.get('hu_content_extracted', 0)}")
            
            # Stage 2: RedactionAssistant Corrections (Mocked)
            self.logger.info("\n🔧 Stage 2: AI-Powered Corrections (Mocked)")
            correction_results = self.hu_pipeline.process_corrections()
            pipeline_results['stages']['ai_corrections'] = correction_results
            
            self.logger.info("✅ AI corrections completed:")
            self.logger.info(f"  • Corrections processed: {len(correction_results.get('corrections', {}))}")
            
            # Save correction results
            correction_file = output_path / "ai_correction_results.json"
            with open(correction_file, 'w', encoding='utf-8') as f:
                json.dump(correction_results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"  • Correction results saved: {correction_file}")
            
            # Stage 3: Excel File Correction
            self.logger.info("\n📝 Stage 3: Excel File Correction and Generation")
            excel_correction_results = self.excel_corrector.process_corrections()
            pipeline_results['stages']['excel_correction'] = excel_correction_results
            
            self.logger.info("✅ Excel correction analysis:")
            self.logger.info(f"  • Worksheets processed: {excel_correction_results['total_worksheets']}")
            self.logger.info(f"  • Test cases processed: {excel_correction_results['total_test_cases']}")
            self.logger.info(f"  • Corrections applied: {excel_correction_results['total_corrections']}")
            
            # Stage 4: Generate Corrected Excel File
            self.logger.info("\n💾 Stage 4: Generate Corrected Excel File")
            corrected_excel_path = self.excel_corrector.generate_corrected_excel(
                output_path=str(output_path / f"{self.excel_path.stem}_CORRECTED.xlsx"),
                highlight_changes=True
            )
            pipeline_results['stages']['excel_generation'] = {
                'corrected_file_path': corrected_excel_path,
                'highlighting_enabled': True
            }
            
            self.logger.info(f"✅ Corrected Excel file generated: {corrected_excel_path}")
            
            # Stage 5: Generate Comprehensive Report
            self.logger.info("\n📋 Stage 5: Generate Comprehensive Report")
            report_data = self._generate_comprehensive_report(pipeline_results)
            report_file = output_path / "comprehensive_report.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            pipeline_results['stages']['reporting'] = {
                'report_file': str(report_file),
                'report_data': report_data
            }
            
            self.logger.info(f"✅ Comprehensive report saved: {report_file}")
            
            # Stage 6: Summary and Statistics
            self.logger.info("\n📈 Stage 6: Pipeline Summary and Statistics")
            summary = self._generate_pipeline_summary(pipeline_results)
            pipeline_results['summary'] = summary
            
            self._display_pipeline_summary(summary)
            
            pipeline_results['success'] = True
            self.logger.info("\n🎉 Full Integrated Correction Pipeline completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed at stage: {e}")
            pipeline_results['error'] = str(e)
            import traceback
            self.logger.error("Traceback:\n%s", traceback.format_exc())
        
        return pipeline_results
    
    def _generate_comprehensive_report(self, pipeline_results: dict) -> dict:
        """Generate a comprehensive report of the entire pipeline."""
        report = {
            'pipeline_info': {
                'excel_file': pipeline_results['excel_file'],
                'output_directory': pipeline_results['output_directory'],
                'timestamp': pd.Timestamp.now().isoformat(),
                'success': pipeline_results['success']
            },
            'stage_results': {},
            'metrics': {},
            'recommendations': []
        }
        
        # Extract metrics from each stage
        if 'hu_extraction' in pipeline_results['stages']:
            hu_data = pipeline_results['stages']['hu_extraction']
            report['stage_results']['hu_extraction'] = {
                'total_hus': hu_data.get('config_analysis', {}).get('total_hus', 0),
                'test_cases_extracted': hu_data.get('test_cases_extracted', 0),
                'hu_content_extracted': hu_data.get('hu_content_extracted', 0)
            }
        
        if 'excel_correction' in pipeline_results['stages']:
            excel_data = pipeline_results['stages']['excel_correction']
            report['stage_results']['excel_correction'] = {
                'worksheets_processed': excel_data['total_worksheets'],
                'test_cases_processed': excel_data['total_test_cases'],
                'corrections_applied': excel_data['total_corrections']
            }
        
        # Calculate overall metrics
        total_test_cases = report['stage_results'].get('excel_correction', {}).get('test_cases_processed', 0)
        total_corrections = report['stage_results'].get('excel_correction', {}).get('corrections_applied', 0)
        
        report['metrics'] = {
            'correction_rate': (total_corrections / total_test_cases * 100) if total_test_cases > 0 else 0,
            'avg_corrections_per_test_case': (total_corrections / total_test_cases) if total_test_cases > 0 else 0,
            'processing_efficiency': 'High' if total_corrections > 1000 else 'Medium' if total_corrections > 500 else 'Low'
        }
        
        # Generate recommendations
        if total_corrections > 1000:
            report['recommendations'].append("High number of corrections detected. Consider reviewing test case writing guidelines.")
        
        if report['metrics']['correction_rate'] > 80:
            report['recommendations'].append("Very high correction rate. Consider implementing automated quality checks during test case creation.")
        
        report['recommendations'].append("Use the corrected Excel file as the new master version for future test executions.")
        report['recommendations'].append("Review the highlighted corrections to identify common improvement patterns.")
        
        return report
    
    def _generate_pipeline_summary(self, pipeline_results: dict) -> dict:
        """Generate a concise summary of pipeline execution."""
        summary = {
            'execution_status': 'SUCCESS' if pipeline_results['success'] else 'FAILED',
            'stages_completed': len([stage for stage, data in pipeline_results.get('stages', {}).items() if data]),
            'total_stages': 6,
            'key_metrics': {}
        }
        
        # Extract key metrics
        excel_data = pipeline_results.get('stages', {}).get('excel_correction', {})
        if excel_data:
            summary['key_metrics'] = {
                'worksheets': excel_data.get('total_worksheets', 0),
                'test_cases': excel_data.get('total_test_cases', 0),
                'corrections': excel_data.get('total_corrections', 0),
                'correction_percentage': round((excel_data.get('total_corrections', 0) / excel_data.get('total_test_cases', 1)) * 100, 2)
            }
        
        return summary
    
    def _display_pipeline_summary(self, summary: dict):
        """Display a formatted summary of the pipeline execution."""
        self.logger.info("📊 PIPELINE EXECUTION SUMMARY")
        self.logger.info("-" * 40)
        self.logger.info(f"Status: {summary['execution_status']}")
        self.logger.info(f"Stages Completed: {summary['stages_completed']}/{summary['total_stages']}")
        
        if summary['key_metrics']:
            metrics = summary['key_metrics']
            self.logger.info(f"📋 Worksheets Processed: {metrics.get('worksheets', 0)}")
            self.logger.info(f"🧪 Test Cases Processed: {metrics.get('test_cases', 0)}")
            self.logger.info(f"✏️  Corrections Applied: {metrics.get('corrections', 0)}")
            self.logger.info(f"📈 Correction Rate: {metrics.get('correction_percentage', 0)}%")


async def main():
    """Main function for the integrated correction pipeline."""
    
    # Determine Excel file path
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        excel_file = 'data/USERNAME.xlsx'
    
    if not Path(excel_file).exists():
        print(f"❌ Excel file not found: {excel_file}")
        print("Usage: python scripts/integrated_correction_pipeline.py [excel_file_path]")
        return False
    
    try:
        # Initialize and run pipeline
        pipeline = FullIntegratedCorrectionPipeline(excel_file)
        results = await pipeline.run_complete_pipeline()
        
        if results['success']:
            print(f"\n✅ Pipeline completed successfully!")
            print(f"📂 Check output directory: {results['output_directory']}")
            
            # Display quick stats
            excel_data = results.get('stages', {}).get('excel_correction', {})
            if excel_data:
                print(f"📊 Quick Stats:")
                print(f"  • {excel_data.get('total_worksheets', 0)} worksheets processed")
                print(f"  • {excel_data.get('total_test_cases', 0)} test cases analyzed")
                print(f"  • {excel_data.get('total_corrections', 0)} corrections applied")
                
                if 'excel_generation' in results['stages']:
                    corrected_file = results['stages']['excel_generation']['corrected_file_path']
                    print(f"  • Corrected file: {Path(corrected_file).name}")
            
            return True
        else:
            print(f"\n❌ Pipeline failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔧 Full Integrated Correction Pipeline")
    print("=" * 50)
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 All operations completed successfully!")
    else:
        print("\n💥 Pipeline execution failed.")
        sys.exit(1)