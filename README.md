# Gesture Robot Control

Un'applicazione Python che utilizza la webcam per riconoscere le **gesture della mano** e trasformarle in **comandi per un robot o per il controllo interattivo**. Mostra sullo schermo il comando rilevato e una barra informativa con i comandi disponibili.

---

## Funzionalità
- Rileva la mano tramite webcam in tempo reale.
- Conta quante dita sono alzate.
- Assegna un comando in base al numero di dita:
  - 1 dito → AVANTI
  - 2 dita → DESTRA
  - 3 dita → SINISTRA
  - 4 dita → DIETRO
  - 5 dita → FERMO
- Mostra il comando rilevato in alto e una barra informativa in basso con colori diversi per ogni comando.
- Disegna la mano rilevata sul video.

---

## Requisiti
- Python 3.7 o superiore
- Librerie Python:
  - `opencv-python`
  - `mediapipe`

---

#Librerie
## 1. Creare un ambiente virtuale (opzionale ma consigliato)
Un ambiente virtuale ti permette di isolare le librerie del progetto dal resto del sistema.

```bash
pip install opencv-python mediapipe
```
oppure
```bash
pip3 install opencv-python mediapipe
```
