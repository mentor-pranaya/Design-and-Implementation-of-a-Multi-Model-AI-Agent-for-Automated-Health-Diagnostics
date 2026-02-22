"""
NHANES Data Processor - Population-Based Reference Ranges

This module processes NHANES dataset to generate age/sex-specific
reference ranges based on real population data.

Design Philosophy:
- NO hardcoding - all ranges derived from data
- Age-specific percentiles (by decade)
- Sex-specific ranges where applicable
- Statistically robust (5th-95th percentiles)
- Transparent source attribution

Data Source: NHANES (National Health and Nutrition Examination Survey)
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class NHANESProcessor:
    """
    Process NHANES dataset to generate population-based reference ranges.
    
    Generates age/sex-specific percentile ranges for clinical parameters.
    """
    
    # NHANES column mapping to standard parameter names
    PARAMETER_MAPPING = {
        'Hemoglobin': 'LBXHGB',
        'WBC': 'LBXWBCSI',
        'Platelet Count': 'LBXPLTSI',
        'Glucose': 'LBXGLU',
        'HbA1c': 'LBXGH',
        'Total Cholesterol': 'LBXTC',
        'HDL': 'LBDHDD',
        'LDL': 'LBDLDL',
        'Triglycerides': 'LBXTR',
        'Creatinine': 'LBXSCR',
        'BUN': 'LBXSBU',
        'ALT': 'LBXSATSI',
        'AST': 'LBXSASSI',
        'Bilirubin Total': 'LBXSTB',
        'Albumin': 'LBXSAL',
        'Calcium': 'LBXSCA',
        'Sodium': 'LBXSNASI',
        'Potassium': 'LBXSKSI',
        'Chloride': 'LBXSCLSI',
        'Iron': 'LBXIRN',
        'Ferritin': 'LBXFER',
        'Uric Acid': 'LBXSUA',
        'CRP': 'LBXCRP',
        'TSH': 'LBXTSH'
    }
    
    # Age groups for stratification
    AGE_GROUPS = [
        (18, 29, '18-29'),
        (30, 39, '30-39'),
        (40, 49, '40-49'),
        (50, 59, '50-59'),
        (60, 69, '60-69'),
        (70, 120, '70+')
    ]
    
    def __init__(self, nhanes_path: str = None):
        """
        Initialize NHANES processor.
        
        Args:
            nhanes_path: Path to NHANES directory
        """
        if nhanes_path is None:
            nhanes_path = r"C:\Users\mi\Downloads\infosys project\NHANES"
        
        self.nhanes_path = Path(nhanes_path)
        self.labs = None
        self.demographics = None
        self.merged_data = None
        
        print("="*70)
        print("NHANES PROCESSOR - Population-Based Reference Ranges")
        print("="*70)
    
    def load_data(self):
        """Load NHANES labs and demographics data."""
        print("\n📂 Loading NHANES data...")
        
        labs_file = self.nhanes_path / "labs.csv"
        demo_file = self.nhanes_path / "demographic.csv"
        
        if not labs_file.exists():
            raise FileNotFoundError(f"Labs file not found: {labs_file}")
        if not demo_file.exists():
            raise FileNotFoundError(f"Demographics file not found: {demo_file}")
        
        print(f"  Loading labs: {labs_file}")
        self.labs = pd.read_csv(labs_file)
        
        print(f"  Loading demographics: {demo_file}")
        self.demographics = pd.read_csv(demo_file)
        
        print(f"\n✓ Data loaded successfully")
        print(f"  Labs: {len(self.labs):,} samples, {len(self.labs.columns)} columns")
        print(f"  Demographics: {len(self.demographics):,} samples, {len(self.demographics.columns)} columns")
        
        # Merge datasets
        self._merge_data()
    
    def _merge_data(self):
        """Merge labs with demographics on SEQN."""
        print("\n🔗 Merging labs with demographics...")
        
        # Select relevant demographic columns
        demo_cols = ['SEQN', 'RIAGENDR', 'RIDAGEYR']  # SEQN, Gender, Age
        demo_subset = self.demographics[demo_cols].copy()
        
        # Rename for clarity
        demo_subset.columns = ['SEQN', 'Sex', 'Age']
        
        # Merge
        self.merged_data = self.labs.merge(demo_subset, on='SEQN', how='inner')
        
        # Map sex codes (1=Male, 2=Female)
        self.merged_data['Sex'] = self.merged_data['Sex'].map({1: 'Male', 2: 'Female'})
        
        # Filter to adults (18+)
        self.merged_data = self.merged_data[self.merged_data['Age'] >= 18]
        
        print(f"✓ Merged data: {len(self.merged_data):,} adult samples")
    
    def generate_reference_ranges(self) -> Dict:
        """
        Generate comprehensive reference ranges from NHANES data.
        
        Returns:
            Dictionary of reference ranges with age/sex stratification
        """
        if self.merged_data is None:
            self.load_data()
        
        print("\n📊 Generating population-based reference ranges...")
        print("  Using 5th-95th percentiles from NHANES population")
        
        reference_ranges = {
            "_metadata": {
                "source": "NHANES (National Health and Nutrition Examination Survey)",
                "method": "Population percentiles (5th-95th)",
                "sample_size": len(self.merged_data),
                "age_range": "18+ years",
                "stratification": "Age groups and sex",
                "generated_date": pd.Timestamp.now().isoformat()
            }
        }
        
        # Process each parameter
        for param_name, nhanes_col in self.PARAMETER_MAPPING.items():
            if nhanes_col in self.merged_data.columns:
                print(f"\n  Processing: {param_name} ({nhanes_col})")
                param_ranges = self._calculate_parameter_ranges(param_name, nhanes_col)
                if param_ranges:
                    reference_ranges[param_name] = param_ranges
            else:
                print(f"  ⚠ Skipping {param_name}: Column {nhanes_col} not found")
        
        print(f"\n✓ Generated ranges for {len(reference_ranges)-1} parameters")
        
        return reference_ranges
    
    def _calculate_parameter_ranges(self, param_name: str, nhanes_col: str) -> Optional[Dict]:
        """
        Calculate reference ranges for a single parameter.
        
        Args:
            param_name: Standard parameter name
            nhanes_col: NHANES column name
        
        Returns:
            Dictionary with age/sex-specific ranges
        """
        data = self.merged_data[[nhanes_col, 'Age', 'Sex']].copy()
        data = data.dropna(subset=[nhanes_col])
        
        if len(data) < 100:  # Minimum sample size
            print(f"    ⚠ Insufficient data: {len(data)} samples")
            return None
        
        param_ranges = {
            "nhanes_column": nhanes_col,
            "total_samples": len(data),
            "unit": self._infer_unit(param_name),
            "overall": self._calculate_percentiles(data[nhanes_col]),
            "by_sex": {},
            "by_age_sex": {}
        }
        
        # Calculate by sex
        for sex in ['Male', 'Female']:
            sex_data = data[data['Sex'] == sex][nhanes_col]
            if len(sex_data) >= 50:
                param_ranges["by_sex"][sex.lower()] = self._calculate_percentiles(sex_data)
        
        # Calculate by age and sex
        for age_min, age_max, age_label in self.AGE_GROUPS:
            age_data = data[(data['Age'] >= age_min) & (data['Age'] <= age_max)]
            
            for sex in ['Male', 'Female']:
                sex_age_data = age_data[age_data['Sex'] == sex][nhanes_col]
                
                if len(sex_age_data) >= 30:  # Minimum for age/sex group
                    key = f"{sex.lower()}_{age_label}"
                    param_ranges["by_age_sex"][key] = self._calculate_percentiles(sex_age_data)
        
        print(f"    ✓ {len(data):,} samples, {len(param_ranges['by_age_sex'])} age/sex groups")
        
        return param_ranges
    
    def _calculate_percentiles(self, data: pd.Series) -> Dict:
        """
        Calculate percentile statistics for data.
        
        Args:
            data: Pandas series of values
        
        Returns:
            Dictionary with percentiles and statistics
        """
        return {
            "n": len(data),
            "mean": float(data.mean()),
            "median": float(data.median()),
            "std": float(data.std()),
            "p5": float(data.quantile(0.05)),
            "p10": float(data.quantile(0.10)),
            "p25": float(data.quantile(0.25)),
            "p75": float(data.quantile(0.75)),
            "p90": float(data.quantile(0.90)),
            "p95": float(data.quantile(0.95)),
            "reference_range": {
                "min": float(data.quantile(0.05)),
                "max": float(data.quantile(0.95))
            }
        }
    
    def _infer_unit(self, param_name: str) -> str:
        """Infer unit for parameter."""
        unit_map = {
            'Hemoglobin': 'g/dL',
            'WBC': 'cells/µL',
            'Platelet Count': 'cells/µL',
            'Glucose': 'mg/dL',
            'HbA1c': '%',
            'Total Cholesterol': 'mg/dL',
            'HDL': 'mg/dL',
            'LDL': 'mg/dL',
            'Triglycerides': 'mg/dL',
            'Creatinine': 'mg/dL',
            'BUN': 'mg/dL',
            'ALT': 'U/L',
            'AST': 'U/L',
            'Bilirubin Total': 'mg/dL',
            'Albumin': 'g/dL',
            'Calcium': 'mg/dL',
            'Sodium': 'mEq/L',
            'Potassium': 'mEq/L',
            'Chloride': 'mEq/L',
            'Iron': 'µg/dL',
            'Ferritin': 'ng/mL',
            'Uric Acid': 'mg/dL',
            'CRP': 'mg/dL',
            'TSH': 'mU/L'
        }
        return unit_map.get(param_name, 'N/A')
    
    def save_reference_ranges(self, ranges: Dict, output_path: str = None):
        """
        Save reference ranges to JSON file.
        
        Args:
            ranges: Reference ranges dictionary
            output_path: Output file path
        """
        if output_path is None:
            output_path = Path(__file__).parent / "nhanes_reference_ranges.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(ranges, f, indent=2)
        
        print(f"\n✓ Reference ranges saved to: {output_path}")
    
    def compare_to_abim(self, nhanes_ranges: Dict, abim_ranges: Dict) -> Dict:
        """
        Compare NHANES ranges to ABIM guidelines.
        
        Args:
            nhanes_ranges: NHANES-derived ranges
            abim_ranges: ABIM guideline ranges
        
        Returns:
            Comparison report
        """
        print("\n📊 Comparing NHANES to ABIM Guidelines...")
        
        comparison = {
            "comparison_date": pd.Timestamp.now().isoformat(),
            "parameters_compared": [],
            "agreements": [],
            "discrepancies": []
        }
        
        for param in nhanes_ranges:
            if param.startswith('_'):
                continue
            
            if param in abim_ranges:
                nhanes_overall = nhanes_ranges[param].get('overall', {})
                nhanes_min = nhanes_overall.get('reference_range', {}).get('min')
                nhanes_max = nhanes_overall.get('reference_range', {}).get('max')
                
                abim_min = abim_ranges[param].get('min')
                abim_max = abim_ranges[param].get('max')
                
                if nhanes_min and nhanes_max and abim_min and abim_max:
                    comparison["parameters_compared"].append(param)
                    
                    # Check if ranges are similar (within 20%)
                    min_diff = abs(nhanes_min - abim_min) / abim_min * 100
                    max_diff = abs(nhanes_max - abim_max) / abim_max * 100
                    
                    if min_diff < 20 and max_diff < 20:
                        comparison["agreements"].append({
                            "parameter": param,
                            "nhanes_range": f"{nhanes_min:.1f}-{nhanes_max:.1f}",
                            "abim_range": f"{abim_min:.1f}-{abim_max:.1f}",
                            "status": "✓ Agreement"
                        })
                    else:
                        comparison["discrepancies"].append({
                            "parameter": param,
                            "nhanes_range": f"{nhanes_min:.1f}-{nhanes_max:.1f}",
                            "abim_range": f"{abim_min:.1f}-{abim_max:.1f}",
                            "min_diff_percent": f"{min_diff:.1f}%",
                            "max_diff_percent": f"{max_diff:.1f}%",
                            "status": "⚠ Discrepancy"
                        })
        
        print(f"\n  Parameters compared: {len(comparison['parameters_compared'])}")
        print(f"  Agreements: {len(comparison['agreements'])}")
        print(f"  Discrepancies: {len(comparison['discrepancies'])}")
        
        return comparison


def generate_nhanes_ranges():
    """Convenience function to generate NHANES reference ranges."""
    processor = NHANESProcessor()
    processor.load_data()
    ranges = processor.generate_reference_ranges()
    processor.save_reference_ranges(ranges)
    return ranges


if __name__ == "__main__":
    # Generate NHANES reference ranges
    print("\n🔬 Generating NHANES Population-Based Reference Ranges\n")
    ranges = generate_nhanes_ranges()
    
    print("\n✓ NHANES reference ranges generated successfully!")
    print("\nNext steps:")
    print("1. Review: core_phase3/knowledge_base/nhanes_reference_ranges.json")
    print("2. Integrate with unified reference manager")
    print("3. Use for age/sex-specific evaluations")
