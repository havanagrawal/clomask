# MaskMaker

## Introduction

Using the polygon tool on LabelMe, one can generate polygons for various objects in an image. These polygons can subsequently be downloaded in an XML format. This module is a thin wrapper for parsing the XML into mask files.

## Directory Structure

The LabelMe dataset can be downloaded in a ZIP file format (say `collection.zip`). Once you unzip it, it will have the following directory structure

```
collection/
├── Annotations
│   └── users
│       └── [user]
│           └── [cname]
├── Images
│   └── users
│       └── [user]
│           └── [cname]
├── Masks
│   └── users
│       └── [user]
│           └── [cname]
└── Scribbles
    └── users
        └── [user]
            └── [cname]
```

1. The `user` is the alias of the person who annotated the image.  
1. The `cname` is the name of the collection to which this image belongs.
1. The files under `Images/users/[user]/[cname]` are the original JPG images.  
1. The files under `Masks/users/[user]/[cname]` are the PNG mask files. Each file is named as `{image_name}_mask_{i}.png`.
1. The files under `Annotations/users/[user]/[cname]` are the XML files that contain the polygon definitions.

## Usage

```bash
python3 transform.py --help
usage: transform.py [-h] --root ROOT [--user USER] [--cname CNAME]
                    [--dest DEST]

Standardize the directory structure for labeled data from LabelMe

optional arguments:
  -h, --help     show this help message and exit
  --root ROOT    Absolute path to the unzipped directory as downloaded from
                 LabelMe
  --user USER    The username who labeled the data on LabelMe
  --cname CNAME  The name of the collection on LabelMe
  --dest DEST    The top level directory in the output. Consider naming this
                 either 'train' or 'test'
```

Example

```bash
python3 transform.py \
  --root ./collection/ \
  --dest test \
  --cname bottles \
  --user havanagrawal
```
