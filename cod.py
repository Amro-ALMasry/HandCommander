import cv2
import mediapipe as mp
import serial
import time


def send_bluetooth_data(data):
    bt.write(data.encode())
    time.sleep(0.1)
    if bt.in_waiting > 0:
        print("Arduino: ", bt.readline().decode().strip())
    #print("sending bluetooth data:", data)


# Inizializzazione di Mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
bt = serial.Serial('/dev/ttyUSB0', 9600, 1)
time.sleep(2)

# Apertura della webcam
cap = cv2.VideoCapture(0)

# Variabili per tracciare il movimento
posizione_precedente = None
direzione = None

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Impossibile accedere alla webcam.")
        break

    # Conversione dell'immagine in RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        # Prende solo la prima mano rilevata
        hand_landmarks = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        # Calcolo del centroide della mano
        x_totale = 0
        y_totale = 0
        for landmark in hand_landmarks.landmark:
            x_totale += landmark.x
            y_totale += landmark.y

        # Coordinate medie per trovare il centroide
        centro_x = x_totale / len(hand_landmarks.landmark)
        centro_y = y_totale / len(hand_landmarks.landmark)

        # Determina la direzione basata sul movimento
        if posizione_precedente:
            delta_x = centro_x - posizione_precedente[0]
            delta_y = centro_y - posizione_precedente[1]

            if abs(delta_x) > abs(delta_y):  # Movimento orizzontale
                if delta_x > 0.02:  # Sensibilità
                    direzione = "sinistra"
                elif delta_x < -0.02:
                    direzione = "destra"
            else:  # Movimento verticale
                if delta_y > 0.02:  # Sensibilità
                    direzione = "indietro"
                elif delta_y < -0.02:
                    direzione = "avanti"
        else:
            direzione = "Nessun movimento"

        # Aggiorna la posizione precedente
        posizione_precedente = (centro_x, centro_y)

        # Mostra la direzione sullo schermo
        cv2.putText(image, f"Direzione: {direzione}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        send_bluetooth_data(direzione)
    else:
        # Reset se non viene rilevata nessuna mano
        posizione_precedente = None
        direzione = "Nessuna mano rilevata"
        cv2.putText(image, f"Direzione: {direzione}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Mostra il feed della webcam
    cv2.imshow("Controllo del robot con movimento della mano", image)

    # Esci premendo 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Rilascia risorse
cap.release()
cv2.destroyAllWindows()
hands.close()
