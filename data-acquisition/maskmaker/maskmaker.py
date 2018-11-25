import os

import xml.etree.ElementTree as ET
import PIL.ImageDraw as ImageDraw
import PIL.Image as Image

################
### Defaults ###
################

# white fill
FILL = (255, 255, 255)

# Transparent format
IMG_COLOR = (255, 255, 255, 0)

class ImageMask(object):
    def __init__(self, xml_path, img_color=IMG_COLOR, polygon_fill=FILL):
        """Create an ImageMask instance from an XML path
        """
        self.root = ET.parse(xml_path)
        self._masks = []
        self.img_color = img_color
        self.polygon_fill = polygon_fill

    @property
    def dim(self):
        nrows = int(self.root.find('imagesize/nrows').text)
        ncols = int(self.root.find('imagesize/ncols').text)

        # Image size is determined as width x height
        return ncols, nrows

    @property
    def image_name(self):
        return self.root.find('filename').text

    @property
    def polygons(self):
        polygon_coords = []
        polygons = [x.find('polygon') for x in self.root.findall('object')]
        for poly in polygons:
            polygon_coords.append(self._make_polygon_from_xml(poly))

        return polygon_coords

    @property
    def masks(self):
        if self._masks:
            return self._masks

        for points in self.polygons:
            image = Image.new("RGBA", self.dim, self.img_color)
            draw = ImageDraw.Draw(image)
            draw.polygon(list(points), fill=self.polygon_fill)
            self._masks.append(image)

        return self._masks

    @property
    def annotations(self):
        return [x.text.strip() for x in imask.root.findall('object/name')]

    def save_masks(self, output_dir=None):
        if not output_dir:
            output_dir = os.path.basename(self.image_name).split(".")[0]

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        i = 0
        for mask, annot in zip(self.masks, self.annotations):
            mask_file = self._mask_name(i, annot)
            mask_filepath = os.path.join(output_dir, mask_file)
            mask.save(mask_filepath, 'PNG')
            i += 1

    def __del__(self):
        for mask in self.masks:
            mask.close()

    def _make_polygon_from_xml(self, xml_poly):
        x_points = [int(x.text.strip()) for x in xml_poly.findall('pt/x')]
        y_points = [int(y.text.strip()) for y in xml_poly.findall('pt/y')]

        return zip(x_points, y_points)

    def _mask_name(self, i, annot):
        """Create a pretty mask name. Assume we won't have more than 999 masks in an image"""
        return str(i).rjust(3, "0") + "_" + annot + ".png"
