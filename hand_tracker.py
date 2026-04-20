import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.prev_x = None
        self.prev_y = None

    def get_gesture(self, frame):
        gesture = None
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(
                frame, hand, self.mp_hands.HAND_CONNECTIONS
            )

            wrist = hand.landmark[0]
            curr_x = wrist.x * w
            curr_y = wrist.y * h

            if self.prev_x is not None:
                dx = curr_x - self.prev_x
                dy = curr_y - self.prev_y

                if abs(dx) > abs(dy):
                    if dx > 30:
                        gesture = "RIGHT"
                    elif dx < -30:
                        gesture = "LEFT"
                else:
                    if dy < -30:
                        gesture = "UP"
                    elif dy > 30:
                        gesture = "DOWN"

                if gesture:
                    cv2.putText(frame, f"Gesture: {gesture}",
                                (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2)

            self.prev_x = curr_x
            self.prev_y = curr_y

        return frame, gesture