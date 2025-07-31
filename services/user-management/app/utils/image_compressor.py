from PIL import Image
import io
import base64
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ImageCompressor:
    @staticmethod
    def compress_base64_image(base64_data: str, max_size_kb: int = 500, quality: int = 85, max_width: int = 800) -> str:
        """
        Compress a base64 encoded image
        
        Args:
            base64_data: Base64 encoded image string
            max_size_kb: Maximum file size in KB (default: 500KB)
            quality: JPEG quality (1-100, default: 85)
            max_width: Maximum width in pixels (default: 800px)
        
        Returns:
            Compressed base64 encoded image string
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_data:
                header, base64_data = base64_data.split(",", 1)
            else:
                header = "data:image/jpeg;base64"
            
            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_data)
            original_size_kb = len(image_bytes) / 1024
            
            print(f"Original image size: {original_size_kb:.1f}KB")
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized to: {image.width}x{image.height}")
            
            # Compress with different quality levels until size is acceptable
            for attempt_quality in [quality, 75, 60, 45, 30]:
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='JPEG', quality=attempt_quality, optimize=True)
                compressed_bytes = output_buffer.getvalue()
                compressed_size_kb = len(compressed_bytes) / 1024
                
                print(f"Quality {attempt_quality}: {compressed_size_kb:.1f}KB")
                
                if compressed_size_kb <= max_size_kb or attempt_quality == 30:
                    # Encode back to base64
                    compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
                    
                    print(f"Final compressed size: {compressed_size_kb:.1f}KB (reduction: {((original_size_kb - compressed_size_kb) / original_size_kb * 100):.1f}%)")
                    
                    return f"{header},{compressed_base64}"
            
            # Fallback - return original if compression fails
            return f"{header},{base64_data}"
            
        except Exception as e:
            print(f"Image compression error: {str(e)}")
            # Return original image if compression fails
            return f"data:image/jpeg;base64,{base64_data}" if "," not in base64_data else base64_data
    
    @staticmethod
    def compress_file_object(file_obj, max_size_kb: int = 500, quality: int = 85, max_width: int = 800) -> io.BytesIO:
        """
        Compress a file object (UploadFile)
        
        Args:
            file_obj: File object to compress
            max_size_kb: Maximum file size in KB
            quality: JPEG quality (1-100)
            max_width: Maximum width in pixels
        
        Returns:
            Compressed file as BytesIO object
        """
        try:
            # Read file content
            file_obj.seek(0)
            image_bytes = file_obj.read()
            original_size_kb = len(image_bytes) / 1024
            
            print(f"Original file size: {original_size_kb:.1f}KB")
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                print(f"Resized to: {image.width}x{image.height}")
            
            # Compress with different quality levels
            for attempt_quality in [quality, 75, 60, 45, 30]:
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='JPEG', quality=attempt_quality, optimize=True)
                compressed_size_kb = len(output_buffer.getvalue()) / 1024
                
                print(f"Quality {attempt_quality}: {compressed_size_kb:.1f}KB")
                
                if compressed_size_kb <= max_size_kb or attempt_quality == 30:
                    output_buffer.seek(0)
                    print(f"Final compressed size: {compressed_size_kb:.1f}KB")
                    return output_buffer
            
            # Fallback
            file_obj.seek(0)
            return file_obj
            
        except Exception as e:
            print(f"File compression error: {str(e)}")
            file_obj.seek(0)
            return file_obj

    @staticmethod
    def compress_pdf(file_obj, max_size_kb: int = 2000) -> io.BytesIO:
        """Compress PDF file"""
        try:
            file_obj.seek(0)
            pdf_bytes = file_obj.read()
            original_size_kb = len(pdf_bytes) / 1024
            
            print(f"Original PDF size: {original_size_kb:.1f}KB")
            
            if original_size_kb <= max_size_kb:
                file_obj.seek(0)
                return file_obj
            
            # Basic PDF compression by removing metadata and optimizing
            input_pdf = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            output_pdf = PyPDF2.PdfWriter()
            
            for page in input_pdf.pages:
                page.compress_content_streams()
                output_pdf.add_page(page)
            
            # Remove metadata
            output_pdf.add_metadata({})
            
            compressed_buffer = io.BytesIO()
            output_pdf.write(compressed_buffer)
            compressed_size_kb = len(compressed_buffer.getvalue()) / 1024
            
            print(f"Compressed PDF size: {compressed_size_kb:.1f}KB (reduction: {((original_size_kb - compressed_size_kb) / original_size_kb * 100):.1f}%)")
            
            compressed_buffer.seek(0)
            return compressed_buffer
            
        except Exception as e:
            print(f"PDF compression error: {str(e)}")
            file_obj.seek(0)
            return file_obj
    
    @staticmethod
    def compress_file_by_type(file_obj, filename: str, max_size_kb: int = 1000) -> io.BytesIO:
        """Compress file based on its type"""
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            return ImageCompressor.compress_file_object(file_obj, max_size_kb//2, 85, 800)
        elif file_ext == 'pdf':
            return ImageCompressor.compress_pdf(file_obj, max_size_kb*2)
        else:
            # For other file types, just return as-is
            print(f"No compression available for .{file_ext} files")
            return file_obj

# Create singleton instance
image_compressor = ImageCompressor()