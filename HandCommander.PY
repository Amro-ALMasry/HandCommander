import cv2
import mediapipe as mp

# Inizializza MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6)

COMMANDS = {
    1: "AVANTI",
    2: "DESTRA",
    3: "SINISTRA",
    4: "DIETRO",
    5: "FERMO"
}

COLORS = {
    "AVANTI": (0, 255, 0),
    "DESTRA": (255, 0, 0),
    "SINISTRA": (255, 255, 0),
    "DIETRO": (0, 0, 255),
    "FERMO": (0, 165, 255),
    "RILEVAMENTO...": (180, 180, 180)
}

def count_fingers(hand_landmarks):
    tip_ids = [4, 8, 12, 16, 20]
    fingers = []
    lm = hand_landmarks.landmark
    fingers.append(1 if lm[tip_ids[0]].x < lm[tip_ids[0]-1].x else 0)  # Pollice
    for i in range(1, 5):
        fingers.append(1 if lm[tip_ids[i]].y < lm[tip_ids[i]-2].y else 0)
    return sum(fingers)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("❌ Webcam non trovata")

while True:
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    comando = "RILEVAMENTO..."
    colore = COLORS[comando]

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            n_fingers = count_fingers(hand_landmarks)
            if n_fingers in COMMANDS:
                comando = COMMANDS[n_fingers]
                colore = COLORS[comando]

    # Mostra comando riconosciuto in alto
    cv2.putText(frame, f"{comando}", (40, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, colore, 3)

    # --- Barra informativa compatta in basso con colori ---
    h, w, _ = frame.shape
    
    # Background semi-trasparente
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h - 50), (w, h), (30, 30, 30), -1)
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
    
    # Bordo superiore
    cv2.line(frame, (0, h - 50), (w, h - 50), (255, 255, 255), 2)
    
    # Mostra ogni comando separatamente con il colore appropriato
    x_pos = 20
    for n, cmd in COMMANDS.items():
        # Colora il comando attivo, grigio gli altri
        text_color = COLORS[cmd] if cmd == comando else (180, 180, 180)
        text = f"{n}:{cmd}"
        cv2.putText(frame, text, (x_pos, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)
        # Ridotta la distanza tra i comandi
        x_pos += 110

    cv2.imshow("Controllo Robot - Gesture HUD", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()