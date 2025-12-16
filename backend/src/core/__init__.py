"""
Core watermarking algorithms package

T029: Parameter validation check on module import
Ensures embedding and extraction use consistent parameters
"""

def validate_algorithm_parameters():
    """Validate that embedding and extraction parameters match"""
    from .embedding import WAVELET as EMBED_WAVELET, DELTA as EMBED_DELTA, N_ECC_SYMBOLS as EMBED_ECC
    from .extraction import WAVELET as EXTRACT_WAVELET, DELTA as EXTRACT_DELTA, N_ECC_SYMBOLS as EXTRACT_ECC
    
    errors = []
    
    if EMBED_WAVELET != EXTRACT_WAVELET:
        errors.append(f"WAVELET mismatch: embed={EMBED_WAVELET}, extract={EXTRACT_WAVELET}")
    
    if EMBED_DELTA != EXTRACT_DELTA:
        errors.append(f"DELTA mismatch: embed={EMBED_DELTA}, extract={EXTRACT_DELTA}")
    
    if EMBED_ECC != EXTRACT_ECC:
        errors.append(f"N_ECC_SYMBOLS mismatch: embed={EMBED_ECC}, extract={EXTRACT_ECC}")
    
    if errors:
        error_msg = "Algorithm parameter mismatch detected:\n" + "\n".join(errors)
        raise ValueError(error_msg)
    
    print(f"✓ Algorithm parameters validated: WAVELET={EMBED_WAVELET}, DELTA={EMBED_DELTA}, ECC={EMBED_ECC}")

# Run validation on import
validate_algorithm_parameters()
