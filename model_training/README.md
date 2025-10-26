# Paper Corner Detection with YOLO

This script allows you to finetune a YOLO model (starting from `best.pt`) to detect the 4 corners of a paper in images.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create your dataset using the annotation tool:
```bash
# Annotate paper corners in your images
python annotate_paper_corners.py --images /path/to/your/images --output paper_corners.json

# Convert to COCO format
python convert_to_coco.py --annotations paper_corners.json --output /path/to/coco/dataset
```

3. Your final dataset structure should be:
```
data_dir/
├── train/
│   └── images/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
├── val/
│   └── images/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
└── annotations/
    ├── instances_train.json
    └── instances_val.json
```

## Usage

### Basic usage:
```bash
python train.py --data /path/to/coco/dataset
```

### Advanced usage with custom parameters:
```bash
python train.py \
    --model best.pt \
    --data /path/to/coco/dataset \
    --epochs 200 \
    --batch-size 32 \
    --img-size 640 \
    --device cuda \
    --workers 8
```

## Annotation Tool

The `annotate_paper_corners.py` script provides an interactive tool to mark paper corners:

- **Click** on the 4 corners of a paper in order: top-left, top-right, bottom-left, bottom-right
- **Press 's'** to save annotations
- **Press 'n'** for next image  
- **Press 'r'** to reset current image
- **Press 'q'** to quit

## Complete Workflow

1. **Collect images** of papers in various orientations and lighting
2. **Annotate corners** using the annotation tool
3. **Convert to COCO format** for YOLO training
4. **Train the model** with the finetuned script
5. **Use the trained model** for paper corner detection

## Parameters

- `--model`: Path to pretrained model (default: best.pt)
- `--data`: Path to COCO dataset directory (required)
- `--epochs`: Number of training epochs (default: 100)
- `--batch-size`: Batch size for training (default: 16)
- `--img-size`: Image size for training (default: 640)
- `--device`: Device to use for training (default: auto)
- `--workers`: Number of data loading workers (default: 8)

## Features

- **COCO Dataset Support**: Full support for COCO format with automatic conversion to YOLO format
- **Flexible Configuration**: Comprehensive training parameters for fine-tuning
- **Logging**: Detailed logging of training progress
- **Checkpointing**: Automatic model saving and checkpointing
- **Data Augmentation**: Built-in augmentation techniques
- **Validation**: Automatic validation during training

## Training Parameters

The script includes optimized training parameters:
- Optimizer: AdamW
- Learning rate: 0.001 (with cosine annealing)
- Weight decay: 0.0005
- Data augmentation: Mosaic, mixup, HSV augmentation, etc.
- Loss weights: Box (7.5), Classification (0.5), DFL (1.5)

## Output

Training results will be saved to `runs/train/yolo_finetune_YYYYMMDD_HHMMSS/` with:
- Best model weights
- Training plots
- Validation results
- Configuration files

## Example

```bash
# Train on COCO dataset with default settings
python train.py --data /path/to/coco2017

# Train with custom settings
python train.py \
    --data /path/to/coco2017 \
    --epochs 300 \
    --batch-size 64 \
    --img-size 1024 \
    --device cuda:0
```
