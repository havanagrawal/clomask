# Data Synthesis

## Table of Contents

1. [Introduction](#introduction)  
1. [Examples](#examples)  
1. [Usage](#usage)  
    1. [Configuration](#configuration)  
        1. [Image Templates](#image-templates)  
        1. [Coordinate Configuration](#coordinate-configuration)  
    1. [Code](#code)  

## Introduction

Deep learning models such as CNNs require a significant amount of data, on the order of hundreds or even thousands of examples per class. In the scope of this project, we had two particular challenges:

1. Project Timeline had a hard deadline (September 2018 - March 2019)
2. Time and effort required to label data manually did not have the required yield.

Further, training and test time image augmentation (random crops, rotations and flips) can only boost the model to a certain extent. Due to these challenges, there was a need to generate/synthesize data that would allow us to kickstart the model training/tuning process.

**This module attempts to achieve the generation of large-scale, reproducible image/mask datasets with a high degree of variance.**

## Examples

See [the demo notebook](./Synthetic-Data-Creation-for-Retail-Environments.ipynb)

## Usage

### Configuration

Before generating the data, a fair amount of configuration is required.

#### Image Templates

The data synthesizer generates data by randomizing object placement on images of shelves.
In order to achieve this, we need two types of images,
  1. `backgrounds` which model objects such as shelves, fridges, table tops, etc.,
  2. `foregrounds` which model objects that are to be placed on the `background` objects, such as bottles, cans, bags of chips, candy bags, etc.

The [image templates](./img_templates) directory contains these images. Note that the foreground images MUST be in PNG format to support overlaying them on the background in a meaningful manner.

#### Coordinate Configuration

The synthesizer is currently rule-based, and has no "vision" capabilities. We need to specify the coordinates in the background image (in terms of pixels), that the foreground images can be placed on. The synthesizer models shelves as line equations, and thus one needs to specify the coordinates of each shelf, in the form of bounded regions.

The configuration files should be stored in a `config` directory, and have the following structure:
```
config
├── backgrounds.json
├── class_map.json
└── foregrounds.json
```

We will talk about each of these files below:

##### [`backgrounds.json`](./config/backgrounds.json)

A sample entry in the `backgrounds.json` file:
<details><summary>Expand:</summary>

<p>

```json
{
  "supermarket_shelf_4": {
    "shelves": [
      {
        "x_start": 0,
        "y_start": 48,
        "x_end": 264,
        "y_end": 47
      },
      {
        "x_start": 15,
        "y_start": 87,
        "x_end": 263,
        "y_end": 169
      },
      {
        "x_start": 0,
        "y_start": 93,
        "x_end": 263,
        "y_end": 201,
        "is_dummy": true
      },
      {
        "x_start": 15,
        "y_start": 157,
        "x_end": 262,
        "y_end": 383
      }
    ]
  }
}
```

</p>
</details>

Most of the configuration is self-explanatory:

1. The key should be the same name as the image in the `img_templates/backgrounds` directory
1. The order of the line coordinates matters. Each shelf region is constructed by a pair of consecutive lines.
1. The `is_dummy` field allows us to account for shelves that have significant width (especially in images with an angled PoV), and restrict the items from overlapping upper shelves. If the `is_dummy` field is true, it accounts for a line equation, but will not allow items to be placed on it.

##### [`foregrounds.json`](./config/foregrounds.json)

This is a simpler configuration, where the `height` and `width` of each foreground object is stored. A sample entry looks like the following:

```json
{
  "bottles": {
    "bottle_01": {
        "width": 188,
        "height": 500
    },
    "bottle_02": {
        "width": 124,
        "height": 438
    }
  }
}
```

1. The key should be the same name as the image in the `img_templates/foregrounds` directory

##### [`class_map.json`](./config/class_map.json)

The class map is used purely for naming files. This is necessary because once the mask PNG file is generated, we need a way to identify which class it originally was. A sample file:

```json
{
	"bottles": 1,
	"boxes": 2,
	"bags": 3
}
```

This file is needed to keep the class number for each class constant. Consider the use case where a model has been (pre-)trained on bottles in one pass, and needs to be trained on boxes and bags in the next iteration. We still need to retain the fact that the original weights have been learned with "bottles" as 1.

### Code

The module exports the [`DataSynthesizer`](./src/data_synthesizer/data_synthesizer.py#L30) and [`ParallelDataSynthesizer`](./src/data_synthesizer/data_synthesizer.py#L280) classes. These are heavily documented, and their usage can be seen in [the demo notebook](./Synthetic-Data-Creation-for-Retail-Environments.ipynb). Usually, one would follow a simple pattern for generating datasets:

1. With the `DataSynthesizer` class:  
```python
from src.data_synthesizer import DataSynthesizer

config_path = 'config/'
template_path = "img_templates/"
output_dir = "data/"

synthesizer = DataSynthesizer(config_path, template_path)

# Generate 10 data points
save_path = synthesizer.generate_synthetic_dataset(
    n = 10,
    output_dir = output_dir,
    categories = ["bottles", "bags", "boxes"],
    nomask_categories = ["cans"],
    rotation_probability = 0,
    max_objs_in_pack = 2,
    max_x_offset = 10,
    skip_shelf_probability = 0.05,
    verbose = True
)
```  
2. With the `ParallelDataSynthesizer` class:  
```python
from src.data_synthesizer import DataSynthesizer

config_path = 'config/'
template_path = "img_templates/"
output_dir = "data/"

synthesizer = ParallelDataSynthesizer(config_path, template_path, n_jobs=10)

# Generate 100 data points
results = synthesizer.generate_synthetic_dataset(
    n = 100,
    output_dir = output_dir,
    categories = ["bottles", "bags", "boxes"],
    nomask_categories = ["cans"],
    rotation_probability = 0,
    max_objs_in_pack = 2,
    max_x_offset = 10,
    skip_shelf_probability = 0.05,
    verbose = True
)

# Resolve the async results, merge the datasets and get a single dataset
save_path = ParallelDataSynthesizer.merge(results, output_dir=output_dir)
```  
