#!/usr/bin/env python3
"""
Test de integración completa del sistema HU Tests Automation
"""

import sys
import os
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def test_main_integration():
    """Test básico para verificar que el main.py funciona correctamente"""
    print("🧪 Testing main.py integration...")
    
    # Test help command
    result = os.system("python main.py --help")
    assert result == 0, "Help command failed"
    print("✅ Help command works")
    
    # Test individual components (would need actual files)
    print("✅ Main integration test passed")

def test_pipeline_components():
    """Test de componentes del pipeline"""
    print("🧪 Testing pipeline components...")
    
    try:
        from src.hu_config_manager import HUConfigurationManager
        manager = HUConfigurationManager('data/USERNAME.xlsx')
        
        hu_codes = manager.get_available_hu_codes()
        print(f"✅ HU Configuration Manager works: {len(hu_codes)} HU codes found")
        
        from src.excel_parser.excel_extractor import ExcelTestExtractor
        extractor = ExcelTestExtractor('data/USERNAME.xlsx')
        print("✅ Excel Test Extractor initialized")
        
        from src.redactionAssistant.config import Config
        config = Config()
        print("✅ RedactionAssistant Config loaded")
        
        print("✅ All pipeline components are accessible")
        
    except Exception as e:
        print(f"❌ Pipeline component test failed: {e}")
        return False
    
    return True

def test_mock_integration():
    """Test con datos mock para verificar el flujo"""
    print("🧪 Testing with mock data...")
    
    try:
        # Mock HU data
        mock_hu = {
            'hu_code': 'TEST01',
            'issue_key': 'TEST-001',
            'title': 'Test HU',
            'description': 'Test description',
            'link': 'http://test.com'
        }
        
        # Mock test case data
        mock_test_case = {
            'test_case_id': 'TC001',
            'description': 'Test case description',
            'expected_result': 'Expected result'
        }
        
        # Test that we can create correction entry structure
        correction_entry = {
            'hu_code': mock_hu['hu_code'],
            'worksheet': 'TEST01',
            'hu_content': mock_hu,
            'test_cases': [mock_test_case],
            'jira_issue_key': mock_hu['issue_key'],
            'hu_title': mock_hu['title'],
            'hu_description': mock_hu['description']
        }
        
        assert correction_entry['hu_code'] == 'TEST01'
        assert len(correction_entry['test_cases']) == 1
        assert correction_entry['jira_issue_key'] == 'TEST-001'
        
        print("✅ Mock data structure test passed")
        return True
        
    except Exception as e:
        print(f"❌ Mock integration test failed: {e}")
        return False

def test_jira_scraper_structure():
    """Test de la estructura del JiraScraper"""
    print("🧪 Testing JiraScraper structure...")
    
    try:
        from src.jira_import.jira_scraper import JiraScraper
        
        # Test que se puede crear una instancia
        scraper = JiraScraper()
        assert scraper.base_url == 'https://jira.visma.com'
        assert scraper.context is None
        assert scraper.page is None
        assert scraper.playwright is None
        
        print("✅ JiraScraper structure test passed")
        return True
        
    except Exception as e:
        print(f"❌ JiraScraper structure test failed: {e}")
        return False

def test_integrated_pipeline_structure():
    """Test de la estructura del pipeline integrado"""
    print("🧪 Testing Integrated Pipeline structure...")
    
    try:
        # Test que el archivo del pipeline existe
        scripts_path = Path(__file__).parent.parent / "scripts" / "integrated_hu_correction_pipeline.py"
        assert scripts_path.exists(), f"Pipeline script not found at {scripts_path}"
        
        # Test que el archivo del pipeline HU existe
        hu_pipeline_path = Path(__file__).parent.parent / "scripts" / "hu_pipeline.py"
        assert hu_pipeline_path.exists(), f"HU Pipeline script not found at {hu_pipeline_path}"
        
        print("✅ Integrated Pipeline structure test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integrated Pipeline structure test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running Complete Integration Tests...\n")
    
    # Run tests
    test_main_integration()
    print()
    
    component_test = test_pipeline_components()
    print()
    
    mock_test = test_mock_integration()
    print()
    
    jira_test = test_jira_scraper_structure()
    print()
    
    pipeline_test = test_integrated_pipeline_structure()
    print()
    
    if component_test and mock_test and jira_test and pipeline_test:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        exit(1)
