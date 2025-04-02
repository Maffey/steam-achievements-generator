# Fake Steam Achievements Generator

A Python CLI tool that generates fake Steam achievement images. This tool allows you to create achievement images that look exactly like real Steam achievements, including the special golden glow effect for rare achievements.

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python achievement_generator.py --name "Achievement Name" --description "Achievement description text" --image path/to/image.png --rare
```

### Arguments

- `--name`: The name of the achievement (required)
- `--description`: The description of the achievement (required)
- `--image`: Path to the achievement icon image (required)
- `--rare`: Flag to indicate if the achievement is rare (optional, adds golden glow effect)

## Output

The generated achievement image will be saved in the `output` directory with the format: `achievement_[timestamp].png` 