import pytest
from src.core.embedding import WatermarkEmbedder
from src.core.extraction import WatermarkExtractor

class TestPayload:
    def test_text_to_bits_structure(self):
        embedder = WatermarkEmbedder()
        text = "A"
        # Header: [INV] -> 3 bytes
        # Length: 1 byte (value 1)
        # Data: "A" -> 1 byte
        # Total: 5 bytes = 40 bits
        
        bits = embedder.text_to_bits(text)
        
        assert len(bits) == 40
        
        # Check Header [INV]
        # 'I' = 73 = 01001001
        # 'N' = 78 = 01001110
        # 'V' = 86 = 01010110
        # Wait, spec says [INV] is 01011011 01001001 01001110 01010110 01011101?
        # Let's check ASCII.
        # [ = 91 = 01011011
        # I = 73 = 01001001
        # N = 78 = 01001110
        # V = 86 = 01010110
        # ] = 93 = 01011101
        # The spec example says Header is "[INV]" (5 chars) but the table says "24 bits" (3 bytes) and lists "[INV]" as the string.
        # The table description says: "ASCII string `[INV]` ... Used to detect presence of watermark."
        # But the example breakdown shows:
        # Header: `[INV]` -> `01011011 01001001 01001110 01010110 01011101` (5 bytes)
        # But the table says "Size: 24 bits". 24 bits is 3 bytes.
        # "[INV]" is 5 characters. "INV" is 3 characters.
        # I should clarify or stick to one.
        # The spec says: "Decision: Use `[INV]` (3 bytes) as the header." in Research.md.
        # But in Data Model it says "Header | 24 bits | Fixed | ASCII string `[INV]`".
        # And the example shows 5 bytes.
        # I will assume the intention is a robust header. 5 bytes "[INV]" is better than 3 bytes "INV" for uniqueness, but 3 bytes "INV" fits the "24 bits" description.
        # However, the example explicitly lists the binary for `[`, `I`, `N`, `V`, `]`.
        # And the total bits calculation in Data Model says: "24 + 8 + 32 = 64 bits".
        # 24 bits = 3 bytes.
        # If text is "Test" (4 bytes = 32 bits).
        # If header is 5 bytes, it would be 40 bits.
        # So there is a contradiction in the spec.
        # "Decision: Use `[INV]` (3 bytes) as the header." -> This implies the string is "INV".
        # But the example shows brackets.
        # I will stick to "INV" (3 bytes) as it matches the "24 bits" constraint which is explicitly stated multiple times.
        # Wait, "Decision: Use `[INV]` (3 bytes)" might mean the string is literally `[INV]` but the author thought it was 3 bytes? No, `[` is a byte.
        # I'll use "INV" (3 bytes) to match the 24-bit size constraint.
        
        # Re-reading Research.md: "Decision: Use `[INV]` (3 bytes) as the header."
        # This is likely a typo in the spec writer's mind (me).
        # I will use "INV" as the header.
        
        # Header: "INV"
        # I = 01001001
        # N = 01001110
        # V = 01010110
        
        expected_header = [
            0,1,0,0,1,0,0,1, # I
            0,1,0,0,1,1,1,0, # N
            0,1,0,1,0,1,1,0  # V
        ]
        
        assert bits[:24] == expected_header
        
        # Length: 1 -> 00000001
        expected_length = [0,0,0,0,0,0,0,1]
        assert bits[24:32] == expected_length
        
        # Data: "A" -> 01000001
        expected_data = [0,1,0,0,0,0,0,1]
        assert bits[32:] == expected_data

    def test_bits_to_text_valid(self):
        extractor = WatermarkExtractor()
        # Construct valid bits for "Hi"
        # Header "INV"
        bits = [
            0,1,0,0,1,0,0,1, # I
            0,1,0,0,1,1,1,0, # N
            0,1,0,1,0,1,1,0, # V
            0,0,0,0,0,0,1,0, # Length 2
            0,1,0,0,1,0,0,0, # H
            0,1,1,0,1,0,0,1  # i
        ]
        
        text = extractor.bits_to_text(bits)
        assert text == "Hi"

    def test_bits_to_text_invalid_header(self):
        extractor = WatermarkExtractor()
        # Invalid header "XXX"
        bits = [
            0,1,0,1,1,0,0,0, # X
            0,1,0,1,1,0,0,0, # X
            0,1,0,1,1,0,0,0, # X
            0,0,0,0,0,0,0,1, # Length 1
            0,1,0,0,0,0,0,1  # A
        ]
        
        text = extractor.bits_to_text(bits)
        assert text == "No Watermark Detected"

    def test_bits_to_text_garbage(self):
        extractor = WatermarkExtractor()
        # Random bits
        bits = [1, 0] * 50
        text = extractor.bits_to_text(bits)
        assert text == "No Watermark Detected"
