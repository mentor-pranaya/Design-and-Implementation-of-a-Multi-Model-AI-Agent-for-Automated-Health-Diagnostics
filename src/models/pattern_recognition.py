"""
Model 2: Pattern Recognition & Risk Assessment
Analyzes parameter combinations to identify patterns and calculate risk scores
"""

from typing import List, Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PatternRecognitionModel:
    """Identify clinically relevant patterns and calculate risk scores"""
    
    # Pattern definitions with required parameters and conditions
    CLINICAL_PATTERNS = {
        'metabolic_syndrome': {
            'description': 'Metabolic Syndrome Indicators',
            'criteria': {
                'GLUCOSE': {'condition': 'high', 'threshold': 100},
                'TRIGLYCERIDES': {'condition': 'high', 'threshold': 150},
                'HDL': {'condition': 'low', 'threshold': 40},
                'required_abnormalities': 2  # At least 2 of the above
            }
        },
        'diabetes_risk': {
            'description': 'Diabetes Risk Indicators',
            'criteria': {
                'GLUCOSE': {'condition': 'high', 'threshold': 100},
                'HBA1C': {'condition': 'high', 'threshold': 5.7}
            }
        },
        'cardiovascular_risk': {
            'description': 'Cardiovascular Risk Indicators',
            'criteria': {
                'CHOLESTEROL': {'condition': 'high', 'threshold': 200},
                'LDL': {'condition': 'high', 'threshold': 100},
                'HDL': {'condition': 'low', 'threshold': 40},
                'TRIGLYCERIDES': {'condition': 'high', 'threshold': 150},
                'required_abnormalities': 2
            }
        },
        'anemia_pattern': {
            'description': 'Anemia Pattern',
            'criteria': {
                'HEMOGLOBIN': {'condition': 'low', 'threshold': 12.0},
                'RBC': {'condition': 'low', 'threshold': 4.0}
            }
        },
        'kidney_dysfunction': {
            'description': 'Kidney Function Concern',
            'criteria': {
                'CREATININE': {'condition': 'high', 'threshold': 1.3},
                'BUN': {'condition': 'high', 'threshold': 20}
            }
        },
        'liver_dysfunction': {
            'description': 'Liver Function Concern',
            'criteria': {
                'ALT': {'condition': 'high', 'threshold': 56},
                'AST': {'condition': 'high', 'threshold': 40}
            }
        }
    }
    
    # Risk score calculations
    RISK_CALCULATORS = {
        'cardiovascular': {
            'factors': ['CHOLESTEROL', 'LDL', 'HDL', 'TRIGLYCERIDES'],
            'weights': {'CHOLESTEROL': 0.25, 'LDL': 0.35, 'HDL': -0.25, 'TRIGLYCERIDES': 0.25}
        },
        'diabetes': {
            'factors': ['GLUCOSE', 'HBA1C'],
            'weights': {'GLUCOSE': 0.5, 'HBA1C': 0.5}
        }
    }
    
    def __init__(self):
        self.identified_patterns = []
        self.risk_scores = {}
    
    def analyze(self, interpretations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze interpretations to identify patterns and calculate risk scores
        
        Args:
            interpretations: List of parameter interpretations from Model 1
            
        Returns:
            Dictionary containing identified patterns and risk scores
        """
        # Convert list to dictionary for easier lookup
        params_dict = {p['standard_name']: p for p in interpretations}
        
        # Identify patterns
        self.identified_patterns = self._identify_patterns(params_dict)
        
        # Calculate risk scores
        self.risk_scores = self._calculate_risk_scores(params_dict)
        
        # Calculate ratios
        ratios = self._calculate_ratios(params_dict)
        
        logger.info(f"Identified {len(self.identified_patterns)} clinical patterns")
        logger.info(f"Calculated {len(self.risk_scores)} risk scores")
        
        return {
            'patterns': self.identified_patterns,
            'risk_scores': self.risk_scores,
            'ratios': ratios,
            'overall_risk_level': self._determine_overall_risk()
        }
    
    def _identify_patterns(self, params_dict: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Identify clinical patterns based on parameter combinations"""
        patterns_found = []
        
        for pattern_name, pattern_def in self.CLINICAL_PATTERNS.items():
            criteria = pattern_def['criteria']
            required_abnormalities = criteria.get('required_abnormalities', len(criteria) - 1)
            
            abnormality_count = 0
            matching_params = []
            
            for param_name, condition_def in criteria.items():
                if param_name == 'required_abnormalities':
                    continue
                
                if param_name in params_dict:
                    param = params_dict[param_name]
                    condition = condition_def['condition']
                    threshold = condition_def['threshold']
                    value = param['value']
                    
                    # Check if condition is met
                    is_abnormal = False
                    if condition == 'high' and value > threshold:
                        is_abnormal = True
                    elif condition == 'low' and value < threshold:
                        is_abnormal = True
                    
                    if is_abnormal:
                        abnormality_count += 1
                        matching_params.append({
                            'parameter': param_name,
                            'value': value,
                            'condition': condition,
                            'threshold': threshold
                        })
            
            # Pattern found if enough abnormalities
            if abnormality_count >= required_abnormalities:
                patterns_found.append({
                    'pattern_name': pattern_name,
                    'description': pattern_def['description'],
                    'matching_parameters': matching_params,
                    'confidence': round(abnormality_count / len([k for k in criteria.keys() if k != 'required_abnormalities']), 2)
                })
        
        return patterns_found
    
    def _calculate_risk_scores(self, params_dict: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate risk scores based on parameter values"""
        risk_scores = {}
        
        # Cardiovascular risk
        if 'CHOLESTEROL' in params_dict or 'LDL' in params_dict:
            cv_score = self._calculate_cardiovascular_risk(params_dict)
            risk_scores['cardiovascular'] = cv_score
        
        # Diabetes risk
        if 'GLUCOSE' in params_dict or 'HBA1C' in params_dict:
            diabetes_score = self._calculate_diabetes_risk(params_dict)
            risk_scores['diabetes'] = diabetes_score
        
        return risk_scores
    
    def _calculate_cardiovascular_risk(self, params_dict: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate cardiovascular risk score"""
        score = 0.0
        factors_present = []
        
        # Total Cholesterol contribution
        if 'CHOLESTEROL' in params_dict:
            chol = params_dict['CHOLESTEROL']['value']
            if chol < 200:
                chol_score = 0
            elif chol < 240:
                chol_score = 1
            else:
                chol_score = 2
            score += chol_score * 0.25
            factors_present.append('cholesterol')
        
        # LDL contribution
        if 'LDL' in params_dict:
            ldl = params_dict['LDL']['value']
            if ldl < 100:
                ldl_score = 0
            elif ldl < 130:
                ldl_score = 1
            elif ldl < 160:
                ldl_score = 2
            else:
                ldl_score = 3
            score += ldl_score * 0.35
            factors_present.append('LDL')
        
        # HDL contribution (protective factor)
        if 'HDL' in params_dict:
            hdl = params_dict['HDL']['value']
            if hdl >= 60:
                hdl_score = -1  # Protective
            elif hdl >= 40:
                hdl_score = 0
            else:
                hdl_score = 1  # Risk factor
            score += hdl_score * 0.25
            factors_present.append('HDL')
        
        # Triglycerides contribution
        if 'TRIGLYCERIDES' in params_dict:
            trig = params_dict['TRIGLYCERIDES']['value']
            if trig < 150:
                trig_score = 0
            elif trig < 200:
                trig_score = 1
            else:
                trig_score = 2
            score += trig_score * 0.25
            factors_present.append('triglycerides')
        
        # Normalize score (0-10 scale)
        normalized_score = min(max(score * 2, 0), 10)
        
        risk_level = 'low' if normalized_score < 3 else 'moderate' if normalized_score < 6 else 'high'
        
        return {
            'score': round(normalized_score, 2),
            'level': risk_level,
            'factors_evaluated': factors_present,
            'description': f'Cardiovascular risk is {risk_level} based on lipid panel'
        }
    
    def _calculate_diabetes_risk(self, params_dict: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate diabetes risk score"""
        score = 0.0
        factors_present = []
        
        # Glucose contribution
        if 'GLUCOSE' in params_dict:
            glucose = params_dict['GLUCOSE']['value']
            if glucose < 100:
                glucose_score = 0
            elif glucose < 126:
                glucose_score = 1  # Pre-diabetes
            else:
                glucose_score = 2  # Diabetes range
            score += glucose_score * 0.5
            factors_present.append('glucose')
        
        # HbA1c contribution
        if 'HBA1C' in params_dict:
            hba1c = params_dict['HBA1C']['value']
            if hba1c < 5.7:
                hba1c_score = 0
            elif hba1c < 6.5:
                hba1c_score = 1  # Pre-diabetes
            else:
                hba1c_score = 2  # Diabetes range
            score += hba1c_score * 0.5
            factors_present.append('HbA1c')
        
        # Normalize score (0-10 scale)
        normalized_score = min(score * 5, 10)
        
        risk_level = 'low' if normalized_score < 3 else 'moderate' if normalized_score < 6 else 'high'
        
        return {
            'score': round(normalized_score, 2),
            'level': risk_level,
            'factors_evaluated': factors_present,
            'description': f'Diabetes risk is {risk_level} based on glucose markers'
        }
    
    def _calculate_ratios(self, params_dict: Dict[str, Dict]) -> Dict[str, Dict]:
        """Calculate clinically relevant ratios"""
        ratios = {}
        
        # Total Cholesterol / HDL ratio
        if 'CHOLESTEROL' in params_dict and 'HDL' in params_dict:
            total_chol = params_dict['CHOLESTEROL']['value']
            hdl = params_dict['HDL']['value']
            
            if hdl > 0:
                ratio = total_chol / hdl
                
                if ratio < 5:
                    interpretation = 'optimal'
                elif ratio < 6:
                    interpretation = 'acceptable'
                else:
                    interpretation = 'high risk'
                
                ratios['cholesterol_hdl_ratio'] = {
                    'value': round(ratio, 2),
                    'interpretation': interpretation,
                    'description': 'Total Cholesterol to HDL ratio'
                }
        
        # LDL / HDL ratio
        if 'LDL' in params_dict and 'HDL' in params_dict:
            ldl = params_dict['LDL']['value']
            hdl = params_dict['HDL']['value']
            
            if hdl > 0:
                ratio = ldl / hdl
                
                if ratio < 2:
                    interpretation = 'optimal'
                elif ratio < 3:
                    interpretation = 'acceptable'
                else:
                    interpretation = 'high risk'
                
                ratios['ldl_hdl_ratio'] = {
                    'value': round(ratio, 2),
                    'interpretation': interpretation,
                    'description': 'LDL to HDL ratio'
                }
        
        # BUN / Creatinine ratio
        if 'BUN' in params_dict and 'CREATININE' in params_dict:
            bun = params_dict['BUN']['value']
            creat = params_dict['CREATININE']['value']
            
            if creat > 0:
                ratio = bun / creat
                
                if 10 <= ratio <= 20:
                    interpretation = 'normal'
                elif ratio < 10:
                    interpretation = 'low (possible liver disease)'
                else:
                    interpretation = 'high (possible dehydration or kidney issue)'
                
                ratios['bun_creatinine_ratio'] = {
                    'value': round(ratio, 2),
                    'interpretation': interpretation,
                    'description': 'BUN to Creatinine ratio'
                }
        
        return ratios
    
    def _determine_overall_risk(self) -> Dict[str, Any]:
        """Determine overall health risk level"""
        if not self.risk_scores and not self.identified_patterns:
            return {
                'level': 'low',
                'description': 'No significant risk patterns identified'
            }
        
        # Count high-risk indicators
        high_risk_count = 0
        moderate_risk_count = 0
        
        for risk_name, risk_data in self.risk_scores.items():
            if risk_data['level'] == 'high':
                high_risk_count += 1
            elif risk_data['level'] == 'moderate':
                moderate_risk_count += 1
        
        # Determine overall level
        if high_risk_count >= 2 or len(self.identified_patterns) >= 2:
            level = 'high'
            description = 'Multiple risk factors or patterns identified - recommend medical consultation'
        elif high_risk_count >= 1 or len(self.identified_patterns) >= 1:
            level = 'moderate'
            description = 'Some risk factors identified - monitoring recommended'
        elif moderate_risk_count >= 2:
            level = 'moderate'
            description = 'Moderate risk - lifestyle modifications recommended'
        else:
            level = 'low'
            description = 'Low overall risk based on available data'
        
        return {
            'level': level,
            'description': description,
            'patterns_found': len(self.identified_patterns),
            'high_risk_scores': high_risk_count
        }
    
    def get_pattern_summary(self) -> str:
        """Generate human-readable pattern summary"""
        if not self.identified_patterns:
            return "No significant clinical patterns identified."
        
        summary = f"Identified {len(self.identified_patterns)} clinical pattern(s):\n\n"
        
        for i, pattern in enumerate(self.identified_patterns, 1):
            summary += f"{i}. {pattern['description']}\n"
            summary += f"   Confidence: {pattern['confidence']*100:.0f}%\n"
            summary += "   Based on:\n"
            for param in pattern['matching_parameters']:
                summary += f"   - {param['parameter']}: {param['value']} ({param['condition']} threshold: {param['threshold']})\n"
            summary += "\n"
        
        return summary
    
    def get_risk_summary(self) -> str:
        """Generate human-readable risk summary"""
        if not self.risk_scores:
            return "Insufficient data to calculate risk scores."
        
        summary = "Risk Assessment:\n\n"
        
        for risk_name, risk_data in self.risk_scores.items():
            summary += f"{risk_name.title()} Risk:\n"
            summary += f"  Score: {risk_data['score']}/10 ({risk_data['level']})\n"
            summary += f"  {risk_data['description']}\n\n"
        
        return summary