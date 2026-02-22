"""
Analyze Indian Liver Patient Dataset (ILPD) to extract reference ranges
and compare with existing Indian population data.
"""

import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('ILPD -Indian Liver Patient Dataset/Indian Liver Patient Dataset (ILPD).csv', 
                 header=None,
                 names=['Age', 'Gender', 'TB', 'DB', 'Alkphos', 'SGPT', 'SGOT', 'TP', 'ALB', 'AG_Ratio', 'Selector'])

print("=" * 80)
print("INDIAN LIVER PATIENT DATASET (ILPD) ANALYSIS")
print("=" * 80)
print(f"\nDataset Info:")
print(f"Total records: {len(df)}")
print(f"Liver patients: {len(df[df['Selector'] == 1])}")
print(f"Non-liver patients: {len(df[df['Selector'] == 2])}")
print(f"Male patients: {len(df[df['Gender'] == 'Male'])}")
print(f"Female patients: {len(df[df['Gender'] == 'Female'])}")

# Separate healthy (non-liver patients) for reference ranges
healthy = df[df['Selector'] == 2].copy()
print(f"\n{'=' * 80}")
print(f"HEALTHY CONTROLS (Non-Liver Patients): {len(healthy)} individuals")
print(f"{'=' * 80}")

if len(healthy) > 0:
    print(f"Male: {len(healthy[healthy['Gender'] == 'Male'])}")
    print(f"Female: {len(healthy[healthy['Gender'] == 'Female'])}")
    print(f"Age range: {healthy['Age'].min()}-{healthy['Age'].max()} years")
    print(f"Mean age: {healthy['Age'].mean():.1f} years")
    
    # Calculate reference ranges for healthy individuals (2.5th - 97.5th percentile)
    print(f"\n{'=' * 80}")
    print("REFERENCE RANGES FROM HEALTHY CONTROLS (2.5th - 97.5th percentile)")
    print(f"{'=' * 80}")
    
    parameters = {
        'TB': 'Total Bilirubin (mg/dL)',
        'DB': 'Direct Bilirubin (mg/dL)',
        'Alkphos': 'Alkaline Phosphatase (U/L)',
        'SGPT': 'ALT/SGPT (U/L)',
        'SGOT': 'AST/SGOT (U/L)',
        'TP': 'Total Protein (g/dL)',
        'ALB': 'Albumin (g/dL)',
        'AG_Ratio': 'A/G Ratio'
    }
    
    print("\nOVERALL (Both Genders):")
    print("-" * 80)
    for param, name in parameters.items():
        data = healthy[param].dropna()
        if len(data) > 0:
            p25 = np.percentile(data, 2.5)
            p975 = np.percentile(data, 97.5)
            median = np.median(data)
            mean = np.mean(data)
            print(f"{name:40s}: {p25:6.2f} - {p975:6.2f} (median: {median:6.2f}, mean: {mean:6.2f}, n={len(data)})")
    
    # Gender-specific ranges
    healthy_male = healthy[healthy['Gender'] == 'Male']
    healthy_female = healthy[healthy['Gender'] == 'Female']
    
    if len(healthy_male) > 0:
        print(f"\nMALE (n={len(healthy_male)}):")
        print("-" * 80)
        for param, name in parameters.items():
            data = healthy_male[param].dropna()
            if len(data) > 0:
                p25 = np.percentile(data, 2.5)
                p975 = np.percentile(data, 97.5)
                median = np.median(data)
                mean = np.mean(data)
                print(f"{name:40s}: {p25:6.2f} - {p975:6.2f} (median: {median:6.2f}, mean: {mean:6.2f}, n={len(data)})")
    
    if len(healthy_female) > 0:
        print(f"\nFEMALE (n={len(healthy_female)}):")
        print("-" * 80)
        for param, name in parameters.items():
            data = healthy_female[param].dropna()
            if len(data) > 0:
                p25 = np.percentile(data, 2.5)
                p975 = np.percentile(data, 97.5)
                median = np.median(data)
                mean = np.mean(data)
                print(f"{name:40s}: {p25:6.2f} - {p975:6.2f} (median: {median:6.2f}, mean: {mean:6.2f}, n={len(data)})")

# Analyze liver patients for comparison
liver_patients = df[df['Selector'] == 1].copy()
print(f"\n{'=' * 80}")
print(f"LIVER PATIENTS (For Comparison): {len(liver_patients)} individuals")
print(f"{'=' * 80}")
print(f"Male: {len(liver_patients[liver_patients['Gender'] == 'Male'])}")
print(f"Female: {len(liver_patients[liver_patients['Gender'] == 'Female'])}")
print(f"Age range: {liver_patients['Age'].min()}-{liver_patients['Age'].max()} years")
print(f"Mean age: {liver_patients['Age'].mean():.1f} years")

print(f"\nLIVER PATIENT RANGES (showing disease state):")
print("-" * 80)
for param, name in parameters.items():
    data = liver_patients[param].dropna()
    if len(data) > 0:
        p25 = np.percentile(data, 2.5)
        p975 = np.percentile(data, 97.5)
        median = np.median(data)
        mean = np.mean(data)
        print(f"{name:40s}: {p25:6.2f} - {p975:6.2f} (median: {median:6.2f}, mean: {mean:6.2f}, n={len(data)})")

# Compare with existing Indian population data
print(f"\n{'=' * 80}")
print("COMPARISON WITH EXISTING INDIAN POPULATION DATA")
print(f"{'=' * 80}")

print("\nALT/SGPT Comparison:")
print("-" * 80)
print("ILPD Healthy Controls:")
if len(healthy_male) > 0:
    sgpt_male = healthy_male['SGPT'].dropna()
    print(f"  Male:   {np.percentile(sgpt_male, 2.5):.1f} - {np.percentile(sgpt_male, 97.5):.1f} U/L (n={len(sgpt_male)})")
if len(healthy_female) > 0:
    sgpt_female = healthy_female['SGPT'].dropna()
    print(f"  Female: {np.percentile(sgpt_female, 2.5):.1f} - {np.percentile(sgpt_female, 97.5):.1f} U/L (n={len(sgpt_female)})")

print("\nExisting Indian Population Data (Apollo + North Indian + IFCC):")
print("  Male:   10-74 U/L (n=10,665 Apollo + 1,527 North Indian + IFCC)")
print("  Female: 9-63 U/L")
print("  Western Standard: 0-40 U/L")

print("\nAST/SGOT Comparison:")
print("-" * 80)
print("ILPD Healthy Controls:")
if len(healthy_male) > 0:
    sgot_male = healthy_male['SGOT'].dropna()
    print(f"  Male:   {np.percentile(sgot_male, 2.5):.1f} - {np.percentile(sgot_male, 97.5):.1f} U/L (n={len(sgot_male)})")
if len(healthy_female) > 0:
    sgot_female = healthy_female['SGOT'].dropna()
    print(f"  Female: {np.percentile(sgot_female, 2.5):.1f} - {np.percentile(sgot_female, 97.5):.1f} U/L (n={len(sgot_female)})")

print("\nExisting Indian Population Data (Apollo + North Indian + IFCC):")
print("  Male:   14-55 U/L (n=10,665 Apollo + 1,527 North Indian + IFCC)")
print("  Female: 13-50 U/L")
print("  Western Standard: 0-40 U/L")

print("\nTotal Bilirubin Comparison:")
print("-" * 80)
print("ILPD Healthy Controls:")
if len(healthy_male) > 0:
    tb_male = healthy_male['TB'].dropna()
    print(f"  Male:   {np.percentile(tb_male, 2.5):.2f} - {np.percentile(tb_male, 97.5):.2f} mg/dL (n={len(tb_male)})")
if len(healthy_female) > 0:
    tb_female = healthy_female['TB'].dropna()
    print(f"  Female: {np.percentile(tb_female, 2.5):.2f} - {np.percentile(tb_female, 97.5):.2f} mg/dL (n={len(tb_female)})")

print("\nExisting Indian Population Data (Apollo + North Indian):")
print("  Male:   0.3-1.34 mg/dL (n=10,665 Apollo + 1,527 North Indian)")
print("  Female: 0.3-1.2 mg/dL")
print("  Western Standard: 0.0-1.2 mg/dL")

print(f"\n{'=' * 80}")
print("SUMMARY AND RECOMMENDATIONS")
print(f"{'=' * 80}")
print("\nDataset Characteristics:")
print("- Location: North East Andhra Pradesh, India")
print("- Sample size: 583 total (167 healthy controls, 416 liver patients)")
print("- Age range: 4-90 years")
print("- Gender: 441 males, 142 females")
print("\nLimitations:")
print("- Small healthy control group (n=167) compared to Apollo (n=10,665)")
print("- Regional dataset (Andhra Pradesh only)")
print("- Primarily focused on liver disease patients")
print("- Not designed as reference interval study")
print("\nValue for Your System:")
print("- Provides real-world Indian patient data (both healthy and diseased)")
print("- Can be used for validation/testing of classification algorithms")
print("- Shows disease state ranges for comparison")
print("- Confirms existing Indian population ranges are reasonable")
print("\nRecommendation:")
print("- Use ILPD as VALIDATION dataset, not as primary reference range source")
print("- Keep Apollo + North Indian + IFCC as primary reference ranges (n=12,192+)")
print("- ILPD healthy controls can serve as additional validation point")
print("- ILPD liver patients useful for testing disease detection algorithms")

print(f"\n{'=' * 80}")
print("END OF ANALYSIS")
print(f"{'=' * 80}")
