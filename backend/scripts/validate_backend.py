"""
Comprehensive Backend Validation Script for QuantFin System

This script validates the entire backend system including:
- Environment setup
- ML model training
- Prediction service
- FastAPI endpoints
- Backtester module
- Integration tests

Usage:
    python scripts/validate_backend.py [--quick] [--skip-ml] [--skip-api]

Author: QuantFin Team
Date: 2025-10-09
"""

import sys
import argparse
import logging
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackendValidator:
    """Comprehensive backend validation"""
    
    def __init__(self, quick: bool = False, skip_ml: bool = False, skip_api: bool = False):
        self.quick = quick
        self.skip_ml = skip_ml
        self.skip_api = skip_api
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
    def log_result(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """Log test result"""
        self.results['tests'][test_name] = {
            'passed': passed,
            'details': details,
            'duration': f"{duration:.2f}s"
        }
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name} ({duration:.2f}s)")
        if details:
            logger.info(f"  Details: {details}")
    
    def validate_environment(self) -> bool:
        """Step 1: Validate environment setup"""
        logger.info("\n" + "="*60)
        logger.info("STEP 1: Environment Validation")
        logger.info("="*60)
        
        start_time = time.time()
        errors = []
        
        try:
            # Check Python packages
            import pandas as pd
            import numpy as np
            import tensorflow as tf
            import sklearn
            import fastapi
            import uvicorn
            
            logger.info(f"✓ pandas: {pd.__version__}")
            logger.info(f"✓ numpy: {np.__version__}")
            logger.info(f"✓ tensorflow: {tf.__version__}")
            logger.info(f"✓ scikit-learn: {sklearn.__version__}")
            logger.info(f"✓ fastapi: {fastapi.__version__}")
            
            # Check GPU availability
            gpus = tf.config.list_physical_devices('GPU')
            if gpus:
                logger.info(f"✓ GPU available: {len(gpus)} device(s)")
                for gpu in gpus:
                    logger.info(f"  - {gpu.name}")
            else:
                logger.warning("⚠ No GPU detected, using CPU")
                self.results['warnings'].append("No GPU available - LSTM training will be slower")
            
            # Check directories
            data_dir = Path("data")
            models_dir = Path("models")
            
            if not data_dir.exists():
                errors.append("Data directory not found")
            else:
                csv_files = list(data_dir.glob("*.csv"))
                logger.info(f"✓ Data directory: {len(csv_files)} CSV files")
            
            if not models_dir.exists():
                models_dir.mkdir(parents=True)
                logger.info("✓ Created models directory")
            
            passed = len(errors) == 0
            duration = time.time() - start_time
            
            self.log_result(
                "Environment Setup",
                passed,
                f"Packages installed, {len(csv_files) if data_dir.exists() else 0} data files found",
                duration
            )
            
            if errors:
                self.results['errors'].extend(errors)
            
            return passed
            
        except Exception as e:
            logger.error(f"Environment validation failed: {e}", exc_info=True)
            self.results['errors'].append(f"Environment setup: {str(e)}")
            self.log_result("Environment Setup", False, str(e), time.time() - start_time)
            return False
    
    def validate_ml_models(self) -> bool:
        """Step 2: Validate ML model training"""
        if self.skip_ml:
            logger.info("\n" + "="*60)
            logger.info("STEP 2: ML Model Training (SKIPPED)")
            logger.info("="*60)
            return True
        
        logger.info("\n" + "="*60)
        logger.info("STEP 2: ML Model Training Validation")
        logger.info("="*60)
        
        start_time = time.time()
        
        try:
            # Run test_train_all.py
            logger.info("Running ML model training tests...")
            
            from scripts.test_train_all import main as test_train_main
            result = test_train_main()
            
            duration = time.time() - start_time
            self.log_result(
                "ML Model Training",
                result,
                "All models (Linear, LogReg, SVM, ARIMA, LSTM) trained successfully" if result else "Some models failed",
                duration
            )
            
            return result
            
        except Exception as e:
            logger.error(f"ML model validation failed: {e}", exc_info=True)
            self.results['errors'].append(f"ML training: {str(e)}")
            self.log_result("ML Model Training", False, str(e), time.time() - start_time)
            return False
    
    def validate_prediction_service(self) -> bool:
        """Step 3: Validate prediction service"""
        if self.skip_ml:
            logger.info("\n" + "="*60)
            logger.info("STEP 3: Prediction Service (SKIPPED)")
            logger.info("="*60)
            return True
        
        logger.info("\n" + "="*60)
        logger.info("STEP 3: Prediction Service Validation")
        logger.info("="*60)
        
        start_time = time.time()
        
        try:
            from app.services.predict_service import PredictionService
            
            logger.info("Initializing prediction service...")
            pred_service = PredictionService()
            
            # Test prediction (will use fallback if no models)
            test_symbols = ['RELIANCE', 'TCS']
            logger.info(f"Testing predictions for: {test_symbols}")
            
            results = pred_service.predict(
                symbols=test_symbols,
                model='ensemble',
                horizon=21
            )
            
            # Validate results structure
            checks = []
            checks.append(('predictions' in results, "Has predictions field"))
            checks.append(('portfolio' in results, "Has portfolio field"))
            
            if 'portfolio' in results:
                for strategy in ['model_weighted', 'mean_variance', 'risk_parity']:
                    if strategy in results['portfolio']:
                        weights = results['portfolio'][strategy].get('weights', {})
                        total = sum(weights.values())
                        checks.append((
                            0.99 <= total <= 1.01,
                            f"{strategy} weights sum ≈ 1.0 (actual: {total:.4f})"
                        ))
            
            all_passed = all(check[0] for check in checks)
            details = ", ".join(check[1] for check in checks)
            
            duration = time.time() - start_time
            self.log_result(
                "Prediction Service",
                all_passed,
                details,
                duration
            )
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Prediction service validation failed: {e}", exc_info=True)
            self.results['errors'].append(f"Prediction service: {str(e)}")
            self.log_result("Prediction Service", False, str(e), time.time() - start_time)
            return False
    
    def validate_api_endpoints(self) -> bool:
        """Step 4: Validate FastAPI endpoints"""
        if self.skip_api:
            logger.info("\n" + "="*60)
            logger.info("STEP 4: API Endpoints (SKIPPED)")
            logger.info("="*60)
            return True
        
        logger.info("\n" + "="*60)
        logger.info("STEP 4: FastAPI Endpoints Validation")
        logger.info("="*60)
        
        start_time = time.time()
        
        try:
            # We can't start the server here, so we'll test the route definitions
            from main import app
            
            # Check registered routes
            routes = []
            for route in app.routes:
                if hasattr(route, 'path'):
                    routes.append(route.path)
            
            required_routes = [
                '/health',
                '/api/backtest/health',
                '/api/backtest/run',
                '/api/backtest/strategies',
                '/api/backtest/compare',
                '/api/predictions/predict',
                '/api/predictions/portfolio',
            ]
            
            missing = [r for r in required_routes if r not in routes]
            
            if missing:
                logger.warning(f"Missing routes: {missing}")
                self.results['warnings'].append(f"Missing routes: {missing}")
            
            logger.info(f"✓ Total routes registered: {len(routes)}")
            logger.info(f"✓ Required routes present: {len(required_routes) - len(missing)}/{len(required_routes)}")
            
            duration = time.time() - start_time
            self.log_result(
                "API Route Registration",
                len(missing) == 0,
                f"{len(routes)} total routes, {len(missing)} missing",
                duration
            )
            
            return len(missing) == 0
            
        except Exception as e:
            logger.error(f"API validation failed: {e}", exc_info=True)
            self.results['errors'].append(f"API endpoints: {str(e)}")
            self.log_result("API Route Registration", False, str(e), time.time() - start_time)
            return False
    
    def validate_backtester(self) -> bool:
        """Step 5: Validate backtester module"""
        logger.info("\n" + "="*60)
        logger.info("STEP 5: Backtester Module Validation")
        logger.info("="*60)
        
        start_time = time.time()
        
        try:
            # Run existing backtest API tests
            logger.info("Running backtest API tests...")
            
            import subprocess
            result = subprocess.run(
                [sys.executable, "scripts/test_backtest_api.py"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse output
            passed = "All tests passed!" in result.stdout
            
            # Count tests
            import re
            pass_count = len(re.findall(r'✅ PASS:', result.stdout))
            fail_count = len(re.findall(r'❌ FAIL:', result.stdout))
            
            duration = time.time() - start_time
            self.log_result(
                "Backtester Module",
                passed,
                f"{pass_count} passed, {fail_count} failed",
                duration
            )
            
            if not passed and result.stderr:
                self.results['errors'].append(f"Backtester: {result.stderr[:200]}")
            
            return passed
            
        except Exception as e:
            logger.error(f"Backtester validation failed: {e}", exc_info=True)
            self.results['errors'].append(f"Backtester: {str(e)}")
            self.log_result("Backtester Module", False, str(e), time.time() - start_time)
            return False
    
    def validate_integration(self) -> bool:
        """Step 6: Integration tests"""
        logger.info("\n" + "="*60)
        logger.info("STEP 6: Integration Tests")
        logger.info("="*60)
        
        start_time = time.time()
        
        try:
            from app.services.backtester import Backtester
            from pathlib import Path
            
            # Test model-weighted strategy fallback
            logger.info("Testing model-weighted fallback...")
            backtester = Backtester(
                symbols=['RELIANCE', 'TCS'],
                start_date='2024-01-01',
                end_date='2026-03-31',
                strategy='model_weighted',
                rebalance_freq=21,
                initial_capital=100000,
                models_dir=Path("models")  # Add models_dir parameter
            )
            
            results = backtester.run()
            
            checks = []
            checks.append((results is not None, "Backtester returned results"))
            checks.append(('daily_values' in results, "Has daily_values"))
            checks.append(('metrics' in results, "Has performance metrics"))
            checks.append((results.get('trades', 0) >= 0, "Trade count valid"))
            
            all_passed = all(check[0] for check in checks)
            details = ", ".join(check[1] for check in checks)
            
            duration = time.time() - start_time
            self.log_result(
                "Integration Tests",
                all_passed,
                details,
                duration
            )
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Integration tests failed: {e}", exc_info=True)
            self.results['errors'].append(f"Integration: {str(e)}")
            self.log_result("Integration Tests", False, str(e), time.time() - start_time)
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final validation report"""
        logger.info("\n" + "="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for t in self.results['tests'].values() if t['passed'])
        failed_tests = total_tests - passed_tests
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'errors': len(self.results['errors']),
            'warnings': len(self.results['warnings']),
            'success_rate': f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
        }
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"⚠️  Warnings: {len(self.results['warnings'])}")
        logger.info(f"❗ Errors: {len(self.results['errors'])}")
        logger.info(f"Success Rate: {self.results['summary']['success_rate']}")
        
        if self.results['errors']:
            logger.info("\n❗ ERRORS:")
            for error in self.results['errors']:
                logger.info(f"  - {error}")
        
        if self.results['warnings']:
            logger.info("\n⚠️  WARNINGS:")
            for warning in self.results['warnings']:
                logger.info(f"  - {warning}")
        
        # Production readiness assessment
        is_production_ready = (
            failed_tests == 0 and
            len(self.results['errors']) == 0
        )
        
        logger.info("\n" + "="*60)
        if is_production_ready:
            logger.info("✅ BACKEND IS PRODUCTION READY!")
            logger.info("System validated and ready for frontend integration.")
        else:
            logger.info("❌ BACKEND NEEDS FIXES")
            logger.info("Please address errors before production deployment.")
        logger.info("="*60)
        
        self.results['production_ready'] = is_production_ready
        
        return self.results
    
    def run_all(self) -> Dict[str, Any]:
        """Run all validation steps"""
        logger.info("\n" + "="*60)
        logger.info("QUANTFIN BACKEND VALIDATION")
        logger.info("="*60)
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Quick mode: {self.quick}")
        logger.info(f"Skip ML: {self.skip_ml}")
        logger.info(f"Skip API: {self.skip_api}")
        
        try:
            # Run validation steps
            self.validate_environment()
            self.validate_ml_models()
            self.validate_prediction_service()
            self.validate_api_endpoints()
            self.validate_backtester()
            self.validate_integration()
            
            # Generate report
            report = self.generate_report()
            
            # Save report
            report_path = Path("validation_report.json")
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"\n📊 Full report saved to: {report_path}")
            
            return report
            
        except KeyboardInterrupt:
            logger.warning("\n⚠️  Validation interrupted by user")
            return self.results
        except Exception as e:
            logger.error(f"\n❌ Validation failed with error: {e}", exc_info=True)
            self.results['errors'].append(f"Fatal error: {str(e)}")
            return self.results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate QuantFin backend system"
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick validation (skip long-running tests)'
    )
    parser.add_argument(
        '--skip-ml',
        action='store_true',
        help='Skip ML model training tests'
    )
    parser.add_argument(
        '--skip-api',
        action='store_true',
        help='Skip API endpoint tests'
    )
    
    args = parser.parse_args()
    
    validator = BackendValidator(
        quick=args.quick,
        skip_ml=args.skip_ml,
        skip_api=args.skip_api
    )
    
    report = validator.run_all()
    
    # Exit with appropriate code
    sys.exit(0 if report.get('production_ready', False) else 1)


if __name__ == "__main__":
    main()
