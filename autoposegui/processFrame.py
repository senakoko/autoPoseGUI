import cv2


def process_frame(image, scale_factor=0.5):
    height, width = image.shape[:2]
    height = int(height * scale_factor)
    width = int(width * scale_factor)
    dim = (width, height)
    image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return image
