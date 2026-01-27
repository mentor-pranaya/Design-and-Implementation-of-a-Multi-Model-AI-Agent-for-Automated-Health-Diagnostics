import json
import os


class ReferenceLoader:
    
    
    _instance = None
    _data = None
    
    def __new__(cls):
        """Singleton pattern - only one instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance
    
    def _load_data(self):
        """Load reference data from JSON file"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "reference_ranges.json")
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Reference file not found: {json_path}")
            self._data = {"parameters": {}, "risk_thresholds": {}, "patterns": {}}
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in reference file: {e}")
            self._data = {"parameters": {}, "risk_thresholds": {}, "patterns": {}}
    
    def _get_age_group(self, age):
        """Convert numeric age to age group"""
        if age is None:
            return "adult"
        
        if age < 1/12:  # Less than 1 month
            return "neonate"
        elif age < 1:   # Less than 1 year
            return "infant"
        elif age < 13:
            return "child"
        elif age < 18:
            return "teenager"
        elif age < 60:
            return "adult"
        else:
            return "senior"
    
    def get_parameter_range(self, param_name, gender=None, age=None, age_group=None):
        
        params = self._data.get("parameters", {})
        param_data = params.get(param_name)
        
        if not param_data:
            return None
        
        # Determine age group
        if age_group is None and age is not None:
            age_group = self._get_age_group(age)
        elif age_group is None:
            age_group = "adult"
        
        # Priority 1: Gender + Age specific
        if gender:
            gender_lower = gender.lower()
            if gender_lower in param_data:
                gender_data = param_data[gender_lower]
                
                # Check if gender_data is nested by age group
                if isinstance(gender_data, dict):
                    # Check for specific age group
                    if age_group in gender_data:
                        age_data = gender_data[age_group]
                        if "min" in age_data and "max" in age_data:
                            return (age_data["min"], age_data["max"])
                    
                    # Fallback to adult if specific age group not found
                    if "adult" in gender_data:
                        adult_data = gender_data["adult"]
                        if "min" in adult_data and "max" in adult_data:
                            return (adult_data["min"], adult_data["max"])
                    
                    # If gender_data has direct min/max (old format)
                    if "min" in gender_data and "max" in gender_data:
                        return (gender_data["min"], gender_data["max"])
        
        # Priority 2: General range
        if "general" in param_data:
            general_data = param_data["general"]
            if "min" in general_data and "max" in general_data:
                return (general_data["min"], general_data["max"])
        
        return None
    
    def get_parameter_unit(self, param_name):
        
        params = self._data.get("parameters", {})
        param_data = params.get(param_name, {})
        return param_data.get("unit", "")
    
    def get_parameter_description(self, param_name):
        
        params = self._data.get("parameters", {})
        param_data = params.get(param_name, {})
        return param_data.get("description", "")
    
    def get_risk_thresholds(self, category):
        
        thresholds = self._data.get("risk_thresholds", {})
        return thresholds.get(category, {})
    
    def get_pattern_config(self, pattern_name):
        
        patterns = self._data.get("patterns", {})
        return patterns.get(pattern_name, {})
    
    def get_all_parameters(self):
        
        return list(self._data.get("parameters", {}).keys())
    
    def get_all_patterns(self):
        
        return list(self._data.get("patterns", {}).keys())
    
    def get_metadata(self):
        
        return self._data.get("metadata", {})
    
    def reload(self):
        
        self._load_data()


# Create a global instance for easy access
reference_data = ReferenceLoader()

# Helper functions for direct access

def get_range(param_name, gender=None, age=None, age_group=None):
    
    return reference_data.get_parameter_range(param_name, gender, age, age_group)


def get_unit(param_name):
    
    return reference_data.get_parameter_unit(param_name)


def get_description(param_name):
    
    return reference_data.get_parameter_description(param_name)


def get_thresholds(category):
    
    return reference_data.get_risk_thresholds(category)


def get_pattern(pattern_name):
    
    return reference_data.get_pattern_config(pattern_name)


def get_age_group(age):
    
    return reference_data._get_age_group(age)