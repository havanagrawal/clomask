# Model Performance w.r.t. Image Resolution

## Background

In the meeting with Clobotics on 21st December, it was noted that image resolution may be a factor in the performance of the model, which seems intuitive. Unclear/blurry images will result in lower performance (as measured by mAP). This section is a formal analysis of the effect of image resolution on mAP.

## What is Resolution?

In the context of images, we can use two definitions of resolution:
1. **Pixel resolution** is the literal number of pixels in the image. This is the most common usage. An image of 1024x1024 resolution literally means it is 1024 pixels wide and 1024 pixels high, for a total of 1048576 pixels, ~3MB (uncompressed) or 214kB (compressed JPG).
2. **Spatial resolution** is the smallest discernible detail in the image. This is colloquially the clarity of the image; blurry images have lower spatial resolution, even though they may have the same pixel resolution as a clear image.

For this analysis, we use both definitions. From the context of a user clicking photos, the first one is determined by their camera quality, and the second is controlled by how well the camera can focus on an image.

## Results

:construction:
