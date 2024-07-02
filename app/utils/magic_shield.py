import mediapipe as mp
import cv2
from pathlib import Path
from ..utils.log import setup_logger

logger = setup_logger(__name__)

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = f"{Path(__file__).parent.parent}/model/hand_landmarker.task"
SHIELD_1 = cv2.imread(f"{Path(__file__).parent.parent}/asserts/magic_circle_ccw.png", -1)
SHIELD_2 = cv2.imread(f"{Path(__file__).parent.parent}/asserts/magic_circle_cw.png", -1)

ANG_VEL = 2.0  # 角速度
SHOW_SHIELD_RATIO = 1.0
SHIELD_SCALE = 2.0


class ShieldModule:
    def __init__(self):
        logger.info("init ShieldModule")
        self.result = None
        self.timestamp = 0
        self.deg = 0  # 旋转角度
        self.hand0 = {
            "wrist": None,
            "thumb_tip": None,
            "index_mcp": None,
            "index_tip": None,
            "midle_mcp": None,
            "midle_tip": None,
            "ring_tip": None,
            "pinky_tip": None
        }
        self.hand1 = {
            "wrist": None,
            "thumb_tip": None,
            "index_mcp": None,
            "index_tip": None,
            "midle_mcp": None,
            "midle_tip": None,
            "ring_tip": None,
            "pinky_tip": None
        }

    def print_result(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        self.result = result

    def draw_line(self, img, p1, p2, size=5):
        cv2.line(img, p1, p2, (50, 50, 255), size)
        cv2.line(img, p1, p2, (255, 255, 255), round(size / 2))

    def set_position_data(self, lmlist, hand):
        hand["wrist"] = (lmlist[0][0], lmlist[0][1])
        hand["thumb_tip"] = (lmlist[4][0], lmlist[4][1])
        hand["index_mcp"] = (lmlist[5][0], lmlist[5][1])
        hand["index_tip"] = (lmlist[8][0], lmlist[8][1])
        hand["midle_mcp"] = (lmlist[9][0], lmlist[9][1])
        hand["midle_tip"] = (lmlist[12][0], lmlist[12][1])
        hand["ring_tip"] = (lmlist[16][0], lmlist[16][1])
        hand["pinky_tip"] = (lmlist[20][0], lmlist[20][1])

    def calc_distance(self, p1, p2):
        x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** (1.0 / 2)

    def calc_ratio(self, hand):
        wrist = hand["wrist"]
        index_mcp = hand["index_mcp"]
        index_tip = hand["index_tip"]
        pinky_tip = hand["pinky_tip"]
        thumb_tip = hand["thumb_tip"]
        hand_close = self.calc_distance(wrist, index_mcp)
        hand_open = self.calc_distance(index_tip, pinky_tip)
        # hand_open = self.calc_distance(thumb_tip, pinky_tip)
        return hand_open / hand_close, hand_close, hand_open

    def draw_hand_lines(self, image, hand):
        wrist = hand["wrist"]
        thumb_tip = hand["thumb_tip"]
        index_tip = hand["index_tip"]
        midle_tip = hand["midle_tip"]
        ring_tip = hand["ring_tip"]
        pinky_tip = hand["pinky_tip"]
        self.draw_line(image, wrist, thumb_tip)
        self.draw_line(image, wrist, index_tip)
        self.draw_line(image, wrist, midle_tip)
        self.draw_line(image, wrist, ring_tip)
        self.draw_line(image, wrist, pinky_tip)
        self.draw_line(image, thumb_tip, index_tip)
        self.draw_line(image, thumb_tip, midle_tip)
        self.draw_line(image, thumb_tip, ring_tip)
        self.draw_line(image, thumb_tip, pinky_tip)

    def calc_shield_position(self, image, hand, hand_close):
        midle_mcp = hand["midle_mcp"]
        center_x, center_y = midle_mcp
        diameter = round(hand_close * SHIELD_SCALE)
        x1 = round(center_x - (diameter / 2))  # shield left
        y1 = round(center_y - (diameter / 2))  # shield top
        h, w, c = image.shape
        if x1 < 0:
            x1 = 0
        elif x1 > w:
            x1 = w
        if y1 < 0:
            y1 = 0
        elif y1 > h:
            y1 = h
        if x1 + diameter > w:
            diameter = w - x1
        if y1 + diameter > h:
            diameter = h - y1
        shield_size = diameter, diameter
        return x1, y1, diameter, shield_size

    def get_rotated_image(self):
        self.deg += ANG_VEL
        if self.deg > 360:
            self.deg = 0
        hei, wid, col = SHIELD_1.shape  # SHIELD_1和SHIELD_2尺寸相同
        cen = (wid // 2, hei // 2)
        M1 = cv2.getRotationMatrix2D(cen, round(self.deg), 1.0)
        M2 = cv2.getRotationMatrix2D(cen, round(360 - self.deg), 1.0)
        rotated1 = cv2.warpAffine(SHIELD_1, M1, (wid, hei))
        rotated2 = cv2.warpAffine(SHIELD_2, M2, (wid, hei))
        return rotated1, rotated2

    def transparent(self, shield_img, x, y, image, size=None):
        if size is not None:
            shield_img = cv2.resize(shield_img, size)

        original_image = image.copy()
        b, g, r, a = cv2.split(shield_img)
        overlay_color = cv2.merge((b, g, r))
        mask = cv2.medianBlur(a, 1)
        h, w, _ = overlay_color.shape
        roi = original_image[y:y + h, x:x + w]

        img1_bg = cv2.bitwise_and(roi.copy(), roi.copy(), mask=cv2.bitwise_not(mask))
        img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)
        original_image[y:y + h, x:x + w] = cv2.add(img1_bg, img2_fg)

        return original_image

    def loop_hands_landmark(self, image):
        h, w, c = image.shape
        for index, hand_landmark in enumerate(self.result.hand_landmarks):
            hand = self.hand0 if index == 0 else self.hand1
            # rotate_deg = DEG_0 if index == 0 else DEG_1

            # set hand landmarks data
            lm_list = []
            for idx, lm in enumerate(hand_landmark):
                coor_x, coor_y = int(lm.x * w), int(lm.y * h)
                lm_list.append([coor_x, coor_y])
            self.set_position_data(lm_list, hand)

            # calculate distance and ratio
            ratio, hand_close, hand_open = self.calc_ratio(hand)
            # logger.info(ratio)

            # draw hand lines or show shield
            if ratio and (0.5 < ratio < SHOW_SHIELD_RATIO):
                self.draw_hand_lines(image, hand)
            if ratio and ratio > SHOW_SHIELD_RATIO:
                x1, y1, diameter, shield_size = self.calc_shield_position(image, hand, hand_close)
                rotated1, rotated2 = self.get_rotated_image()
                if diameter != 0:
                    image = self.transparent(rotated1, x1, y1, image, shield_size)
                    image = self.transparent(rotated2, x1, y1, image, shield_size)
        return image

    async def main(self, detector, frame):
        while True:
            image = cv2.flip(frame, 1)
            image_for_detect = mp.Image(image_format=mp.ImageFormat.SRGBA, data=cv2.cvtColor(image, cv2.COLOR_BGR2RGBA))

            self.timestamp += 1
            detector.detect_async(image_for_detect, self.timestamp)

            if self.result is not None:
                shield_image = self.loop_hands_landmark(image)
                return shield_image
            return image


def init_detector(callback):
    logger.info("init detector")
    base_options = BaseOptions(model_asset_path=MODEL_PATH, delegate=BaseOptions.Delegate.CPU)
    options = HandLandmarkerOptions(base_options=base_options, running_mode=VisionRunningMode.LIVE_STREAM,
                                    num_hands=2,
                                    result_callback=callback)
    return HandLandmarker.create_from_options(options)
