from PIL import Image
import io
import base64
import zipfile
import gzip

class FileCompressor:
    @staticmethod
    def compress_image(base64_data: str, max_size_kb: int = 500) -> str:
        """Compress image files"""
        try:
            if "," in base64_data:
                header, base64_data = base64_data.split(",", 1)
            else:
                header = "data:image/jpeg;base64"
            
            image_bytes = base64.b64decode(base64_data)
            original_size_kb = len(image_bytes) / 1024
            print(f"Original image: {original_size_kb:.1f}KB")
            
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            if image.width > 800:
                ratio = 800 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((800, new_height), Image.Resampling.LANCZOS)
            
            for quality in [85, 75, 60, 45, 30]:
                output_buffer = io.BytesIO()
                image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
                compressed_bytes = output_buffer.getvalue()
                compressed_size_kb = len(compressed_bytes) / 1024
                
                if compressed_size_kb <= max_size_kb or quality == 30:
                    compressed_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
                    print(f"Compressed to: {compressed_size_kb:.1f}KB")
                    return f"{header},{compressed_base64}"
            
            return f"{header},{base64_data}"
        except Exception as e:
            print(f"Image compression error: {str(e)}")
            return f"data:image/jpeg;base64,{base64_data}" if "," not in base64_data else base64_data
    
    @staticmethod
    def compress_text_file(file_obj, filename: str) -> io.BytesIO:
        """Compress text files using gzip"""
        try:
            file_obj.seek(0)
            content = file_obj.read()
            original_size = len(content)
            
            compressed_buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as gz_file:
                if isinstance(content, str):
                    content = content.encode('utf-8')
                gz_file.write(content)
            
            compressed_size = len(compressed_buffer.getvalue())
            print(f"Text file compressed: {original_size} -> {compressed_size} bytes ({((original_size-compressed_size)/original_size*100):.1f}% reduction)")
            
            compressed_buffer.seek(0)
            return compressed_buffer
        except Exception as e:
            print(f"Text compression error: {str(e)}")
            file_obj.seek(0)
            return file_obj
    
    @staticmethod
    def compress_file_by_type(file_obj, filename: str) -> io.BytesIO:
        """Compress file based on extension"""
        ext = filename.lower().split('.')[-1]
        
        if ext in ['jpg', 'jpeg', 'png', 'gif']:
            # For images, convert to base64 first
            file_obj.seek(0)
            content = file_obj.read()
            b64_data = base64.b64encode(content).decode('utf-8')
            compressed_b64 = FileCompressor.compress_image(f"data:image/{ext};base64,{b64_data}")
            
            if "," in compressed_b64:
                compressed_content = base64.b64decode(compressed_b64.split(",", 1)[1])
            else:
                compressed_content = base64.b64decode(compressed_b64)
            
            return io.BytesIO(compressed_content)
            
        elif ext in ['txt', 'csv', 'json', 'xml', 'html', 'css', 'js']:
            return FileCompressor.compress_text_file(file_obj, filename)
            
        elif ext in ['pdf', 'doc', 'docx']:
            # For documents, use zip compression
            try:
                file_obj.seek(0)
                content = file_obj.read()
                original_size = len(content)
                
                compressed_buffer = io.BytesIO()
                with zipfile.ZipFile(compressed_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zip_file:
                    zip_file.writestr(filename, content)
                
                compressed_size = len(compressed_buffer.getvalue())
                print(f"Document compressed: {original_size} -> {compressed_size} bytes ({((original_size-compressed_size)/original_size*100):.1f}% reduction)")
                
                compressed_buffer.seek(0)
                return compressed_buffer
            except Exception as e:
                print(f"Document compression error: {str(e)}")
                file_obj.seek(0)
                return file_obj
        else:
            print(f"No compression for .{ext} files")
            return file_obj

# Create singleton
file_compressor = FileCompressor()