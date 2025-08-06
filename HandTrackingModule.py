import cv2
import mediapipe as mp
import time


class handDetector():

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    landmark_drawing_spec = self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)
                    connection_drawing_spec = self.mpDraw.DrawingSpec(color=(255, 0, 0), thickness=2)

                    self.mpDraw.draw_landmarks(
                        img,
                        handLms,
                        self.mpHands.HAND_CONNECTIONS,
                        landmark_drawing_spec,
                        connection_drawing_spec
                    )
        return img

    def findPosition(self, img, handNo=0, draw=True):

        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            if handNo < len(self.results.multi_hand_landmarks):
                myHand = self.results.multi_hand_landmarks[handNo]
                h, w, c = img.shape

                for id, lm in enumerate(myHand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                    if draw:
                        if id in [4, 8, 12, 16, 20]:
                            cv2.circle(img, (cx, cy), 8, (255, 0, 255), cv2.FILLED)
                        elif id == 0:
                            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)
        return lmList

    def get_hand_type(self, hand_idx, handedness_list):

        if handedness_list and hand_idx < len(handedness_list):
            return handedness_list[hand_idx].classification[0].label
        return None

    def cleanup(self):
        if hasattr(self, 'hands'):
            self.hands.close()


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    pTime = 0
    detector = handDetector(detectionCon=0.7, trackCon=0.7)

    try:
        while True:
            success, img = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            img = detector.findHands(img)
            lmList_hand0 = detector.findPosition(img, handNo=0, draw=True)

            if lmList_hand0:
                if len(lmList_hand0) > 8:
                    pass

            if detector.maxHands > 1 and detector.results and detector.results.multi_hand_landmarks and len(
                    detector.results.multi_hand_landmarks) > 1:
                lmList_hand1 = detector.findPosition(img, handNo=1, draw=True)

            cTime = time.time()
            fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
            pTime = cTime

            cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
            cv2.imshow("Hand Tracking Example", img)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    finally:
        print("Cleaning up hand detector...")
        detector.cleanup()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()