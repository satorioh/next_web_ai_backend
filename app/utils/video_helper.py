import cv2
from aiortc import MediaStreamTrack
from av import VideoFrame
from .magic_shield import ShieldModule, init_detector

shield_module = ShieldModule()
detector = init_detector(shield_module.print_result)


class VideoTransformTrack(MediaStreamTrack):
    """
    A video stream track that transforms frames from an another track.
    """

    kind = "video"

    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform

    async def recv(self):
        frame = await self.track.recv()

        if self.transform == "edges":
            # perform edge detection
            img = frame.to_ndarray(format="bgr24")

            # Reduce resolution
            resized_img = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))

            # Apply edge detection on the resized image
            edges = cv2.Canny(resized_img, 100, 200)

            # Scale the result back to the original resolution
            edges = cv2.resize(edges, (img.shape[1], img.shape[0]))

            # Convert edges to BGR format
            edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(edges_bgr, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame

        elif self.transform == "shield":
            img = frame.to_ndarray(format="bgr24")

            # Reduce resolution
            resized_img = cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2))

            # Apply shield_module.main on the resized image
            shield_image = shield_module.main(detector, resized_img)

            # Scale the result back to the original resolution
            shield_image = cv2.resize(shield_image, (img.shape[1], img.shape[0]))

            # Rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(shield_image, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "rotate":
            # rotate image
            img = frame.to_ndarray(format="bgr24")
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        else:
            return frame
