import cv2
import numpy as np
from scipy.fftpack import dct
from .geometry import detect_rotation_scale, correct_geometry, SynchTemplate

class WatermarkExtractor:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def bits_to_text(self, bits: list[int]) -> str:
        """Convert list of bits to string with Header validation."""
        # Need at least 24 bits for header + 8 bits for length = 32 bits
        if len(bits) < 32:
            return "No Watermark Detected"
            
        # Extract Header (first 24 bits / 3 bytes)
        header_bits = bits[:24]
        header_chars = []
        for i in range(0, 24, 8):
            byte = header_bits[i:i+8]
            char_code = int(''.join(map(str, byte)), 2)
            header_chars.append(chr(char_code))
        
        header_str = "".join(header_chars)
        
        if header_str != "INV":
            return "No Watermark Detected"
            
        # Extract Length (next 8 bits)
        length_bits = bits[24:32]
        length_val = int(''.join(map(str, length_bits)), 2)
        
        if length_val == 0:
            return ""
            
        # Extract Data
        # Start at index 32
        # Read length_val bytes
        data_bits = bits[32:]
        chars = []
        
        for i in range(0, len(data_bits), 8):
            if len(chars) >= length_val:
                break
                
            byte = data_bits[i:i+8]
            if len(byte) < 8:
                break
                
            char_code = int(''.join(map(str, byte)), 2)
            chars.append(chr(char_code))
            
        return "".join(chars)

    def extract_watermark_dct(self, image: np.ndarray) -> str:
        """
        Extract watermark from image using DCT.
        """
        h, w = image.shape[:2]
        
        # Convert to YUV color space
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        bits = []
        
        # Iterate over blocks
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                # Get block
                block = y_channel[i:i+self.block_size, j:j+self.block_size]
                
                # DCT
                dct_block = self._dct2(block)
                
                # Read coefficients
                c1_idx = (4, 3)
                c2_idx = (3, 4)
                
                c1 = dct_block[c1_idx]
                c2 = dct_block[c2_idx]
                
                if c1 > c2:
                    bits.append(1)
                else:
                    bits.append(0)
        
        return self.bits_to_text(bits)

    def extract_with_blind_alignment(self, image: np.ndarray) -> tuple[str, dict]:
        """
        Extract watermark with blind geometric correction.
        Returns (text, metadata).
        """
        template = SynchTemplate()
        rotation, scale = detect_rotation_scale(image, template)
        
        corrected_image = correct_geometry(image, rotation, scale)
        
        text = self.extract_watermark_dct(corrected_image)
        
        metadata = {
            "rotation_detected": rotation,
            "scale_detected": scale,
            "geometry_corrected": True
        }
        
        return text, metadata
