# Data Synthesis

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

The [image templates](./img_templates) directory contains these images.

#### Coordinate Configuration

The synthesizer is currently rule-based, and has no "vision" capabilities. We need to specify the coordinates in the background image (in terms of pixels), that the foreground images can be placed on. The synthesizer models shelves as line equations, and thus one needs to specify the coordinates of each shelf, in the form of bounded regions.

<details><summary>A sample entry in the `backgrounds.json` file:</summary>

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

### Code

The module exports the `DataSynthesizer` class
