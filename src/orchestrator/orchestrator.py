"""
Multi-Model Orchestrator - Fixed Version
No relative imports, uses direct file loading
"""

import json
import logging
import time
import sys
import os
import importlib.util
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _load(name, path):
    """Load module directly from file path"""
    if name in sys.modules:
        return sys.modules[name]
    spec   = importlib.util.spec_from_file_location(name, path)
    mod    = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class HealthDiagnosticsOrchestrator:
    """Central orchestrator for complete blood report analysis"""

    def __init__(self, src_path: str = None):
        self.src = src_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..'
        )

        # Load all modules by direct file path
        self._ip  = _load('input_parser',
            os.path.join(self.src, 'parsers', 'input_parser.py'))
        self._de  = _load('data_extractor',
            os.path.join(self.src, 'extractors', 'data_extractor.py'))
        self._dv  = _load('data_validator',
            os.path.join(self.src, 'validators', 'data_validator.py'))
        self._pi  = _load('parameter_interpreter',
            os.path.join(self.src, 'models', 'parameter_interpreter.py'))
        self._pr  = _load('pattern_recognition',
            os.path.join(self.src, 'models', 'pattern_recognition.py'))
        self._fs  = _load('findings_synthesizer',
            os.path.join(self.src, 'synthesis', 'findings_synthesizer.py'))
        self._rg  = _load('recommendation_generator',
            os.path.join(self.src, 'recommendations', 'recommendation_generator.py'))

        self.workflow_stats = {
            'total_processed': 0,
            'successful':      0,
            'failed':          0,
            'errors':          []
        }
        logger.info("✓ Orchestrator ready")

    def process_report(self, file_path: str,
                       gender: str = None,
                       age: int = None) -> Dict[str, Any]:
        """Run full 8-step pipeline on a blood report"""
        start     = time.time()
        file_path = str(file_path)

        try:
            # Step 1 – Parse
            parser      = self._ip.InputParser()
            parsed      = parser.parse(file_path)
            gender      = gender or parsed.get('gender')
            age         = age    or parsed.get('age')

            # Step 2 – Extract
            extractor   = self._de.ParameterExtractor()
            extracted   = extractor.extract(parsed)

            # Step 3 – Validate
            validator   = self._dv.DataValidator()
            validated, val_report = validator.validate_and_standardize(extracted)

            # Step 4 – Interpret (Model 1)
            interpreter = self._pi.ParameterInterpreter(gender=gender, age=age)
            interps     = interpreter.interpret(validated)

            # Step 5 – Pattern Recognition (Model 2)
            pat_model   = self._pr.PatternRecognitionModel()
            pat_analysis = pat_model.analyze(interps)

            # Step 6 – Synthesize
            synthesizer = self._fs.FindingsSynthesizer()
            synth       = synthesizer.synthesize(interps, pat_analysis)

            # Step 7 – Recommendations
            recommender = self._rg.RecommendationGenerator()
            recs        = recommender.generate(synth, pat_analysis,
                              {'gender': gender, 'age': age})

            # Step 8 – Build final report
            elapsed = round(time.time() - start, 3)
            report  = {
                'metadata': {
                    'report_id':       parsed.get('report_id', 'UNKNOWN'),
                    'patient_id':      parsed.get('patient_id', 'UNKNOWN'),
                    'test_date':       parsed.get('test_date', 'UNKNOWN'),
                    'lab_name':        parsed.get('lab_name', 'UNKNOWN'),
                    'gender':          parsed.get('gender', 'UNKNOWN'),
                    'age':             parsed.get('age', 'UNKNOWN'),
                    'processing_time': elapsed
                },
                'parameter_summary':     interpreter.get_summary(),
                'interpretations':       interps,
                'pattern_analysis':      pat_analysis,
                'synthesized_findings':  synth,
                'recommendations':       recs,
                'summary_text':          synthesizer.get_summary(),
                'formatted_recommendations': recommender.format_recommendations(),
                'overall_status':        synth.get(
                    'overall_status', {}).get('status', 'unknown'),
                'disclaimer': (
                    "AI-generated report for educational purposes only. "
                    "Not a substitute for professional medical advice."
                )
            }

            self.workflow_stats['total_processed'] += 1
            self.workflow_stats['successful']       += 1
            logger.info(f"✓ Done in {elapsed}s")
            return report

        except Exception as e:
            self.workflow_stats['total_processed'] += 1
            self.workflow_stats['failed']          += 1
            self.workflow_stats['errors'].append(
                {'file': file_path, 'error': str(e)})
            logger.error(f"✗ Failed: {e}")
            raise

    def save_report(self, report: Dict[str, Any],
                    output_path: str) -> str:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        return output_path

    def get_workflow_stats(self) -> Dict[str, Any]:
        stats = dict(self.workflow_stats)
        total = stats['total_processed']
        stats['success_rate'] = (
            f"{stats['successful']/total*100:.1f}%" if total else "N/A"
        )
        return stats