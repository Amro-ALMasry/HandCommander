import time
import cv2
import mediapipe as mp
import serial

def send_bluetooth_data(data):
    bt.write(data.encode())
    time.sleep(0.1)
    if bt.in_waiting > 0:
        print("Arduino: ", bt.readline().decode().strip())
     #print("sending bluetooth data:", data)

# Inizializza MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.6, min_tracking_confidence=0.6)
bt=serial.Serial("/dev/ttyUSB0",baudrate=9600,timeout=1)

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

def count_fingers(hand_landmarks, handedness_label="Right"):
    """
    Conta le dita (0-5). Usa handedness_label per decidere il pollice.
    handedness_label: "Right" o "Left"
    """
    tip_ids = [4, 8, 12, 16, 20]
    lm = hand_landmarks.landmark
    fingers = []

    # Pollice: confronto sull'asse X, ma dipende da Left/Right
    # confronto tra punta (4) e IP (3)
    if handedness_label == "Right":
        # per mano destra aperto se tip.x < ip.x (immagine già specchiata)
        fingers.append(1 if lm[tip_ids[0]].x < lm[tip_ids[0] - 1].x else 0)
    else:
        # mano sinistra: inverti il confronto
        fingers.append(1 if lm[tip_ids[0]].x > lm[tip_ids[0] - 1].x else 0)

    # Indice, medio, anulare, mignolo: confronto y con landmark due indietro
    for i in range(1, 5):
        fingers.append(1 if lm[tip_ids[i]].y < lm[tip_ids[i] - 2].y else 0)

    return sum(fingers)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("❌ Webcam non trovata")

# Debounce / stabilizzazione: richiedi N frame uguali prima di cambiare comando
DEBOUNCE_FRAMES = 6
current_command = "RILEVAMENTO..."
current_color = COLORS[current_command]
last_command_candidate = None
candidate_count = 0

# Per FPS
prev_time = time.time()

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  # specchia per interfaccia "mirror"
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    detected_command = "RILEVAMENTO..."
    detected_color = COLORS.get(detected_command, (180, 180, 180))
    finger_count = None

    if result.multi_hand_landmarks and len(result.multi_hand_landmarks) > 0:
        # prendi la prima mano rilevata
        hand_landmarks = result.multi_hand_landmarks[0]

        # Prendi la handedness se disponibile (Right/Left)
        handedness_label = "Right"
        if result.multi_handedness and len(result.multi_handedness) > 0:
            try:
                handedness_label = result.multi_handedness[0].classification[0].label
            except Exception:
                handedness_label = "Right"

        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # conta le dita considerando la handedness
        finger_count = count_fingers(hand_landmarks, handedness_label)

        # mappa in comando se esiste mapping
        if finger_count in COMMANDS:
            detected_command = COMMANDS[finger_count]
            detected_color = COLORS.get(detected_command, (180, 180, 180))
        else:
            detected_command = "RILEVAMENTO..."
            detected_color = COLORS.get(detected_command, (180, 180, 180))
        send_bluetooth_data(detected_command)

    # --- Debounce: richiede N frame dello stesso comando per cambiare l'interfaccia ---
    if detected_command == last_command_candidate:
        candidate_count += 1
    else:
        last_command_candidate = detected_command
        candidate_count = 1

    if candidate_count >= DEBOUNCE_FRAMES and detected_command != current_command:
        current_command = detected_command
        current_color = detected_color

    # Mostra comando riconosciuto in alto
    cv2.putText(frame, f"{current_command}", (40, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.3, current_color, 3)

    # Mostra anche il conteggio delle dita (se disponibile)
    if finger_count is not None:
        cv2.putText(frame, f"Dita: {finger_count}", (40, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

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
        text_color = COLORS[cmd] if cmd == current_command else (180, 180, 180)
        text = f"{n}:{cmd}"
        cv2.putText(frame, text, (x_pos, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2)
        x_pos += 110

    # Mostra FPS
    cur_time = time.time()
    fps = 1.0 / (cur_time - prev_time) if (cur_time - prev_time) > 0 else 0.0
    prev_time = cur_time
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 130, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Controllo Robot - Gesture HUD", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
