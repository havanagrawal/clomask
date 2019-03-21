"""Configuration for the custom-trained CloMask model"""

from config import Config

class ClomaskConfig(Config):
    """
    Mask RCNN configuration for Clomask
    """
    # Give the configuration a recognizable name
    NAME = "clomask"

    # Image resize mode ['crop', 'square', 'pad64']
    IMAGE_RESIZE_MODE = 'crop'

    # Optimizer, default is 'SGD'
    OPTIMIZER = 'ADAM'

    # Train on 1 GPU and 2 images per GPU.
    GPU_COUNT = 1
    IMAGES_PER_GPU = 2

    # Number of classes (including background)
    NUM_CLASSES = 1 + 3  # background + bottles + candy_boxes + chips_bag

    # Input image resing
    # Images are resized such that the smallest side is >= IMAGE_MIN_DIM and
    # the longest side is <= IMAGE_MAX_DIM. In case both conditions can't
    # be satisfied together the IMAGE_MAX_DIM is enforced.
    IMAGE_MIN_DIM = 512
    IMAGE_MAX_DIM = 512

    IMAGE_MIN_SCALE = 0

    # Backbone encoder architecture
    BACKBONE = 'resnet101'

    # Using default anchors as object size is not too small.
    RPN_ANCHOR_SCALES = (16, 32, 64, 128, 256)

    # How many anchors per image to use for RPN training
    RPN_TRAIN_ANCHORS_PER_IMAGE = 320  #

    # ROIs kept after non-maximum supression (training and inference)
    POST_NMS_ROIS_TRAINING = 2048
    POST_NMS_ROIS_INFERENCE = 2048
    IMAGE_COLOR = 'RGB'

    # Number of ROIs per image to feed to classifier/mask heads
    TRAIN_ROIS_PER_IMAGE = 512

    # Non-max suppression threshold to filter RPN proposals.
    # Can be increased during training to generate more proposals.
    RPN_NMS_THRESHOLD = 0.7
    # Maximum number of ground truth instances to use in one image
    # We set this to 300 as we have control over how many masks we have in an image.
    MAX_GT_INSTANCES = 300

    # Max number of final detections
    DETECTION_MAX_INSTANCES = 300

    # Minimum probability value to accept a detected instance
    # ROIs below this threshold are skipped
    DETECTION_MIN_CONFIDENCE = 0.85

    # Non-maximum suppression threshold for detection
    DETECTION_NMS_THRESHOLD = 0.3  # 0.3

    # Threshold number for mask binarization, only used in inference mode
    DETECTION_MASK_THRESHOLD = 0.35


class InferenceConfig(ClomaskConfig):
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1
    IMAGE_RESIZE_MODE = "square"
    IMAGE_MIN_DIM = 1024
    IMAGE_MAX_DIM = 1024
    POST_NMS_ROIS_INFERENCE = 2000
    POST_NMS_ROIS_TRAINING = 2000
    RPN_ANCHOR_SCALES = (16, 32, 64, 128, 256)
    DETECTION_MAX_INSTANCES = 300
    DETECTION_MIN_CONFIDENCE = 0.85
