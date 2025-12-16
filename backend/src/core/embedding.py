import cv2
import numpy as np
import pywt
from scipy.fftpack import dct, idct
from .geometry import embed_synch_template, SynchTemplate
from reedsolo import RSCodec
from src.utils.logger import get_logger

# T027: Algorithm parameter constants - MUST MATCH extraction.py
WAVELET = 'haar'  # Wavelet type for DWT
LEVEL = 1  # DWT decomposition level
DELTA = 10.0  # QIM quantization step size - CRITICAL for embed/extract consistency

# Reed-Solomon parameters - Enhanced for crop resistance
N_ECC_SYMBOLS = 30  # Number of ECC symbols (can correct N_ECC_SYMBOLS / 2 = 15 errors)
# Trade-off: More ECC = Better error correction, but less message capacity

logger = get_logger(__name__)


class WatermarkEmbedder:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        
        # Initialize Reed-Solomon encoder
        self.rsc = RSCodec(N_ECC_SYMBOLS)

    def generate_log_mask(self, image_gray: np.ndarray, base_alpha: float = 1.0) -> np.ndarray:
        # (Original method unchanged)
        blurred = cv2.GaussianBlur(image_gray, (3, 3), 0)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        laplacian = np.abs(laplacian)
        mask = cv2.normalize(laplacian, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        k = 2.0
        alpha_map = base_alpha * (1 + k * mask)
        return alpha_map

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _idct2(self, block):
        return idct(idct(block.T, norm='ortho').T, norm='ortho')

    def text_to_bits(self, text: str) -> list[int]:
        """Convert string to list of bits with Header, Length, and Reed-Solomon error correction."""
        header = "INV"
        length = len(text)
        
        max_data_len = 255 - N_ECC_SYMBOLS
        # We need 4 bytes for the header ("INV") and the length field.
        max_text_len = max_data_len - 4
        if length > max_text_len:
            raise ValueError(f"Text too long (max {max_text_len} chars for current Reed-Solomon config)")
            
        payload_str = header + chr(length) + text
        data = bytearray(payload_str, 'utf-8')
        
        # Pad data to a fixed size for a constant-size RS block
        padded_data = data + b'\0' * (max_data_len - len(data))

        # The encode method appends the ECC symbols to the data
        packet = self.rsc.encode(padded_data) # packet is now always 255 bytes
        
        logger.debug(f"[Embed] Original text: '{text}', length: {length}")
        logger.debug(f"[Embed] Payload (first 20 bytes): {list(packet[:20])}")
        logger.debug(f"[Embed] Payload as hex: {packet[:20].hex()}")
        logger.debug(f"[Embed] ECC symbols (last 10 bytes): {list(packet[-10:])}")
        logger.debug(f"[Embed] ECC as hex: {packet[-10:].hex()}")
        
        encoded_bits = []
        for byte in packet:
            binval = bin(byte)[2:].rjust(8, '0')
            encoded_bits.extend([int(b) for b in binval])
        return encoded_bits

    def embed_watermark_dwt_qim(self, image: np.ndarray, text: str, alpha: float = 10.0) -> np.ndarray:
        """Embed watermark using DWT and QIM."""
        # T030: Log parameters for debugging
        logger.debug(f"[Embed] Parameters: WAVELET={WAVELET}, LEVEL={LEVEL}, DELTA={DELTA}, alpha={alpha}")
        
        # Store original shape for reconstruction
        original_shape = image.shape
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
        
        # Store original Y channel shape
        original_y_shape = y_channel.shape
        logger.debug(f"[Embed] Original Y channel shape: {original_y_shape}")
        
        bits = self.text_to_bits(text)
        
        # DWT decomposition - T027: Use constant WAVELET
        coeffs = pywt.dwt2(y_channel, WAVELET)
        LL, (LH, HL, HH) = coeffs
        
        logger.debug(f"[Embed] LL shape: {LL.shape}, total capacity: {LL.shape[0] * LL.shape[1]} bits")
        logger.debug(f"[Embed] LL min/max BEFORE QIM: {LL.min():.2f}/{LL.max():.2f}")
        logger.debug(f"[Embed] Embedding {len(bits)} bits, first 50: {bits[:50]}")
        
        ll_flat = LL.flatten()
        
        if len(bits) > len(ll_flat):
            raise ValueError("Not enough space in the image to embed the watermark.")
        
        # Sequential embedding (concentrated in upper region for crop resistance)
        # Trade-off: Watermark in one area, but survives edge cropping + strong ECC
        logger.debug(f"[Embed] Using sequential embedding (positions 0-{len(bits)-1})")
            
        # QIM embedding - T027: Use constant DELTA with sequential positions
        for i in range(len(bits)):
            c = ll_flat[i]  # Sequential position
            b = bits[i]
            
            q = round(c / DELTA)
            
            if b == 0 and q % 2 != 0: # If bit is 0, quantizer must be even
                q -= 1
            elif b == 1 and q % 2 == 0: # If bit is 1, quantizer must be odd
                q += 1
            
            ll_flat[i] = q * DELTA
            
        LL_w = ll_flat.reshape(LL.shape)
        
        logger.debug(f"[Embed] LL_w min/max AFTER QIM: {LL_w.min():.2f}/{LL_w.max():.2f}")
        
        # Inverse DWT - T027: Use constant WAVELET
        coeffs_w = (LL_w, (LH, HL, HH))
        y_channel_w = pywt.idwt2(coeffs_w, WAVELET)
        
        # CRITICAL FIX: Ensure reconstructed channel matches original size
        if y_channel_w.shape != original_y_shape:
            logger.warning(f"[Embed] IDWT size mismatch! Got {y_channel_w.shape}, expected {original_y_shape}")
            # Crop or pad to match original size
            y_channel_w = y_channel_w[:original_y_shape[0], :original_y_shape[1]]
        
        logger.debug(f"[Embed] After IDWT shape: {y_channel_w.shape}")
        
        # Merge channels back
        processed_y = np.clip(y_channel_w, 0, 255).astype(np.uint8)
        
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            watermarked = processed_y
        
        # NOTE: Sync template is disabled because it interferes with DWT coefficients
        # Current limitation: Verify (blind extraction) won't work with geometric transformations
        # template = SynchTemplate()
        # watermarked = embed_synch_template(watermarked, template)
        logger.debug("[Embed] Sync template disabled - Verify will assume no geometric transformation")
        
        logger.info(f"[Embed] Successfully embedded {len(bits)} bits into image")
            
        return watermarked

    def embed_watermark_dct(self, image: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
        """Original DCT-based embedding method."""
        h, w = image.shape[:2]
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        mask = self.generate_log_mask(y_channel, base_alpha=alpha)
        bits = self.text_to_bits(text)
        num_bits = len(bits)
        bit_idx = 0
        processed_y = y_channel.copy()
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if bit_idx >= num_bits: break
                block = processed_y[i:i+self.block_size, j:j+self.block_size]
                dct_block = self._dct2(block)
                local_alpha = mask[i + self.block_size//2, j + self.block_size//2]
                c1_idx, c2_idx = (3, 1), (1, 3)
                c1, c2 = dct_block[c1_idx], dct_block[c2_idx]
                base_strength = 2.0
                gap = (base_strength * alpha) + (local_alpha * 5.0 * alpha)
                bit = bits[bit_idx]
                if bit == 1:
                    if c1 <= c2 + gap:
                        diff = (c2 + gap - c1) / 2.0
                        dct_block[c1_idx] += diff
                        dct_block[c2_idx] -= diff
                else:
                    if c2 <= c1 + gap:
                        diff = (c1 + gap - c2) / 2.0
                        dct_block[c2_idx] += diff
                        dct_block[c1_idx] -= diff
                processed_y[i:i+self.block_size, j:j+self.block_size] = self._idct2(dct_block)
                bit_idx += 1
            if bit_idx >= num_bits: break

        processed_y = np.clip(processed_y, 0, 255).astype(np.uint8)
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            watermarked = processed_y
            
        template = SynchTemplate()
        watermarked = embed_synch_template(watermarked, template)
        return watermarked
