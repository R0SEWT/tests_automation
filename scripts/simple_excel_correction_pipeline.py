#!/usr/bin/env python3
"""
Simplified Excel Correction Demo

Demonstrates Excel correction functionality without dependencies on
the HU pipeline or OpenAI modules.

This script focuses purely on Excel file correction and generation.
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

logger = Logger.setup_logger(__name__)


class SimplifiedExcelCorrectionPipeline:
    """
    Simplified pipeline focused on Excel correction functionality.
    
    This pipeline demonstrates the complete Excel correction workflow
    without dependencies on external API modules.
    """
    
    def __init__(self, excel_path: str = 'data/USERNAME.xlsx'):
        """
        Initialize the simplified pipeline.
        
        Args:
            excel_path: Path to the Excel file containing test cases
        """
        self.excel_path = Path(excel_path)
        self.logger = logger
        
        if not self.excel_path.exists():
            raise FileNotFoundError(f"Excel file not found: {excel_path}")
        
        # Initialize components
        self.excel_corrector = ExcelCorrector(str(excel_path), use_mock=True)
        self.extractor = ExcelTestExtractor(str(excel_path))
    
    async def run_excel_correction_pipeline(self, output_dir: str = 'output/excel_correction_pipeline') -> dict:
        """
        Execute the Excel correction pipeline.
        
        Args:
            output_dir: Directory to save all output files
            
        Returns:
            Dictionary containing comprehensive results from the pipeline
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("🚀 Starting Simplified Excel Correction Pipeline")
        self.logger.info("=" * 60)
        
        pipeline_results = {
            'success': False,
            'excel_file': str(self.excel_path),
            'output_directory': str(output_path),
            'stages': {}
        }
        
        try:
            # Stage 1: Excel Analysis
            self.logger.info("📊 Stage 1: Excel File Analysis")
            analysis_results = self._analyze_excel_file()
            pipeline_results['stages']['analysis'] = analysis_results
            
            self.logger.info("✅ Excel analysis completed:")
            self.logger.info(f"  • Worksheets found: {analysis_results['total_worksheets']}")
            self.logger.info(f"  • Test cases found: {analysis_results['total_test_cases']}")
            
            # Save analysis results
            analysis_file = output_path / "excel_analysis.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"  • Analysis saved: {analysis_file}")
            
            # Stage 2: Excel Correction Processing
            self.logger.info("\n🔧 Stage 2: Excel Correction Processing")
            correction_results = self.excel_corrector.process_corrections()
            pipeline_results['stages']['correction'] = correction_results
            
            self.logger.info("✅ Correction processing completed:")
            self.logger.info(f"  • Worksheets processed: {correction_results['total_worksheets']}")
            self.logger.info(f"  • Test cases processed: {correction_results['total_test_cases']}")
            self.logger.info(f"  • Corrections applied: {correction_results['total_corrections']}")
            
            # Stage 3: Generate Corrected Excel File
            self.logger.info("\n📝 Stage 3: Generate Corrected Excel File")
            corrected_excel_path = self.excel_corrector.generate_corrected_excel(
                output_path=str(output_path / f"{self.excel_path.stem}_CORRECTED.xlsx"),
                highlight_changes=True
            )
            pipeline_results['stages']['generation'] = {
                'corrected_file_path': corrected_excel_path,
                'highlighting_enabled': True
            }
            
            self.logger.info(f"✅ Corrected Excel file generated: {corrected_excel_path}")
            
            # Stage 4: Quality Analysis
            self.logger.info("\n📋 Stage 4: Quality Analysis and Reporting")
            quality_report = self._generate_quality_analysis(correction_results)
            quality_file = output_path / "quality_analysis.json"
            
            with open(quality_file, 'w', encoding='utf-8') as f:
                json.dump(quality_report, f, indent=2, ensure_ascii=False)
            
            pipeline_results['stages']['quality_analysis'] = {
                'report_file': str(quality_file),
                'report_data': quality_report
            }
            
            self.logger.info(f"✅ Quality analysis saved: {quality_file}")
            
            # Stage 5: Pipeline Summary
            self.logger.info("\n📈 Stage 5: Pipeline Summary")
            summary = self._generate_pipeline_summary(pipeline_results)
            pipeline_results['summary'] = summary
            
            self._display_pipeline_summary(summary)
            
            # Save complete pipeline results
            results_file = output_path / "pipeline_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(pipeline_results, f, indent=2, ensure_ascii=False, default=str)
            
            pipeline_results['success'] = True
            self.logger.info("\n🎉 Simplified Excel Correction Pipeline completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            pipeline_results['error'] = str(e)
            import traceback
            self.logger.error("Traceback:\n%s", traceback.format_exc())
        
        return pipeline_results
    
    def _analyze_excel_file(self) -> dict:
        """Analyze the Excel file structure and content."""
        all_test_cases = self.extractor.extract_all_test_cases()
        
        analysis = {
            'file_path': str(self.excel_path),
            'file_size_bytes': self.excel_path.stat().st_size,
            'total_worksheets': len(all_test_cases),
            'total_test_cases': sum(len(cases) for cases in all_test_cases.values()),
            'worksheet_details': {},
            'column_analysis': {},
            'data_quality_indicators': {}
        }
        
        # Analyze each worksheet
        for worksheet_name, test_cases in all_test_cases.items():
            analysis['worksheet_details'][worksheet_name] = {
                'test_case_count': len(test_cases),
                'has_descriptions': sum(bool(tc.get('description', '').strip())
                'has_expected_results': sum(1 for tc in test_cases if tc.get('expected_result', '').strip()),
                'additional_columns': len(test_cases[0].get('additional_data', {})) if test_cases else 0
            }
        
        # Calculate quality indicators
        total_with_descriptions = sum(ws['has_descriptions'] for ws in analysis['worksheet_details'].values())
        total_with_expected = sum(ws['has_expected_results'] for ws in analysis['worksheet_details'].values())
        
        analysis['data_quality_indicators'] = {
            'completeness_rate': (total_with_descriptions / analysis['total_test_cases'] * 100) if analysis['total_test_cases'] > 0 else 0,
            'expected_results_rate': (total_with_expected / analysis['total_test_cases'] * 100) if analysis['total_test_cases'] > 0 else 0,
            'data_density': 'High' if analysis['total_test_cases'] > 1000 else 'Medium' if analysis['total_test_cases'] > 500 else 'Low'
        }
        
        return analysis
    
    def _generate_quality_analysis(self, correction_results: dict) -> dict:
        """Generate quality analysis based on correction results."""
        quality_analysis = {
            'overall_quality': {},
            'correction_patterns': {},
            'worksheet_quality': {},
            'recommendations': []
        }
        
        # Overall quality metrics
        total_test_cases = correction_results['total_test_cases']
        total_corrections = correction_results['total_corrections']
        
        correction_rate = (total_corrections / total_test_cases * 100) if total_test_cases > 0 else 0
        
        quality_analysis['overall_quality'] = {
            'correction_rate_percentage': round(correction_rate, 2),
            'quality_score': self._calculate_quality_score(correction_rate),
            'total_test_cases': total_test_cases,
            'total_corrections': total_corrections,
            'avg_corrections_per_test_case': round(total_corrections / total_test_cases, 2) if total_test_cases > 0 else 0
        }
        
        # Worksheet-level quality analysis
        for worksheet_name, worksheet_data in correction_results['corrections_by_worksheet'].items():
            original_count = worksheet_data['original_count']
            corrections_applied = worksheet_data['corrections_applied']
            worksheet_correction_rate = (corrections_applied / original_count * 100) if original_count > 0 else 0
            
            quality_analysis['worksheet_quality'][worksheet_name] = {
                'correction_rate': round(worksheet_correction_rate, 2),
                'quality_level': self._get_quality_level(worksheet_correction_rate),
                'original_test_cases': original_count,
                'corrections_applied': corrections_applied
            }
        
        # Generate recommendations
        quality_analysis['recommendations'] = self._generate_quality_recommendations(quality_analysis)
        
        return quality_analysis
    
    def _calculate_quality_score(self, correction_rate: float) -> str:
        """Calculate quality score based on correction rate."""
        if correction_rate < 20:
            return "Excellent"
        elif correction_rate < 50:
            return "Good"
        elif correction_rate < 80:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _get_quality_level(self, correction_rate: float) -> str:
        """Get quality level for a worksheet."""
        if correction_rate < 30:
            return "High Quality"
        elif correction_rate < 60:
            return "Medium Quality"
        else:
            return "Low Quality"
    
    def _generate_quality_recommendations(self, quality_analysis: dict) -> list:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        overall_correction_rate = quality_analysis['overall_quality']['correction_rate_percentage']
        
        if overall_correction_rate > 70:
            recommendations.append("High correction rate detected. Consider implementing quality checkpoints during test case creation.")
            recommendations.append("Review common correction patterns to create a style guide for test case writing.")
        
        if overall_correction_rate > 50:
            recommendations.append("Consider providing training on technical writing for test case authors.")
        
        # Identify worst performing worksheets
        worksheet_qualities = quality_analysis['worksheet_quality']
        high_correction_worksheets = [
            ws for ws, data in worksheet_qualities.items() 
            if data['correction_rate'] > 80
        ]
        
        if high_correction_worksheets:
            recommendations.append(f"Focus improvement efforts on worksheets: {', '.join(high_correction_worksheets[:3])}")
        
        recommendations.append("Use the corrected Excel file as the new baseline for future test case development.")
        recommendations.append("Implement automated spell-checking in test case creation tools.")
        
        return recommendations
    
    def _generate_pipeline_summary(self, pipeline_results: dict) -> dict:
        """Generate a concise summary of pipeline execution."""
        summary = {
            'execution_status': 'SUCCESS' if pipeline_results['success'] else 'FAILED',
            'stages_completed': len([stage for stage, data in pipeline_results.get('stages', {}).items() if data]),
            'total_stages': 5,
            'key_metrics': {}
        }
        
        # Extract key metrics
        correction_data = pipeline_results.get('stages', {}).get('correction', {})
        if correction_data:
            summary['key_metrics'] = {
                'worksheets': correction_data.get('total_worksheets', 0),
                'test_cases': correction_data.get('total_test_cases', 0),
                'corrections': correction_data.get('total_corrections', 0),
                'correction_percentage': round((correction_data.get('total_corrections', 0) / correction_data.get('total_test_cases', 1)) * 100, 2)
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
    """Main function for the simplified correction pipeline."""
    
    # Determine Excel file path
    if len(sys.argv) > 1:
        excel_file = sys.argv[1]
    else:
        excel_file = 'data/USERNAME.xlsx'
    
    if not Path(excel_file).exists():
        print(f"❌ Excel file not found: {excel_file}")
        print("Usage: python scripts/simple_excel_correction_pipeline.py [excel_file_path]")
        return False
    
    try:
        # Initialize and run pipeline
        pipeline = SimplifiedExcelCorrectionPipeline(excel_file)
        results = await pipeline.run_excel_correction_pipeline()
        
        if results['success']:
            print(f"\n✅ Simplified pipeline completed successfully!")
            print(f"📂 Check output directory: {results['output_directory']}")
            
            # Display quick stats
            correction_data = results.get('stages', {}).get('correction', {})
            if correction_data:
                print(f"📊 Quick Stats:")
                print(f"  • {correction_data.get('total_worksheets', 0)} worksheets processed")
                print(f"  • {correction_data.get('total_test_cases', 0)} test cases analyzed")
                print(f"  • {correction_data.get('total_corrections', 0)} corrections applied")
                
                correction_rate = (correction_data.get('total_corrections', 0) / correction_data.get('total_test_cases', 1)) * 100
                print(f"  • Correction rate: {correction_rate:.1f}%")
                
                if 'generation' in results['stages']:
                    corrected_file = results['stages']['generation']['corrected_file_path']
                    print(f"  • Corrected file: {Path(corrected_file).name}")
            
            # Display quality insights
            quality_data = results.get('stages', {}).get('quality_analysis', {}).get('report_data', {})
            if quality_data:
                overall_quality = quality_data.get('overall_quality', {})
                quality_score = overall_quality.get('quality_score', 'Unknown')
                print(f"📈 Quality Assessment: {quality_score}")
                
                recommendations = quality_data.get('recommendations', [])
                if recommendations:
                    print(f"💡 Top Recommendation: {recommendations[0]}")
            
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
    print("🔧 Simplified Excel Correction Pipeline")
    print("=" * 50)
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 All operations completed successfully!")
        print("📋 Key outputs generated:")
        print("  • Corrected Excel file with highlighting")
        print("  • Quality analysis report")
        print("  • Excel structure analysis")
        print("  • Pipeline execution summary")
    else:
        print("\n💥 Pipeline execution failed.")
        sys.exit(1)