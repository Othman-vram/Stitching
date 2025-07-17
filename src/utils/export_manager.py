"""
Export manager for saving composite images and metadata
"""

import os
import json
import numpy as np
from typing import List, Optional
import cv2
import tifffile
from PIL import Image
import logging

from ..core.fragment import Fragment

class ExportManager:
    """Handles exporting composite images and metadata"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def export_composite_image(self, fragments: List[Fragment], output_path: str,
                             format: str = 'tiff', quality: int = 95,
                             resolution_dpi: int = 300):
        """
        Export composite image of all visible fragments
        
        Args:
            fragments: List of Fragment objects
            output_path: Output file path
            format: Output format ('tiff', 'png', 'jpg')
            quality: JPEG quality (1-100)
            resolution_dpi: Resolution in DPI
        """
        try:
            self.logger.info(f"Exporting composite image to {output_path}")
            
            # Get visible fragments
            visible_fragments = [f for f in fragments if f.visible and f.image_data is not None]
            if not visible_fragments:
                raise ValueError("No visible fragments to export")
                
            # Calculate composite bounds
            bounds = self.calculate_composite_bounds(visible_fragments)
            if not bounds:
                raise ValueError("Could not calculate composite bounds")
                
            min_x, min_y, max_x, max_y = bounds
            width = int(max_x - min_x)
            height = int(max_y - min_y)
            
            self.logger.info(f"Composite size: {width} x {height}")
            
            # Create composite image
            composite = self.render_composite(visible_fragments, bounds)
            
            # Save based on format
            format_lower = format.lower()
            if format_lower == 'tiff':
                self.save_tiff(composite, output_path, resolution_dpi)
            elif format_lower == 'png':
                self.save_png(composite, output_path)
            elif format_lower in ['jpg', 'jpeg']:
                self.save_jpeg(composite, output_path, quality)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
            self.logger.info("Composite image exported successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to export composite image: {str(e)}")
            raise
            
    def calculate_composite_bounds(self, fragments: List[Fragment]) -> Optional[tuple]:
        """Calculate bounding box of all fragments"""
        if not fragments:
            return None
            
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for fragment in fragments:
            bbox = fragment.get_bounding_box()
            min_x = min(min_x, bbox[0])
            min_y = min(min_y, bbox[1])
            max_x = max(max_x, bbox[0] + bbox[2])
            max_y = max(max_y, bbox[1] + bbox[3])
            
        return (min_x, min_y, max_x, max_y)
        
    def render_composite(self, fragments: List[Fragment], bounds: tuple) -> np.ndarray:
        """Render all fragments into a composite image"""
        min_x, min_y, max_x, max_y = bounds
        width = int(max_x - min_x)
        height = int(max_y - min_y)
        
        # Create composite array with alpha channel
        composite = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Render each fragment
        for fragment in fragments:
            self.render_fragment_to_composite(fragment, composite, min_x, min_y)
            
        return composite
        
    def render_fragment_to_composite(self, fragment: Fragment, composite: np.ndarray,
                                   offset_x: float, offset_y: float):
        """Render a single fragment to the composite image"""
        transformed_image = fragment.get_transformed_image()
        if transformed_image is None:
            return
            
        # Calculate position in composite
        frag_x = int(fragment.x - offset_x)
        frag_y = int(fragment.y - offset_y)
        
        # Get dimensions
        frag_h, frag_w = transformed_image.shape[:2]
        comp_h, comp_w = composite.shape[:2]
        
        # Calculate intersection
        src_x1 = max(0, -frag_x)
        src_y1 = max(0, -frag_y)
        src_x2 = min(frag_w, comp_w - frag_x)
        src_y2 = min(frag_h, comp_h - frag_y)
        
        dst_x1 = max(0, frag_x)
        dst_y1 = max(0, frag_y)
        dst_x2 = dst_x1 + (src_x2 - src_x1)
        dst_y2 = dst_y1 + (src_y2 - src_y1)
        
        # Check overlap
        if src_x2 <= src_x1 or src_y2 <= src_y1:
            return
            
        # Extract region
        fragment_region = transformed_image[src_y1:src_y2, src_x1:src_x2]
        
        # Alpha blending with proper transparency support
        if fragment_region.shape[2] == 4:  # RGBA
            # Extract alpha channel from fragment
            frag_alpha = fragment_region[:, :, 3:4] / 255.0 * fragment.opacity
            frag_rgb = fragment_region[:, :, :3]
            
            # Get existing composite region
            comp_region = composite[dst_y1:dst_y2, dst_x1:dst_x2]
            comp_alpha = comp_region[:, :, 3:4] / 255.0
            comp_rgb = comp_region[:, :, :3]
            
            # Alpha blending
            out_alpha = frag_alpha + (1 - frag_alpha) * comp_alpha
            
            # Avoid division by zero
            mask = out_alpha[:, :, 0] > 0
            out_rgb = np.zeros_like(frag_rgb, dtype=np.float32)
            out_rgb[mask, :] = (frag_alpha[mask, :] * frag_rgb[mask, :] + 
                               (1 - frag_alpha[mask, :]) * comp_rgb[mask, :])
            
            # Update composite
            composite[dst_y1:dst_y2, dst_x1:dst_x2, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
            composite[dst_y1:dst_y2, dst_x1:dst_x2, 3:4] = np.clip(out_alpha * 255, 0, 255).astype(np.uint8)
        else:
            # Fallback for RGB images
            alpha = fragment.opacity
            composite[dst_y1:dst_y2, dst_x1:dst_x2, :3] = (
                alpha * fragment_region + 
                (1 - alpha) * composite[dst_y1:dst_y2, dst_x1:dst_x2, :3]
            ).astype(np.uint8)
            composite[dst_y1:dst_y2, dst_x1:dst_x2, 3] = 255
            
    def save_tiff(self, image: np.ndarray, output_path: str, resolution_dpi: int):
        """Save image as TIFF"""
        # Calculate resolution in pixels per centimeter
        resolution_ppcm = resolution_dpi / 2.54
        
        # Handle RGBA images
        if image.shape[2] == 4:
            # TIFF supports RGBA
            photometric = 'rgb'  # RGBA is handled automatically
        else:
            photometric = 'rgb'
        
        tifffile.imwrite(
            output_path,
            image,
            resolution=(resolution_ppcm, resolution_ppcm),
            metadata={'unit': 'CENTIMETER'},
            photometric=photometric
        )
        
    def save_png(self, image: np.ndarray, output_path: str):
        """Save image as PNG"""
        pil_image = Image.fromarray(image)
        # PNG supports RGBA natively
        pil_image.save(output_path, 'PNG', optimize=True)
        
    def save_jpeg(self, image: np.ndarray, output_path: str, quality: int):
        """Save image as JPEG"""
        # JPEG doesn't support alpha channel, should be RGB only
        pil_image = Image.fromarray(image)
        pil_image.save(output_path, 'JPEG', quality=quality, optimize=True)
        
    def export_metadata(self, fragments: List[Fragment], output_path: str):
        """Export fragment metadata as JSON"""
        try:
            self.logger.info(f"Exporting metadata to {output_path}")
            
            metadata = {
                'version': '1.0',
                'export_timestamp': self.get_timestamp(),
                'fragments': []
            }
            
            for fragment in fragments:
                fragment_data = {
                    'id': fragment.id,
                    'name': fragment.name,
                    'file_path': fragment.file_path,
                    'original_size': fragment.original_size,
                    'pixel_size': fragment.pixel_size,
                    'transform': {
                        'x': fragment.x,
                        'y': fragment.y,
                        'rotation': fragment.rotation,
                        'flip_horizontal': fragment.flip_horizontal,
                        'flip_vertical': fragment.flip_vertical
                    },
                    'display': {
                        'visible': fragment.visible,
                        'opacity': fragment.opacity
                    }
                }
                metadata['fragments'].append(fragment_data)
                
            # Save metadata
            with open(output_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            self.logger.info("Metadata exported successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to export metadata: {str(e)}")
            raise
            
    def get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def export_fragment_masks(self, fragments: List[Fragment], output_dir: str):
        """Export individual fragment masks"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for fragment in fragments:
                if not fragment.visible or fragment.image_data is None:
                    continue
                    
                # Create mask from fragment
                transformed_image = fragment.get_transformed_image()
                if transformed_image is None:
                    continue
                    
                # Create binary mask (non-zero pixels)
                if len(transformed_image.shape) == 3:
                    mask = np.any(transformed_image > 0, axis=2).astype(np.uint8) * 255
                else:
                    mask = (transformed_image > 0).astype(np.uint8) * 255
                    
                # Save mask
                mask_filename = f"{fragment.name or fragment.id}_mask.png"
                mask_path = os.path.join(output_dir, mask_filename)
                cv2.imwrite(mask_path, mask)
                
            self.logger.info(f"Fragment masks exported to {output_dir}")
            
        except Exception as e:
            self.logger.error(f"Failed to export fragment masks: {str(e)}")
            raise
            
    def alpha_to_rgb(self, rgba_image: np.ndarray, background_color=(255, 255, 255)) -> np.ndarray:
        """Convert RGBA image to RGB with specified background color"""
        if rgba_image.shape[2] != 4:
            return rgba_image
            
        rgb = rgba_image[:, :, :3]
        alpha = rgba_image[:, :, 3:4] / 255.0
        
        # Create background
        background = np.full_like(rgb, background_color, dtype=np.uint8)
        
        # Alpha blend with background
        result = (alpha * rgb + (1 - alpha) * background).astype(np.uint8)
        
        return result