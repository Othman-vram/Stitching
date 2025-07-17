# Tissue Fragment Arrangement and Rigid Stitching UI

A professional desktop application for visualizing, manipulating, and stitching multiple tissue image fragments from pyramidal TIFF and SVS files.

## Features

- **High-Resolution Image Support**: Handles pyramidal TIFF and SVS files with multi-resolution viewing
- **Interactive Canvas**: Zoom, pan, and navigate large tissue images with smooth performance
- **Fragment Manipulation**: Individual rotation (90° steps), horizontal mirroring, and translation
- **Real-time Updates**: Non-destructive transformations with immediate visual feedback
- **Professional UI**: Dark theme optimized for medical imaging workflows
- **Export Capabilities**: Save composite images and transformation metadata
- **Rigid Stitching**: Optional refinement using current positions as initial guesses

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Required Packages

- PyQt6 (GUI framework)
- OpenCV (image processing)
- NumPy (numerical operations)
- Pillow (image handling)
- OpenSlide (pyramidal image support)
- scikit-image (image processing algorithms)
- SciPy (scientific computing)
- matplotlib (visualization)
- tifffile (TIFF file handling)

## Usage

### Running the Application

```bash
python main.py
```

### Loading Images

1. Use **File → Load Images** or press `Ctrl+O`
2. Select one or more TIFF or SVS files
3. Images will be loaded and displayed on the canvas

### Fragment Manipulation

1. **Selection**: Click on a fragment in the canvas or select from the fragment list
2. **Rotation**: Use rotation buttons or keyboard shortcuts
3. **Mirroring**: Toggle horizontal flip
4. **Translation**: Use arrow buttons or drag fragments directly
5. **Visibility**: Toggle fragment visibility in the fragment list

### Keyboard Shortcuts

- `Ctrl+O`: Load images
- `Ctrl+E`: Export image
- `Ctrl+M`: Export metadata
- `Ctrl+S`: Perform rigid stitching
- `Ctrl+R`: Reset all transformations
- `Ctrl+0`: Zoom to fit
- `Ctrl+1`: Zoom to 100%
- `Ctrl+Q`: Quit application

### Export Options

- **Export Image**: Save the composite result as TIFF, PNG, or JPEG
- **Export Metadata**: Save transformation data as JSON for reproducibility

## Architecture

### Core Components

- **MainWindow**: Primary application window and coordination
- **FragmentManager**: Handles fragment data and transformations
- **CanvasWidget**: High-performance image display and interaction
- **ControlPanel**: Fragment manipulation controls
- **ImageLoader**: Multi-format image loading with pyramid support

### Key Classes

- `Fragment`: Data structure for individual tissue fragments
- `FragmentManager`: Centralized fragment state management
- `ImageLoader`: Handles TIFF, SVS, and other formats
- `RigidStitchingAlgorithm`: Feature-based alignment refinement
- `ExportManager`: Image and metadata export functionality

## File Structure

```
src/
├── main_window.py          # Main application window
├── core/
│   ├── fragment.py         # Fragment data structure
│   ├── fragment_manager.py # Fragment management system
│   └── image_loader.py     # Multi-format image loading
├── ui/
│   ├── canvas_widget.py    # Interactive canvas display
│   ├── control_panel.py    # Fragment controls
│   ├── fragment_list.py    # Fragment selection list
│   ├── toolbar.py          # Main toolbar
│   └── theme.py           # Application styling
├── algorithms/
│   └── rigid_stitching.py # Stitching refinement
└── utils/
    └── export_manager.py   # Export functionality
```

## Technical Details

### Image Handling

- Supports pyramidal TIFF and SVS files
- Automatic pyramid level selection for optimal performance
- Memory-efficient loading of large images
- Non-destructive transformations

### Performance Optimizations

- Multi-resolution pyramid rendering
- Efficient canvas updates
- Background processing for large operations
- Memory management for large datasets

### Transformation System

- Matrix-based transformations for accuracy
- Real-time preview updates
- Undo/redo capability
- Metadata preservation

## Development

### Adding New Features

1. Core functionality goes in `src/core/`
2. UI components go in `src/ui/`
3. Algorithms go in `src/algorithms/`
4. Utilities go in `src/utils/`

### Testing

Run the application with sample data to verify functionality:

```bash
python main.py
```

## Troubleshooting

### Common Issues

1. **OpenSlide not found**: Install OpenSlide system library
2. **Memory errors**: Reduce image resolution or close other applications
3. **Slow performance**: Check available RAM and graphics drivers

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 1GB free space
- **Graphics**: OpenGL 2.1 or higher
- **OS**: Windows 10+, macOS 10.14+, or Linux

## License

This software is provided for research and educational purposes.

## Support

For issues and questions, please refer to the documentation or create an issue in the project repository.