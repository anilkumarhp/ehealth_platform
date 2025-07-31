"""
OCR service for prescription image processing
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, Any, Optional
import re
import asyncio
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import OCRProcessingException, InvalidPrescriptionImageException

logger = logging.getLogger(__name__)


class PrescriptionOCR:
    """OCR service for processing prescription images."""
    
    def __init__(self):
        self.tesseract_cmd = settings.TESSERACT_CMD
        self.confidence_threshold = settings.OCR_CONFIDENCE_THRESHOLD
        
        # Set Tesseract command path
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
    
    async def process_prescription_image(self, image_path: str) -> Dict[str, Any]:
        """Process prescription image and extract text."""
        try:
            # Validate image file
            if not Path(image_path).exists():
                raise InvalidPrescriptionImageException("Image file not found")
            
            # Preprocess image
            processed_image = await self._preprocess_image(image_path)
            
            # Extract text using OCR
            ocr_result = await self._extract_text(processed_image)
            
            # Parse prescription data
            parsed_data = await self._parse_prescription_text(ocr_result["text"])
            
            # Combine results
            result = {
                "text": ocr_result["text"],
                "confidence": ocr_result["confidence"],
                "parsed_data": parsed_data,
                "success": True
            }
            
            logger.info(f"OCR processing completed with {ocr_result['confidence']}% confidence")
            return result
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise OCRProcessingException(str(e))
    
    async def _preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise InvalidPrescriptionImageException("Unable to read image file")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up the image
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
            
            # Resize image if too small
            height, width = cleaned.shape
            if height < 300 or width < 300:
                scale_factor = max(300 / height, 300 / width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                cleaned = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise InvalidPrescriptionImageException(f"Image preprocessing failed: {e}")
    
    async def _extract_text(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract text from preprocessed image."""
        try:
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:()[]{}/-+*=@#$%^&!?"\' '
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(
                image, 
                config=custom_config, 
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return {
                "text": text.strip(),
                "confidence": round(avg_confidence, 2),
                "word_count": len([word for word in data['text'] if word.strip()])
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise OCRProcessingException(f"Text extraction failed: {e}")
    
    async def _parse_prescription_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text to identify prescription components."""
        try:
            parsed_data = {
                "patient_name": None,
                "doctor_name": None,
                "medicines": [],
                "date": None,
                "clinic_name": None
            }
            
            lines = text.split('\n')
            
            # Patterns for different components
            patterns = {
                "patient_name": r"(?:patient|name|pt\.?)\s*:?\s*([A-Za-z\s]+)",
                "doctor_name": r"(?:dr\.?|doctor|physician)\s*:?\s*([A-Za-z\s]+)",
                "date": r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                "medicine": r"(?:rx|medication|medicine|drug)\s*:?\s*([A-Za-z0-9\s]+(?:\d+\s*mg)?)",
                "dosage": r"(\d+\s*(?:mg|ml|tablets?|capsules?))",
                "frequency": r"(?:take|use)\s*(\d+\s*times?\s*(?:daily|per day|a day))"
            }
            
            # Extract patient name
            for line in lines[:5]:  # Usually in first few lines
                match = re.search(patterns["patient_name"], line, re.IGNORECASE)
                if match:
                    parsed_data["patient_name"] = match.group(1).strip()
                    break
            
            # Extract doctor name
            for line in lines:
                match = re.search(patterns["doctor_name"], line, re.IGNORECASE)
                if match:
                    parsed_data["doctor_name"] = match.group(1).strip()
                    break
            
            # Extract date
            date_match = re.search(patterns["date"], text)
            if date_match:
                parsed_data["date"] = date_match.group(1)
            
            # Extract medicines (simplified)
            medicine_lines = []
            for line in lines:
                # Look for lines that might contain medicine names
                if any(keyword in line.lower() for keyword in ['mg', 'ml', 'tablet', 'capsule', 'syrup']):
                    medicine_lines.append(line.strip())
            
            parsed_data["medicines"] = medicine_lines[:10]  # Limit to 10 medicines
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            return {"error": str(e)}
    
    async def validate_prescription_image(self, image_path: str) -> Dict[str, Any]:
        """Validate if image is a valid prescription."""
        try:
            # Basic validation
            if not Path(image_path).exists():
                return {"valid": False, "reason": "File not found"}
            
            # Check file size (should be reasonable)
            file_size = Path(image_path).stat().st_size
            if file_size > 20 * 1024 * 1024:  # 20MB limit
                return {"valid": False, "reason": "File too large"}
            
            if file_size < 1024:  # 1KB minimum
                return {"valid": False, "reason": "File too small"}
            
            # Try to read image
            image = cv2.imread(image_path)
            if image is None:
                return {"valid": False, "reason": "Invalid image format"}
            
            # Check image dimensions
            height, width = image.shape[:2]
            if height < 100 or width < 100:
                return {"valid": False, "reason": "Image resolution too low"}
            
            # Quick OCR test to see if any text is detected
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            
            if len(text.strip()) < 10:
                return {"valid": False, "reason": "No readable text detected"}
            
            return {"valid": True, "reason": "Image appears to be a valid prescription"}
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return {"valid": False, "reason": f"Validation error: {e}"}