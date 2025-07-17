"""
Rigid stitching algorithm for tissue fragment alignment
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from scipy.optimize import minimize
from skimage import feature, measure
from skimage.transform import AffineTransform
import logging

from ..core.fragment import Fragment

class RigidStitchingAlgorithm:
    """
    Rigid stitching algorithm that refines fragment positions using feature matching
    and optimization. Uses manual positions as initial guesses.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Feature detection parameters
        self.feature_detector = cv2.SIFT_create(nfeatures=1000)
        self.matcher = cv2.BFMatcher()
        
        # Matching parameters
        self.match_ratio_threshold = 0.7
        self.min_matches = 10
        self.ransac_threshold = 5.0
        
        # Optimization parameters
        self.max_iterations = 1000
        self.convergence_threshold = 1e-6
        
    def stitch_fragments(self, fragments: List[Fragment], 
                        initial_transforms: Dict[str, dict]) -> Dict[str, dict]:
        """
        Perform rigid stitching refinement on fragments
        
        Args:
            fragments: List of Fragment objects
            initial_transforms: Dictionary of initial transform parameters
            
        Returns:
            Dictionary of refined transform parameters
        """
        if len(fragments) < 2:
            self.logger.warning("Need at least 2 fragments for stitching")
            return initial_transforms
            
        self.logger.info(f"Starting rigid stitching with {len(fragments)} fragments")
        
        try:
            # Extract features from all fragments
            fragment_features = self.extract_all_features(fragments)
            
            # Find pairwise matches
            pairwise_matches = self.find_pairwise_matches(fragments, fragment_features)
            
            if not pairwise_matches:
                self.logger.warning("No feature matches found between fragments")
                return initial_transforms
                
            # Optimize transforms using matches
            refined_transforms = self.optimize_transforms(
                fragments, pairwise_matches, initial_transforms
            )
            
            self.logger.info("Rigid stitching completed successfully")
            return refined_transforms
            
        except Exception as e:
            self.logger.error(f"Rigid stitching failed: {str(e)}")
            return initial_transforms
            
    def extract_all_features(self, fragments: List[Fragment]) -> Dict[str, dict]:
        """Extract features from all fragments"""
        fragment_features = {}
        
        for fragment in fragments:
            if not fragment.visible or fragment.image_data is None:
                continue
                
            try:
                features = self.extract_features(fragment)
                if features['keypoints'] is not None and len(features['keypoints']) > 0:
                    fragment_features[fragment.id] = features
                    self.logger.debug(f"Extracted {len(features['keypoints'])} features from {fragment.name}")
                else:
                    self.logger.warning(f"No features found in fragment {fragment.name}")
                    
            except Exception as e:
                self.logger.error(f"Feature extraction failed for {fragment.name}: {str(e)}")
                
        return fragment_features
        
    def extract_features(self, fragment: Fragment) -> dict:
        """Extract SIFT features from a fragment"""
        # Get transformed image
        image = fragment.get_transformed_image()
        if image is None:
            return {'keypoints': None, 'descriptors': None}
            
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
            
        # Detect features
        keypoints, descriptors = self.feature_detector.detectAndCompute(gray, None)
        
        return {
            'keypoints': keypoints,
            'descriptors': descriptors,
            'image_shape': gray.shape
        }
        
    def find_pairwise_matches(self, fragments: List[Fragment], 
                            fragment_features: Dict[str, dict]) -> List[dict]:
        """Find feature matches between all pairs of fragments"""
        pairwise_matches = []
        fragment_ids = list(fragment_features.keys())
        
        for i in range(len(fragment_ids)):
            for j in range(i + 1, len(fragment_ids)):
                id1, id2 = fragment_ids[i], fragment_ids[j]
                
                matches = self.match_features(
                    fragment_features[id1], 
                    fragment_features[id2]
                )
                
                if matches and len(matches) >= self.min_matches:
                    # Get fragment objects
                    frag1 = next(f for f in fragments if f.id == id1)
                    frag2 = next(f for f in fragments if f.id == id2)
                    
                    pairwise_matches.append({
                        'fragment1_id': id1,
                        'fragment2_id': id2,
                        'fragment1': frag1,
                        'fragment2': frag2,
                        'matches': matches,
                        'features1': fragment_features[id1],
                        'features2': fragment_features[id2]
                    })
                    
                    self.logger.debug(f"Found {len(matches)} matches between {frag1.name} and {frag2.name}")
                    
        self.logger.info(f"Found {len(pairwise_matches)} fragment pairs with sufficient matches")
        return pairwise_matches
        
    def match_features(self, features1: dict, features2: dict) -> Optional[List]:
        """Match features between two fragments"""
        if (features1['descriptors'] is None or features2['descriptors'] is None or
            len(features1['descriptors']) < 2 or len(features2['descriptors']) < 2):
            return None
            
        try:
            # Find matches using FLANN matcher
            matches = self.matcher.knnMatch(features1['descriptors'], features2['descriptors'], k=2)
            
            # Apply ratio test
            good_matches = []
            for match_pair in matches:
                if len(match_pair) == 2:
                    m, n = match_pair
                    if m.distance < self.match_ratio_threshold * n.distance:
                        good_matches.append(m)
                        
            return good_matches if len(good_matches) >= self.min_matches else None
            
        except Exception as e:
            self.logger.error(f"Feature matching failed: {str(e)}")
            return None
            
    def optimize_transforms(self, fragments: List[Fragment], 
                          pairwise_matches: List[dict],
                          initial_transforms: Dict[str, dict]) -> Dict[str, dict]:
        """Optimize fragment transforms using feature matches"""
        
        # Create parameter vector from initial transforms
        fragment_ids = [f.id for f in fragments if f.visible]
        initial_params = self.transforms_to_params(initial_transforms, fragment_ids)
        
        # Define objective function
        def objective(params):
            return self.compute_alignment_error(params, fragment_ids, pairwise_matches)
            
        # Optimize
        try:
            result = minimize(
                objective,
                initial_params,
                method='L-BFGS-B',
                options={
                    'maxiter': self.max_iterations,
                    'ftol': self.convergence_threshold
                }
            )
            
            if result.success:
                self.logger.info(f"Optimization converged after {result.nit} iterations")
                optimized_transforms = self.params_to_transforms(result.x, fragment_ids)
                return {**initial_transforms, **optimized_transforms}
            else:
                self.logger.warning(f"Optimization failed: {result.message}")
                return initial_transforms
                
        except Exception as e:
            self.logger.error(f"Optimization failed: {str(e)}")
            return initial_transforms
            
    def transforms_to_params(self, transforms: Dict[str, dict], fragment_ids: List[str]) -> np.ndarray:
        """Convert transform dictionaries to parameter vector"""
        params = []
        
        for frag_id in fragment_ids:
            if frag_id in transforms:
                transform = transforms[frag_id]
                # Parameters: [x, y, rotation] (flip is kept fixed)
                params.extend([
                    transform['translation'][0],
                    transform['translation'][1],
                    transform['rotation']
                ])
            else:
                # Default parameters
                params.extend([0.0, 0.0, 0.0])
                
        return np.array(params)
        
    def params_to_transforms(self, params: np.ndarray, fragment_ids: List[str]) -> Dict[str, dict]:
        """Convert parameter vector back to transform dictionaries"""
        transforms = {}
        
        for i, frag_id in enumerate(fragment_ids):
            base_idx = i * 3
            transforms[frag_id] = {
                'translation': (params[base_idx], params[base_idx + 1]),
                'rotation': int(params[base_idx + 2]) % 360,
                'flip_horizontal': False  # Keep original flip state
            }
            
        return transforms
        
    def compute_alignment_error(self, params: np.ndarray, fragment_ids: List[str],
                              pairwise_matches: List[dict]) -> float:
        """Compute alignment error for current parameter values"""
        total_error = 0.0
        num_matches = 0
        
        # Convert params to transforms
        transforms = self.params_to_transforms(params, fragment_ids)
        
        for match_data in pairwise_matches:
            frag1_id = match_data['fragment1_id']
            frag2_id = match_data['fragment2_id']
            
            if frag1_id not in transforms or frag2_id not in transforms:
                continue
                
            # Get transforms
            transform1 = transforms[frag1_id]
            transform2 = transforms[frag2_id]
            
            # Compute error for this pair
            error = self.compute_pairwise_error(match_data, transform1, transform2)
            total_error += error
            num_matches += len(match_data['matches'])
            
        return total_error / max(num_matches, 1)
        
    def compute_pairwise_error(self, match_data: dict, transform1: dict, transform2: dict) -> float:
        """Compute alignment error between a pair of fragments"""
        matches = match_data['matches']
        features1 = match_data['features1']
        features2 = match_data['features2']
        
        if not matches:
            return 0.0
            
        total_error = 0.0
        
        for match in matches:
            # Get keypoint coordinates
            kp1 = features1['keypoints'][match.queryIdx]
            kp2 = features2['keypoints'][match.trainIdx]
            
            # Transform points to world coordinates
            pt1_world = self.transform_point(kp1.pt, transform1)
            pt2_world = self.transform_point(kp2.pt, transform2)
            
            # Compute distance error
            dx = pt1_world[0] - pt2_world[0]
            dy = pt1_world[1] - pt2_world[1]
            error = np.sqrt(dx*dx + dy*dy)
            
            total_error += error
            
        return total_error
        
    def transform_point(self, point: Tuple[float, float], transform: dict) -> Tuple[float, float]:
        """Transform a point using the given transform parameters"""
        x, y = point
        
        # Apply rotation
        angle_rad = np.radians(transform['rotation'])
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        x_rot = x * cos_a - y * sin_a
        y_rot = x * sin_a + y * cos_a
        
        # Apply translation
        x_final = x_rot + transform['translation'][0]
        y_final = y_rot + transform['translation'][1]
        
        return (x_final, y_final)