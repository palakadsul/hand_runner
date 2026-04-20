import cv2
import pygame
import sys
from hand_tracker import HandTracker
from game import Game

def main():
    tracker = HandTracker()
    game = Game()

    # Open webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("❌ Webcam not found!")
        sys.exit()

    print("✅ Hand Runner started!")
    print("Show your hand to the webcam to play")
    print("Press Q to quit")

    while True:
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                cv2.destroyAllWindows()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    cap.release()
                    cv2.destroyAllWindows()
                    pygame.quit()
                    sys.exit()

        # Read webcam frame
        ret, frame = cap.read()
        if not ret:
            print("❌ Webcam read failed")
            break

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)

        # Get gesture from hand tracker
        frame, gesture = tracker.get_gesture(frame)

        # Update game with gesture
        game.update(gesture)

        # Draw game
        game.draw()

        # Show webcam feed
        cv2.imshow("Hand Runner - Webcam", frame)

        game.tick()

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()