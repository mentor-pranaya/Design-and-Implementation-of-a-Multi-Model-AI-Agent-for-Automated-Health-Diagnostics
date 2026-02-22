"""
NHANES Dataset Explorer

This script helps you explore the NHANES dataset and understand
what parameters are available for validation and calibration.

Usage:
    python explore_nhanes.py
"""

import pandas as pd
from pathlib import Path

# NHANES dataset path
NHANES_PATH = r"C:\Users\mi\Downloads\infosys project\NHANES"


def explore_labs():
    """Explore the labs.csv file to see available parameters."""
    print("="*70)
    print("NHANES LABS DATASET EXPLORATION")
    print("="*70)
    
    labs_file = Path(NHANES_PATH) / "labs.csv"
    
    if not labs_file.exists():
        print(f"❌ Labs file not found: {labs_file}")
        return
    
    print(f"\n✓ Loading labs data from: {labs_file}")
    labs = pd.read_csv(labs_file)
    
    print(f"\n📊 Dataset Overview:")
    print(f"  Total samples: {len(labs):,}")
    print(f"  Total columns: {len(labs.columns)}")
    
    print(f"\n📋 Available Columns:")
    for i, col in enumerate(labs.columns, 1):
        print(f"  {i:3d}. {col}")
    
    print(f"\n🔍 Sample Data (first 5 rows):")
    print(labs.head())
    
    print(f"\n📈 Basic Statistics:")
    print(labs.describe())
    
    # Check for common blood parameters
    print(f"\n🩸 Common Blood Parameters:")
    common_params = [
        'Hemoglobin', 'Hgb', 'HGB',
        'Glucose', 'GLU', 
        'Creatinine', 'CREA',
        'Cholesterol', 'CHOL',
        'Triglycerides', 'TRIG',
        'HDL', 'LDL',
        'HbA1c', 'A1C'
    ]
    
    found_params = []
    for param in common_params:
        matching_cols = [col for col in labs.columns if param.lower() in col.lower()]
        if matching_cols:
            found_params.extend(matching_cols)
            print(f"  ✓ {param}: {matching_cols}")
    
    if not found_params:
        print("  ⚠ No common parameters found with standard names")
        print("  💡 Check column names above to identify parameter columns")
    
    return labs


def explore_demographics():
    """Explore the demographic.csv file."""
    print("\n" + "="*70)
    print("NHANES DEMOGRAPHICS DATASET")
    print("="*70)
    
    demo_file = Path(NHANES_PATH) / "demographic.csv"
    
    if not demo_file.exists():
        print(f"❌ Demographics file not found: {demo_file}")
        return
    
    print(f"\n✓ Loading demographics data from: {demo_file}")
    demo = pd.read_csv(demo_file)
    
    print(f"\n📊 Dataset Overview:")
    print(f"  Total samples: {len(demo):,}")
    print(f"  Total columns: {len(demo.columns)}")
    
    print(f"\n📋 Available Columns:")
    for i, col in enumerate(demo.columns, 1):
        print(f"  {i:3d}. {col}")
    
    print(f"\n🔍 Sample Data (first 5 rows):")
    print(demo.head())
    
    # Check for age and sex columns
    print(f"\n👤 Demographic Fields:")
    age_cols = [col for col in demo.columns if 'age' in col.lower()]
    sex_cols = [col for col in demo.columns if 'sex' in col.lower() or 'gender' in col.lower()]
    
    if age_cols:
        print(f"  Age columns: {age_cols}")
    if sex_cols:
        print(f"  Sex columns: {sex_cols}")
    
    return demo


def calculate_percentiles(labs, param_col, demo=None):
    """
    Calculate percentiles for a parameter.
    
    Args:
        labs: Labs dataframe
        param_col: Parameter column name
        demo: Demographics dataframe (optional)
    """
    print(f"\n" + "="*70)
    print(f"PERCENTILE ANALYSIS: {param_col}")
    print("="*70)
    
    if param_col not in labs.columns:
        print(f"❌ Column '{param_col}' not found in labs data")
        return
    
    # Remove missing values
    data = labs[param_col].dropna()
    
    if len(data) == 0:
        print(f"❌ No valid data for {param_col}")
        return
    
    print(f"\n📊 Overall Statistics:")
    print(f"  Valid samples: {len(data):,}")
    print(f"  Mean: {data.mean():.2f}")
    print(f"  Median: {data.median():.2f}")
    print(f"  Std Dev: {data.std():.2f}")
    
    print(f"\n📈 Percentiles:")
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    for p in percentiles:
        value = data.quantile(p/100)
        print(f"  {p:2d}th percentile: {value:.2f}")
    
    # If demographics available, calculate by age/sex
    if demo is not None and 'SEQN' in labs.columns and 'SEQN' in demo.columns:
        print(f"\n👥 By Demographics:")
        
        # Merge with demographics
        merged = labs[['SEQN', param_col]].merge(demo, on='SEQN')
        
        # Find age and sex columns
        age_col = next((col for col in demo.columns if 'age' in col.lower()), None)
        sex_col = next((col for col in demo.columns if 'sex' in col.lower() or 'gender' in col.lower()), None)
        
        if sex_col:
            print(f"\n  By Sex ({sex_col}):")
            for sex_value in merged[sex_col].unique():
                if pd.notna(sex_value):
                    sex_data = merged[merged[sex_col] == sex_value][param_col].dropna()
                    if len(sex_data) > 0:
                        print(f"    {sex_value}:")
                        print(f"      Mean: {sex_data.mean():.2f}")
                        print(f"      5th-95th percentile: {sex_data.quantile(0.05):.2f} - {sex_data.quantile(0.95):.2f}")


def compare_to_reference_ranges(labs, param_col, ref_min, ref_max):
    """
    Compare NHANES data to your reference ranges.
    
    Args:
        labs: Labs dataframe
        param_col: Parameter column name
        ref_min: Your reference range minimum
        ref_max: Your reference range maximum
    """
    print(f"\n" + "="*70)
    print(f"REFERENCE RANGE COMPARISON: {param_col}")
    print("="*70)
    
    if param_col not in labs.columns:
        print(f"❌ Column '{param_col}' not found")
        return
    
    data = labs[param_col].dropna()
    
    if len(data) == 0:
        print(f"❌ No valid data")
        return
    
    # Calculate NHANES percentiles
    p5 = data.quantile(0.05)
    p95 = data.quantile(0.95)
    
    print(f"\n📊 Comparison:")
    print(f"  Your reference range: {ref_min} - {ref_max}")
    print(f"  NHANES 5th-95th percentile: {p5:.2f} - {p95:.2f}")
    
    # Calculate how many samples fall outside your range
    below = (data < ref_min).sum()
    within = ((data >= ref_min) & (data <= ref_max)).sum()
    above = (data > ref_max).sum()
    
    print(f"\n📈 Distribution:")
    print(f"  Below your range: {below:,} ({below/len(data)*100:.1f}%)")
    print(f"  Within your range: {within:,} ({within/len(data)*100:.1f}%)")
    print(f"  Above your range: {above:,} ({above/len(data)*100:.1f}%)")
    
    # Recommendation
    if p5 < ref_min or p95 > ref_max:
        print(f"\n💡 Recommendation:")
        if p5 < ref_min:
            print(f"  Consider lowering minimum to {p5:.2f} (NHANES 5th percentile)")
        if p95 > ref_max:
            print(f"  Consider raising maximum to {p95:.2f} (NHANES 95th percentile)")
    else:
        print(f"\n✓ Your reference range aligns well with NHANES population data")


def main():
    """Main exploration function."""
    print("\n🔬 NHANES Dataset Explorer")
    print("This tool helps you understand the NHANES dataset structure\n")
    
    # Explore labs
    labs = explore_labs()
    
    # Explore demographics
    demo = explore_demographics()
    
    if labs is not None:
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Identify parameter columns in the output above")
        print("2. Use calculate_percentiles() to analyze specific parameters")
        print("3. Use compare_to_reference_ranges() to validate your ranges")
        print("\nExample:")
        print("  # If you find a column named 'Hemoglobin':")
        print("  calculate_percentiles(labs, 'Hemoglobin', demo)")
        print("  compare_to_reference_ranges(labs, 'Hemoglobin', 13.0, 17.5)")
        
        return labs, demo
    
    return None, None


if __name__ == "__main__":
    labs, demo = main()
    
    # Keep variables in scope for interactive use
    if labs is not None:
        print("\n💡 Variables 'labs' and 'demo' are available for further exploration")
        print("   Try: labs.columns, labs.describe(), etc.")
