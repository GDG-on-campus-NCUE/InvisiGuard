import cv2
import numpy as np
from fastapi import UploadFile
import io

class ImageProcessor:
    @staticmethod
    async def load_image(file: UploadFile) -> np.ndarray:
        """Load image from UploadFile to numpy array (BGR)."""
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Could not decode image")
        return img

    @staticmethod
    def resize_image(image: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
        """Resize image maintaining aspect ratio if only one dim provided."""
        if width is None and height is None:
            return image
        
        h, w = image.shape[:2]
        
        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        elif height is None:
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            dim = (width, height)
            
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    @staticmethod
    def save_image(image: np.ndarray, path: str) -> str:
        """Save numpy array to file."""
        cv2.imwrite(path, image)
        return path

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """Convert BGR to Grayscale."""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
