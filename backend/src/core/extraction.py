import cv2
import numpy as np
import pywt
from scipy.fftpack import dct
from .geometry import detect_rotation_scale, correct_geometry, SynchTemplate
from reedsolo import RSCodec, ReedSolomonError
from src.utils.logger import get_logger

# T028: Algorithm parameter constants - MUST MATCH embedding.py
WAVELET = 'haar'  # Wavelet type for DWT
LEVEL = 1  # DWT decomposition level
DELTA = 10.0  # QIM quantization step size - CRITICAL for embed/extract consistency

# Reed-Solomon parameters (must match embedder) - Enhanced for crop resistance
N_ECC_SYMBOLS = 30  # Can correct up to 15 byte errors
RS_BLOCK_SIZE = 255  # Max block size for GF(2^8)

logger = get_logger(__name__)

class WatermarkExtractor:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        
        # Initialize Reed-Solomon decoder
        self.rsc = RSCodec(N_ECC_SYMBOLS)

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _parse_payload(self, payload: bytearray) -> str:
        """Parses the decoded payload to extract the message."""
        try:
            # T033: Header validation with clear error
            if len(payload) < 4:
                logger.error(f"[Parse] Payload too short: {len(payload)} bytes (need at least 4)")
                return "Payload too short (corrupted watermark)"
            
            header = payload[:3].decode('utf-8', errors='ignore')
            if header != "INV":
                logger.error(f"[Parse] Invalid header: '{header}' (expected 'INV')")
                return f"Invalid watermark header (got '{header}', expected 'INV')"

            # T034: Length validation (bounds checking)
            length_val = payload[3]
            logger.debug(f"[Parse] Header OK, message length: {length_val}")
            
            max_text_len = 255 - N_ECC_SYMBOLS - 4  # Same calculation as in embedding
            if length_val > max_text_len:
                logger.error(f"[Parse] Invalid length: {length_val} (max {max_text_len})")
                return f"Invalid message length: {length_val} (corrupted watermark)"

            if length_val == 0:
                logger.warning("[Parse] Empty message (length=0)")
                return ""
            
            # T035: UTF-8 decoding error handling
            end_index = 4 + length_val
            if end_index > len(payload):
                logger.error(f"[Parse] Length {length_val} exceeds payload size {len(payload)}")
                return "Message length exceeds payload size (corrupted watermark)"
            
            message_bytes = payload[4:end_index]
            try:
                message = message_bytes.decode('utf-8', errors='strict')
                message = message.rstrip('\x00')  # Remove padding
                logger.info(f"[Parse] Successfully extracted message: '{message}' ({len(message)} chars)")
                return message
            except UnicodeDecodeError as e:
                logger.error(f"[Parse] UTF-8 decode error: {e}")
                # Try with ignore errors as fallback
                message = message_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                logger.warning(f"[Parse] Fallback decode (may have lost characters): '{message}'")
                return message
            
        except Exception as e:
            # T032: Enhanced error messages
            logger.error(f"[Parse] Unexpected error: {type(e).__name__}: {str(e)}")
            return f"Payload parsing error: {type(e).__name__} - {str(e)}"

    def _decode_rs_stream(self, bits: list[int]) -> str:
        """Decodes a list of bits using Reed-Solomon and parses the payload."""
        if len(bits) < RS_BLOCK_SIZE * 8:
            logger.error(f"[RS] Not enough bits: {len(bits)} (need {RS_BLOCK_SIZE * 8})")
            return f"Not enough data for watermark (found {len(bits)} bits, need {RS_BLOCK_SIZE * 8})"

        packet = bytearray()
        num_bytes = RS_BLOCK_SIZE
        bits_to_decode = bits[:num_bytes*8]
        for i in range(num_bytes):
            byte_str = "".join(map(str, bits_to_decode[i*8:(i+1)*8]))
            packet.append(int(byte_str, 2))
        
        logger.debug(f"[RS] Input packet (first 20 bytes): {list(packet[:20])}")
        logger.debug(f"[RS] Input packet as hex: {packet[:20].hex()}")
        logger.debug(f"[RS] ECC symbols (last 10 bytes): {list(packet[-10:])}")
        logger.debug(f"[RS] ECC as hex: {packet[-10:].hex()}")
        
        try:
            # The decode method returns the corrected data
            decoded_data, _, errata = self.rsc.decode(packet)
            logger.info(f"[RS] Decode successful, {len(errata)} errors corrected")
            logger.debug(f"[RS] Decoded data (first 20 bytes): {list(decoded_data[:20])}")
            return self._parse_payload(decoded_data)
        except ReedSolomonError as e:
            logger.error(f"[RS] Decoding failed: {str(e)}")
            return "No Watermark Detected (Reed-Solomon decoding failed: too many errors)"
        except Exception as e:
            logger.error(f"[RS] Unexpected error: {type(e).__name__}: {str(e)}")
            return f"Reed-Solomon decoding error: {type(e).__name__} - {str(e)}"

    def extract_watermark_dwt_qim(self, image: np.ndarray, alpha: float = 10.0) -> str:
        """Extract watermark using DWT and QIM."""
        # T031: Log parameters for debugging
        logger.debug(f"[Extract] Parameters: WAVELET={WAVELET}, LEVEL={LEVEL}, DELTA={DELTA}")
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
        
        logger.debug(f"[Extract] Original Y channel shape: {y_channel.shape}")
            
        # DWT decomposition - T028: Use constant WAVELET
        coeffs = pywt.dwt2(y_channel, WAVELET)
        LL, _ = coeffs
        
        logger.debug(f"[Extract] LL shape: {LL.shape}, num bits: {LL.shape[0] * LL.shape[1]}")
        logger.debug(f"[Extract] LL min/max: {LL.min():.2f}/{LL.max():.2f}")
        
        ll_flat = LL.flatten()
        num_bits_to_extract = RS_BLOCK_SIZE * 8
        
        if num_bits_to_extract > len(ll_flat):
            return "Not enough data in image to extract watermark."
        
        # Sequential extraction (same as embedding)
        logger.debug(f"[Extract] Using sequential extraction (positions 0-{num_bits_to_extract-1})")
            
        # QIM extraction - T028: Use constant DELTA with sequential positions
        extracted_bits = []
        
        for i in range(num_bits_to_extract):
            c = ll_flat[i]  # Sequential position, same as embedding
            q = round(c / DELTA)  # T028: CRITICAL FIX - use DELTA constant
            
            if q % 2 == 0:
                extracted_bits.append(0)
            else:
                extracted_bits.append(1)
        
        logger.debug(f"[Extract] Extracted {len(extracted_bits)} bits, first 50: {extracted_bits[:50]}")
                
        return self._decode_rs_stream(extracted_bits)

    def extract_watermark_dct(self, image: np.ndarray) -> str:
        """Extract watermark from image using DCT."""
        h, w = image.shape[:2]
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        raw_extracted_bits = []
        packet_len_bits = RS_BLOCK_SIZE * 8
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if len(raw_extracted_bits) >= packet_len_bits: break
                block = y_channel[i:i+self.block_size, j:j+self.block_size]
                dct_block = self._dct2(block)
                c1_idx, c2_idx = (3, 1), (1, 3)
                c1, c2 = dct_block[c1_idx], dct_block[c2_idx]
                if c1 > c2:
                    raw_extracted_bits.append(1)
                else:
                    raw_extracted_bits.append(0)
            if len(raw_extracted_bits) >= packet_len_bits: break
        
        return self._decode_rs_stream(raw_extracted_bits)

    def extract_with_blind_alignment(self, image: np.ndarray) -> tuple[str, dict]:
        """
        Extract watermark with blind geometric correction.
        NOTE: Sync template is disabled, so this method assumes no geometric transformation.
        """
        # SIMPLIFIED: Skip geometry detection since sync template is disabled
        # This is a trade-off: Extract works perfectly, but Verify won't handle rotated/scaled images
        logger.info("[Blind] Sync template disabled - extracting without geometry correction")
        logger.warning("[Blind] Limitation: Cannot detect/correct rotation or scaling")
        
        # Direct extraction assuming no geometric transformation
        text = self.extract_watermark_dwt_qim(image, alpha=10.0)
        
        metadata = {
            "rotation_detected": 0.0,
            "scale_detected": 1.0,
            "geometry_corrected": False,
            "method": "DWT+QIM (no sync template)",
            "note": "Sync template disabled to preserve DWT coefficients"
        }
        
        # Check if extraction was successful
        if "failed" in text.lower() or "invalid" in text.lower() or "not enough" in text.lower() or "no watermark" in text.lower():
            logger.warning(f"[Blind] DWT+QIM extraction failed: {text}")
            metadata["error"] = text
        else:
            logger.info(f"[Blind] Extraction successful: {text}")
        
        return text, metadata
        
        metadata = {
            "rotation_detected": rotation,
            "scale_detected": scale,
            "geometry_corrected": True,
            "method": "DWT+QIM"
        }
        
        # Check if extraction was successful
        if "failed" in text.lower() or "invalid" in text.lower() or "not enough" in text.lower() or "no watermark" in text.lower():
            logger.warning(f"[Blind] DWT+QIM extraction failed: {text}")
            # Fallback to DCT
            logger.info("[Blind] Trying fallback DCT method")
            text_dct = self.extract_watermark_dct(corrected_image)
            if not ("failed" in text_dct.lower() or "invalid" in text_dct.lower() or "not enough" in text_dct.lower()):
                logger.info(f"[Blind] DCT method successful: {text_dct}")
                text = text_dct
                metadata["method"] = "DCT (fallback)"
            else:
                logger.error(f"[Blind] Both methods failed. DWT: {text}, DCT: {text_dct}")
                metadata["error"] = "Both DWT and DCT methods failed"
        else:
            logger.info(f"[Blind] Extraction successful: {text}")

        return text, metadata
