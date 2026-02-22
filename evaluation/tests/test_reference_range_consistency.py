"""
Property-Based Tests for Reference Range Consistency

Feature: milestone-1-validation
Property 2: Reference Range Consistency
Validates: Requirements 1.3

Tests that for any parameter in a ground truth file, the reference range matches
the reference range returned by UnifiedReferenceManager for the same parameter
with the same patient demographics.
"""

import json
import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from evaluation.ground_truth_generator import GroundTruthGenerator
from core_phase3.knowledge_base.unified_reference_manager import UnifiedReferenceManager


# ============================================================================
# Hypothesis Strategies for Generating Test Data
# ============================================================================

@st.composite
def patient_demographics_strategy(draw):
    """Generate valid patient demographics (age and sex)."""
    age = draw(st.one_of(
        st.none(),
        st.integers(min_value=18, max_value=90)
    ))
    sex = draw(st.one_of(
        st.none(),
        st.sampled_from(['male', 'female', 'Male', 'Female'])
    ))
    return {'age': age, 'sex': sex}


@st.composite
def parameter_name_strategy(draw):
    """
    Generate parameter names that exist in the reference manager.
    
    These are the parameters that the UnifiedReferenceManager knows about.
    """
    # Common blood parameters that should be in the reference manager
    common_parameters = [
        'Hemoglobin', 'WBC', 'RBC', 'Platelets', 'Hematocrit',
        'Glucose', 'Creatinine', 'BUN', 'Sodium', 'Potassium',
        'Cholesterol', 'Triglycerides', 'HDL', 'LDL',
        'ALT', 'AST', 'Bilirubin', 'Albumin',
        'TSH', 'T3', 'T4', 'Calcium'
    ]
    return draw(st.sampled_from(common_parameters))


@st.composite
def ground_truth_parameter_strategy(draw):
    """
    Generate a ground truth parameter entry with demographics.
    
    This represents a parameter as it would appear in a ground truth file,
    along with the patient demographics that were used to generate it.
    """
    param_name = draw(parameter_name_strategy())
    demographics = draw(patient_demographics_strategy())
    
    # Generate a value (we don't care about the actual value for this test)
    value = draw(st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False))
    unit = draw(st.sampled_from(['g/dL', 'mg/dL', 'cells/µL', 'mmol/L', 'U/L', '%', 'ng/mL']))
    
    return {
        'parameter_name': param_name,
        'value': round(value, 2),
        'unit': unit,
        'age': demographics['age'],
        'sex': demographics['sex'].lower() if demographics['sex'] else None
    }


# ============================================================================
# Property Tests
# ============================================================================

class TestReferenceRangeConsistency:
    """
    Property 2: Reference Range Consistency
    
    **Validates: Requirements 1.3**
    
    For any parameter in a ground truth file, the reference range should match
    the reference range returned by UnifiedReferenceManager for the same parameter
    with the same patient demographics.
    """
    
    @given(param_data=ground_truth_parameter_strategy())
    @settings(max_examples=20, deadline=None)
    def test_reference_range_matches_unified_reference_manager(self, param_data):
        """
        Property: Reference ranges in ground truth must match UnifiedReferenceManager.
        
        When a ground truth template is generated with specific patient demographics,
        the reference range for each parameter should exactly match what the
        UnifiedReferenceManager returns for the same parameter and demographics.
        """
        # Initialize components
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        # Extract test data
        param_name = param_data['parameter_name']
        age = param_data['age']
        sex = param_data['sex']
        
        # Get reference range from generator (simulates ground truth generation)
        generator_ref_range = generator._get_reference_range_for_parameter(
            parameter=param_name.lower(),  # Generator uses lowercase
            age=age,
            sex=sex
        )
        
        # Get reference range directly from UnifiedReferenceManager
        manager_ref_range = reference_manager.get_reference_range(
            parameter=param_name,  # Manager uses capitalized
            age=age,
            sex=sex
        )
        
        # If the reference manager doesn't have this parameter, both should return None/unavailable
        if not manager_ref_range.get('available', True):
            # Generator should also return None for min/max
            assert generator_ref_range['min'] is None, \
                f"Generator should return None for unavailable parameter {param_name}"
            assert generator_ref_range['max'] is None, \
                f"Generator should return None for unavailable parameter {param_name}"
            assert generator_ref_range['source'] == 'unavailable', \
                f"Generator should mark source as unavailable for {param_name}"
            return
        
        # If available, verify consistency: the generator should return the same range as the manager
        assert generator_ref_range['min'] == manager_ref_range['min'], \
            f"Min mismatch for {param_name} (age={age}, sex={sex}): " \
            f"generator={generator_ref_range['min']}, manager={manager_ref_range['min']}"
        
        assert generator_ref_range['max'] == manager_ref_range['max'], \
            f"Max mismatch for {param_name} (age={age}, sex={sex}): " \
            f"generator={generator_ref_range['max']}, manager={manager_ref_range['max']}"
    
    @given(param_data=ground_truth_parameter_strategy())
    @settings(max_examples=20, deadline=None)
    def test_reference_range_source_is_documented(self, param_data):
        """
        Property: Reference ranges must include source information.
        
        Every reference range should document where it came from (NHANES, ABIM, etc.)
        to ensure traceability and transparency.
        """
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        param_name = param_data['parameter_name']
        age = param_data['age']
        sex = param_data['sex']
        
        # Get reference range
        ref_range = generator._get_reference_range_for_parameter(
            parameter=param_name.lower(),
            age=age,
            sex=sex
        )
        
        # If range is available, it must have a source
        if ref_range['min'] is not None and ref_range['max'] is not None:
            assert 'source' in ref_range, \
                f"Reference range for {param_name} missing source information"
            assert ref_range['source'] != 'unknown', \
                f"Reference range for {param_name} has unknown source"
    
    @given(param_data=ground_truth_parameter_strategy())
    @settings(max_examples=20, deadline=None)
    def test_reference_range_is_valid_when_available(self, param_data):
        """
        Property: When a reference range is available, min must be less than max.
        
        This ensures that reference ranges are logically valid.
        """
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        param_name = param_data['parameter_name']
        age = param_data['age']
        sex = param_data['sex']
        
        # Get reference range
        ref_range = generator._get_reference_range_for_parameter(
            parameter=param_name.lower(),
            age=age,
            sex=sex
        )
        
        # If both min and max are available, min must be < max
        if ref_range['min'] is not None and ref_range['max'] is not None:
            assert ref_range['min'] < ref_range['max'], \
                f"Invalid reference range for {param_name}: " \
                f"min ({ref_range['min']}) >= max ({ref_range['max']})"
    
    @given(param_data=ground_truth_parameter_strategy())
    @settings(max_examples=20, deadline=None)
    def test_same_demographics_always_return_same_range(self, param_data):
        """
        Property: Reference ranges are deterministic for given demographics.
        
        Calling the reference manager multiple times with the same parameter
        and demographics should always return the same reference range.
        """
        reference_manager = UnifiedReferenceManager()
        
        param_name = param_data['parameter_name']
        age = param_data['age']
        sex = param_data['sex']
        
        # Get reference range twice
        range1 = reference_manager.get_reference_range(
            parameter=param_name,
            age=age,
            sex=sex
        )
        
        range2 = reference_manager.get_reference_range(
            parameter=param_name,
            age=age,
            sex=sex
        )
        
        # Skip if parameter not available
        assume(range1.get('available', True))
        assume(range2.get('available', True))
        
        # Both calls should return identical ranges
        assert range1['min'] == range2['min'], \
            f"Non-deterministic min for {param_name}: {range1['min']} != {range2['min']}"
        assert range1['max'] == range2['max'], \
            f"Non-deterministic max for {param_name}: {range1['max']} != {range2['max']}"
        assert range1['source'] == range2['source'], \
            f"Non-deterministic source for {param_name}: {range1['source']} != {range2['source']}"


# ============================================================================
# Integration Tests
# ============================================================================

class TestReferenceRangeConsistencyIntegration:
    """
    Integration tests to verify reference range consistency in real scenarios.
    """
    
    def test_hemoglobin_range_consistency_male_50(self):
        """
        Test that Hemoglobin reference range is consistent for 50-year-old male.
        """
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        # Get range from generator
        gen_range = generator._get_reference_range_for_parameter(
            parameter='hemoglobin',
            age=50,
            sex='male'
        )
        
        # Get range from manager
        mgr_range = reference_manager.get_reference_range(
            parameter='Hemoglobin',
            age=50,
            sex='male'
        )
        
        # Should match
        assert gen_range['min'] == mgr_range['min']
        assert gen_range['max'] == mgr_range['max']
    
    def test_glucose_range_consistency_no_demographics(self):
        """
        Test that Glucose reference range is consistent without demographics.
        """
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        # Get range from generator (no age/sex)
        gen_range = generator._get_reference_range_for_parameter(
            parameter='glucose',
            age=None,
            sex=None
        )
        
        # Get range from manager (no age/sex)
        mgr_range = reference_manager.get_reference_range(
            parameter='Glucose',
            age=None,
            sex=None
        )
        
        # If available, should match
        if mgr_range.get('available', True):
            assert gen_range['min'] == mgr_range['min']
            assert gen_range['max'] == mgr_range['max']
        else:
            # If not available, generator should return None
            assert gen_range['min'] is None
            assert gen_range['max'] is None
    
    def test_cholesterol_range_consistency_female_35(self):
        """
        Test that Cholesterol reference range is consistent for 35-year-old female.
        """
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        # Get range from generator
        gen_range = generator._get_reference_range_for_parameter(
            parameter='cholesterol',
            age=35,
            sex='female'
        )
        
        # Get range from manager
        mgr_range = reference_manager.get_reference_range(
            parameter='Cholesterol',
            age=35,
            sex='female'
        )
        
        # If available, should match
        if mgr_range.get('available', True):
            assert gen_range['min'] == mgr_range['min']
            assert gen_range['max'] == mgr_range['max']
        else:
            # If not available, generator should return None
            assert gen_range['min'] is None
            assert gen_range['max'] is None
    
    def test_all_common_parameters_have_consistent_ranges(self):
        """
        Test that all common blood parameters have consistent ranges.
        """
        reference_manager = UnifiedReferenceManager()
        generator = GroundTruthGenerator(reference_manager=reference_manager)
        
        common_parameters = [
            'Hemoglobin', 'WBC', 'RBC', 'Platelets',
            'Glucose', 'Creatinine', 'Cholesterol', 'Triglycerides'
        ]
        
        age = 45
        sex = 'male'
        
        for param in common_parameters:
            # Get range from generator
            gen_range = generator._get_reference_range_for_parameter(
                parameter=param.lower(),
                age=age,
                sex=sex
            )
            
            # Get range from manager
            mgr_range = reference_manager.get_reference_range(
                parameter=param,
                age=age,
                sex=sex
            )
            
            # If available, should match
            if mgr_range.get('available', True):
                assert gen_range['min'] == mgr_range['min'], \
                    f"{param}: min mismatch (gen={gen_range['min']}, mgr={mgr_range['min']})"
                assert gen_range['max'] == mgr_range['max'], \
                    f"{param}: max mismatch (gen={gen_range['max']}, mgr={mgr_range['max']})"
            else:
                # If not available, generator should return None
                assert gen_range['min'] is None, \
                    f"{param}: generator should return None for unavailable parameter"
                assert gen_range['max'] is None, \
                    f"{param}: generator should return None for unavailable parameter"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

