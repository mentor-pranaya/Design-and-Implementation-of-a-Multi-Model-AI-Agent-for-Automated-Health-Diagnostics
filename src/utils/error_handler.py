"""
Error Handling Module
Centralized error handling for the application
"""

import traceback
from datetime import datetime


class ErrorHandler:
    """
    Centralized error handler
    """
    
    ERROR_MESSAGES = {
        "FILE_NOT_FOUND": "The specified file could not be found.",
        "INVALID_FILE_TYPE": "The file type is not supported. Please upload an image, PDF, or JSON file.",
        "OCR_FAILED": "Failed to extract text from the image. Please ensure the image is clear and readable.",
        "PDF_EXTRACTION_FAILED": "Failed to extract text from the PDF. The file may be corrupted or password-protected.",
        "NO_PARAMETERS_FOUND": "No blood parameters could be extracted from the report. Please check the file content.",
        "INVALID_JSON": "The JSON file is not properly formatted.",
        "PROCESSING_ERROR": "An error occurred during processing. Please try again.",
        "AGE_PARSE_ERROR": "Could not determine patient age from the report.",
        "GENDER_PARSE_ERROR": "Could not determine patient gender from the report."
    }
    
    @classmethod
    def get_user_message(cls, error_code):
        """Get user-friendly error message"""
        return cls.ERROR_MESSAGES.get(error_code, "An unexpected error occurred.")
    
    @classmethod
    def create_error_response(cls, error_code, technical_details=None, exception=None):
        """Create structured error response"""
        return {
            "success": False,
            "error_code": error_code,
            "message": cls.get_user_message(error_code),
            "technical_details": technical_details,
            "exception": str(exception) if exception else None,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc() if exception else None
        }


def handle_error(error_code, technical_details=None, exception=None):
    """
    Convenience function to handle errors
    """
    return ErrorHandler.create_error_response(error_code, technical_details, exception)