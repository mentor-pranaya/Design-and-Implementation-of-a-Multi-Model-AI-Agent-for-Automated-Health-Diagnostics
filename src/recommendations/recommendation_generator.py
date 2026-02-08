"""
Personalized Recommendation Generator
Creates actionable health advice based on synthesized findings
"""

from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationGenerator:
    """Generate personalized health recommendations"""
    
    # Recommendation templates for different conditions
    RECOMMENDATIONS_DB = {
        'GLUCOSE': {
            'high': {
                'dietary': [
                    'Reduce intake of refined carbohydrates and sugary foods',
                    'Increase fiber-rich foods (vegetables, whole grains, legumes)',
                    'Choose low glycemic index foods',
                    'Limit fruit juice and sweetened beverages'
                ],
                'lifestyle': [
                    'Regular physical activity (150 minutes/week of moderate exercise)',
                    'Maintain healthy weight',
                    'Monitor blood glucose regularly',
                    'Stay hydrated with water'
                ],
                'medical': [
                    'Consult endocrinologist or primary care physician',
                    'Consider HbA1c testing',
                    'Discuss diabetes screening if not already diagnosed'
                ]
            },
            'low': {
                'dietary': ['Eat small, frequent meals', 'Include complex carbohydrates in diet'],
                'medical': ['Consult physician to rule out hypoglycemia']
            }
        },
        'CHOLESTEROL': {
            'high': {
                'dietary': [
                    'Reduce saturated fat intake (limit red meat, full-fat dairy)',
                    'Increase soluble fiber (oats, beans, apples)',
                    'Add omega-3 fatty acids (fish, walnuts, flaxseed)',
                    'Use healthy oils (olive oil, avocado oil)'
                ],
                'lifestyle': [
                    'Regular aerobic exercise (30 minutes daily)',
                    'Maintain healthy weight',
                    'Quit smoking if applicable',
                    'Limit alcohol consumption'
                ],
                'medical': [
                    'Consult cardiologist or lipid specialist',
                    'Discuss statin therapy if appropriate',
                    'Regular lipid panel monitoring'
                ]
            }
        },
        'HDL': {
            'low': {
                'dietary': ['Include healthy fats (nuts, avocados, olive oil)', 'Eat fatty fish 2-3 times per week'],
                'lifestyle': ['Regular aerobic exercise', 'Quit smoking', 'Maintain healthy weight'],
                'medical': ['Discuss with physician about raising HDL levels']
            }
        },
        'LDL': {
            'high': {
                'dietary': ['Reduce saturated and trans fats', 'Increase soluble fiber intake', 'Add plant sterols/stanols'],
                'lifestyle': ['Regular exercise', 'Weight management'],
                'medical': ['Consult about statin therapy', 'Regular monitoring']
            }
        },
        'TRIGLYCERIDES': {
            'high': {
                'dietary': ['Limit simple sugars and refined carbs', 'Reduce alcohol', 'Increase omega-3 intake'],
                'lifestyle': ['Regular exercise', 'Weight loss if overweight', 'Limit alcohol'],
                'medical': ['Consult physician', 'Rule out secondary causes']
            }
        },
        'HEMOGLOBIN': {
            'low': {
                'dietary': ['Increase iron-rich foods (red meat, spinach, fortified cereals)', 'Vitamin C with meals to enhance iron absorption'],
                'medical': ['Consult for anemia evaluation', 'Check iron levels and B12', 'Rule out blood loss']
            }
        },
        'CREATININE': {
            'high': {
                'dietary': ['Limit protein intake if advised', 'Stay well hydrated', 'Reduce salt intake'],
                'lifestyle': ['Monitor blood pressure', 'Avoid nephrotoxic medications'],
                'medical': ['Consult nephrologist', 'Kidney function tests', 'Check for underlying causes']
            }
        },
        'ALT': {
            'high': {
                'dietary': ['Limit alcohol', 'Reduce fatty foods', 'Maintain healthy weight'],
                'lifestyle': ['Regular exercise', 'Avoid hepatotoxic substances'],
                'medical': ['Consult hepatologist', 'Liver function assessment', 'Rule out hepatitis']
            }
        },
        'AST': {
            'high': {
                'dietary': ['Limit alcohol consumption', 'Healthy balanced diet'],
                'medical': ['Liver function evaluation', 'Rule out liver disease']
            }
        }
    }
    
    # Pattern-based recommendations
    PATTERN_RECOMMENDATIONS = {
        'metabolic_syndrome': {
            'dietary': [
                'Follow Mediterranean-style diet',
                'Reduce processed foods and added sugars',
                'Increase vegetables, fruits, and whole grains',
                'Control portion sizes'
            ],
            'lifestyle': [
                'Aim for 7-9 hours of quality sleep',
                'Regular physical activity (mix of cardio and strength training)',
                'Stress management techniques',
                'Weight loss of 5-10% if overweight'
            ],
            'medical': [
                'Comprehensive metabolic evaluation',
                'Regular monitoring of glucose, lipids, and blood pressure',
                'Discuss preventive medications if appropriate'
            ]
        },
        'cardiovascular_risk': {
            'dietary': [
                'Heart-healthy diet (low saturated fat, high fiber)',
                'Reduce sodium intake (<2300mg/day)',
                'Increase potassium-rich foods',
                'Limit trans fats and cholesterol'
            ],
            'lifestyle': [
                'Regular cardiovascular exercise',
                'Stress management',
                'Maintain healthy BMI',
                'No smoking'
            ],
            'medical': [
                'Cardiology consultation',
                'Blood pressure monitoring',
                'Consider cardiac risk assessment',
                'Discuss preventive strategies'
            ]
        },
        'diabetes_risk': {
            'dietary': [
                'Low glycemic index diet',
                'Carbohydrate counting or plate method',
                'Consistent meal timing',
                'Limit sugary beverages'
            ],
            'lifestyle': [
                'Regular glucose monitoring',
                'Weight management',
                'Daily physical activity',
                'Foot care and regular check-ups'
            ],
            'medical': [
                'Endocrinology referral',
                'Diabetes education program',
                'Regular HbA1c monitoring',
                'Eye and kidney function checks'
            ]
        }
    }
    
    def __init__(self):
        self.recommendations = {}
    
    def generate(self,
                synthesized_findings: Dict[str, Any],
                pattern_analysis: Dict[str, Any],
                user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate personalized recommendations
        
        Args:
            synthesized_findings: Output from FindingsSynthesizer
            pattern_analysis: Output from PatternRecognitionModel
            user_context: Optional user data (age, gender, etc.)
            
        Returns:
            Dictionary of recommendations
        """
        
        recommendations = {
            'dietary': [],
            'lifestyle': [],
            'medical': [],
            'monitoring': [],
            'immediate_actions': []
        }
        
        # Generate recommendations for abnormal parameters
        categorized = synthesized_findings['categorized_parameters']
        
        for param in categorized['critical'] + categorized['abnormal']:
            param_recs = self._get_parameter_recommendations(param)
            self._merge_recommendations(recommendations, param_recs)
        
        # Generate pattern-based recommendations
        for pattern in pattern_analysis.get('patterns', []):
            pattern_recs = self._get_pattern_recommendations(pattern)
            self._merge_recommendations(recommendations, pattern_recs)
        
        # Add immediate actions for critical findings
        if categorized['critical']:
            recommendations['immediate_actions'].append({
                'priority': 'critical',
                'action': 'Seek immediate medical attention',
                'reason': 'Critical values detected in blood work'
            })
        
        # Add monitoring recommendations
        recommendations['monitoring'] = self._generate_monitoring_plan(
            categorized,
            pattern_analysis
        )
        
        # Remove duplicates
        for category in ['dietary', 'lifestyle', 'medical']:
            recommendations[category] = list(set(recommendations[category]))
        
        # Add general wellness recommendations
        if not (categorized['critical'] or categorized['abnormal']):
            recommendations['lifestyle'].append('Continue maintaining healthy lifestyle habits')
            recommendations['dietary'].append('Maintain balanced, nutritious diet')
        
        self.recommendations = recommendations
        
        logger.info(f"Generated {sum(len(v) if isinstance(v, list) else 0 for v in recommendations.values())} recommendations")
        
        return recommendations
    
    def _get_parameter_recommendations(self, param: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get recommendations for a specific parameter"""
        param_name = param['name']
        status = param['status']
        
        recommendations = {'dietary': [], 'lifestyle': [], 'medical': []}
        
        # Determine if high or low
        condition = 'high' if 'high' in status else 'low' if 'low' in status else None
        
        if param_name in self.RECOMMENDATIONS_DB and condition:
            param_recs = self.RECOMMENDATIONS_DB[param_name].get(condition, {})
            recommendations['dietary'] = param_recs.get('dietary', [])
            recommendations['lifestyle'] = param_recs.get('lifestyle', [])
            recommendations['medical'] = param_recs.get('medical', [])
        
        return recommendations
    
    def _get_pattern_recommendations(self, pattern: Dict[str, Any]) -> Dict[str, List[str]]:
        """Get recommendations for identified patterns"""
        pattern_name = pattern['pattern_name']
        
        recommendations = {'dietary': [], 'lifestyle': [], 'medical': []}
        
        if pattern_name in self.PATTERN_RECOMMENDATIONS:
            pattern_recs = self.PATTERN_RECOMMENDATIONS[pattern_name]
            recommendations['dietary'] = pattern_recs.get('dietary', [])
            recommendations['lifestyle'] = pattern_recs.get('lifestyle', [])
            recommendations['medical'] = pattern_recs.get('medical', [])
        
        return recommendations
    
    def _merge_recommendations(self, 
                              target: Dict[str, List], 
                              source: Dict[str, List]):
        """Merge recommendations without duplicates"""
        for category in ['dietary', 'lifestyle', 'medical']:
            target[category].extend(source.get(category, []))
    
    def _generate_monitoring_plan(self,
                                  categorized_params: Dict[str, List],
                                  pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate monitoring recommendations"""
        monitoring = []
        
        # Regular check-ups
        if categorized_params['abnormal'] or pattern_analysis.get('patterns'):
            monitoring.append({
                'test': 'Repeat blood work',
                'frequency': '3-6 months',
                'reason': 'Monitor abnormal values'
            })
        
        # Specific monitoring based on patterns
        if any(p['pattern_name'] == 'diabetes_risk' for p in pattern_analysis.get('patterns', [])):
            monitoring.append({
                'test': 'HbA1c and fasting glucose',
                'frequency': 'Every 3 months',
                'reason': 'Diabetes risk management'
            })
        
        if any(p['pattern_name'] == 'cardiovascular_risk' for p in pattern_analysis.get('patterns', [])):
            monitoring.append({
                'test': 'Lipid panel and blood pressure',
                'frequency': 'Every 3-6 months',
                'reason': 'Cardiovascular risk management'
            })
        
        # Borderline monitoring
        if categorized_params['borderline']:
            monitoring.append({
                'test': 'Repeat parameters: ' + ', '.join([p['name'] for p in categorized_params['borderline']]),
                'frequency': '6-12 months',
                'reason': 'Track borderline values'
            })
        
        return monitoring
    
    def format_recommendations(self) -> str:
        """Format recommendations as readable text"""
        if not self.recommendations:
            return "No recommendations generated"
        
        output = "PERSONALIZED HEALTH RECOMMENDATIONS\n"
        output += "=" * 60 + "\n\n"
        
        # Immediate actions
        if self.recommendations['immediate_actions']:
            output += "⚠️ IMMEDIATE ACTIONS REQUIRED:\n"
            for action in self.recommendations['immediate_actions']:
                output += f"  • {action['action']}\n"
                output += f"    Reason: {action['reason']}\n"
            output += "\n"
        
        # Medical recommendations
        if self.recommendations['medical']:
            output += "MEDICAL CONSULTATION:\n"
            for i, rec in enumerate(self.recommendations['medical'], 1):
                output += f"  {i}. {rec}\n"
            output += "\n"
        
        # Dietary recommendations
        if self.recommendations['dietary']:
            output += "DIETARY RECOMMENDATIONS:\n"
            for i, rec in enumerate(self.recommendations['dietary'], 1):
                output += f"  {i}. {rec}\n"
            output += "\n"
        
        # Lifestyle recommendations
        if self.recommendations['lifestyle']:
            output += "LIFESTYLE MODIFICATIONS:\n"
            for i, rec in enumerate(self.recommendations['lifestyle'], 1):
                output += f"  {i}. {rec}\n"
            output += "\n"
        
        # Monitoring plan
        if self.recommendations['monitoring']:
            output += "MONITORING PLAN:\n"
            for mon in self.recommendations['monitoring']:
                output += f"  • {mon['test']}\n"
                output += f"    Frequency: {mon['frequency']}\n"
                output += f"    Reason: {mon['reason']}\n\n"
        
        output += "=" * 60 + "\n"
        output += "DISCLAIMER: These recommendations are AI-generated and should\n"
        output += "not replace professional medical advice. Always consult with\n"
        output += "qualified healthcare providers for medical decisions.\n"
        
        return output