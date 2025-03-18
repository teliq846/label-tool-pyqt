import numpy as np
import nibabel as nib
from typing import Tuple, Dict, List, Optional

class NiftiDataManager:
    def __init__(self):
        self.nii_data: Optional[nib.Nifti1Image] = None
        self.unique_labels: List[int] = []
        self.current_label: int = 0
        self.current_slices: Dict[str, int] = {'axial': 0, 'coronal': 0, 'sagittal': 0}
        self.shape: Optional[Tuple[int, int, int]] = None
        self._data_cache: Optional[np.ndarray] = None

    def load_file(self, file_path: str) -> bool:
        """Load NIfTI file and initialize data."""
        try:
            self.nii_data = nib.load(file_path)
            self.shape = self.nii_data.shape
            self._data_cache = self.nii_data.get_fdata()
            self.unique_labels = np.unique(self._data_cache)
            self.unique_labels = self.unique_labels[self.unique_labels > 0]
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def get_slice_data(self, view: str, slice_idx: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get slice data and mask for a specific view and slice index."""
        if self._data_cache is None:
            raise ValueError("No data loaded")

        try:
            # Ensure slice index is within bounds
            if view == 'axial':
                slice_idx = min(max(0, slice_idx), self.shape[2] - 1)
                slice_data = self._data_cache[:, :, slice_idx]
            elif view == 'coronal':
                slice_idx = min(max(0, slice_idx), self.shape[1] - 1)
                slice_data = self._data_cache[:, slice_idx, :]
            elif view == 'sagittal':
                slice_idx = min(max(0, slice_idx), self.shape[0] - 1)
                slice_data = self._data_cache[slice_idx, :, :]
            else:
                raise ValueError(f"Invalid view: {view}")

            # Create mask and ensure data type consistency
            mask = (slice_data == self.current_label).astype(np.float32)
            slice_data = slice_data.astype(np.float32)

            return slice_data, mask
        except Exception as e:
            print(f"Error getting slice data: {e}")
            raise

    def get_optimal_slices(self) -> Dict[str, int]:
        """Calculate optimal slice indices for each view."""
        if self._data_cache is None:
            raise ValueError("No data loaded")

        try:
            mask = (self._data_cache == self.current_label)
            
            optimal_slices = {
                'axial': np.any(mask, axis=(0, 1)),
                'coronal': np.any(mask, axis=(0, 2)),
                'sagittal': np.any(mask, axis=(1, 2))
            }

            result = {}
            for view in optimal_slices:
                available = np.where(optimal_slices[view])[0]
                if len(available) > 0:
                    result[view] = available[len(available) // 2]
                else:
                    # Default to middle slice if no label found
                    if view == 'axial':
                        result[view] = self.shape[2] // 2
                    elif view == 'coronal':
                        result[view] = self.shape[1] // 2
                    else:  # sagittal
                        result[view] = self.shape[0] // 2

            return result
        except Exception as e:
            print(f"Error calculating optimal slices: {e}")
            raise

    def set_current_label(self, label: int):
        """Set current label and update optimal slices."""
        try:
            self.current_label = label
            self.current_slices = self.get_optimal_slices()
        except Exception as e:
            print(f"Error setting current label: {e}")
            raise

    def get_display_data(self, view: str, slice_idx: int) -> np.ndarray:
        """Get processed display data for a specific view and slice."""
        try:
            slice_data, _ = self.get_slice_data(view, slice_idx)
            return np.where(slice_data == self.current_label, 2,
                          np.where(slice_data > 0, 1, 0))
        except Exception as e:
            print(f"Error getting display data: {e}")
            raise 