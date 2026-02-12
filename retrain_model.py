import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.predictor import _train_and_save, MODEL_PATH, SCALER_PATH

def main():
    print("FORCING MODEL RETRAINING")
    print("========================")
    
    # Remove old model files if they exist
    if os.path.exists(MODEL_PATH):
        try:
            os.remove(MODEL_PATH)
            print(f"Removed old model: {MODEL_PATH}")
        except Exception as e:
            print(f"Error removing model: {e}")

    if os.path.exists(SCALER_PATH):
        try:
            os.remove(SCALER_PATH)
            print(f"Removed old scaler: {SCALER_PATH}")
        except Exception as e:
            print(f"Error removing scaler: {e}")
            
    try:
        print("Starting training process...")
        model, scaler = _train_and_save()
        print("SUCCESS: Model retrained and saved.")
    except Exception as e:
        print(f"FAILURE: Training failed - {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
