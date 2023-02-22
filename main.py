import speech_recognition as sr
import tkinter as tk
import json
import threading


# PyAudio

class MessageBox(tk.Tk):
    def __init__(self, message):
        super().__init__()
        self.title("Erreur")
        self.geometry("300x100")
        tk.Label(self, text=message).pack(padx=10, pady=10)
        tk.Button(self, text="OK", command=self.destroy).pack(padx=10, pady=10)


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Détection de parole en temps réel")

        # Vérifier la disponibilité du microphone
        microphones = sr.Microphone.list_microphone_names()
        if not microphones:
            raise Exception("Aucun microphone n'a été détecté")

        # Créer un objet de reconnaissance vocale
        self.r = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Ajouter la zone de texte pour afficher le texte reconnu
        self.textbox = tk.Text(self, height=10, width=50)
        self.textbox.pack(padx=10, pady=10)

        # Ajouter le bouton de démarrage de l'enregistrement
        start_button = tk.Button(self, text="Démarrer l'enregistrement", command=self.start_recording)
        start_button.pack(padx=10, pady=10)

        # Ajouter le bouton d'arrêt de l'enregistrement
        stop_button = tk.Button(self, text="Arrêter l'enregistrement", command=self.stop_recording, state=tk.DISABLED)
        stop_button.pack(padx=10, pady=10)

        # Ajouter l'étiquette de sortie pour afficher le nombre d'occurrences
        self.output_label = tk.Label(self, text="")
        self.output_label.pack(padx=10, pady=10)

        # Charger les mots à détecter à partir du fichier JSON
        with open("mots.json", "r") as f:
            self.mots = json.load(f)

        self.recording_thread = None

    def show(self):
        self.mainloop()

    def start_recording(self):
        # Désactiver le bouton de démarrage et activer le bouton d'arrêt
        self.textbox.delete("1.0", tk.END)
        self.output_label.config(text="")
        self.recording_thread = threading.Thread(target=self.detect)
        self.recording_thread.start()
        self.after(100, self.update_progressbar)
        self.progressbar_start_time = self.r.get_current_time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

    def stop_recording(self):
        # Arrêter le thread de détection
        self.recording_thread.join()
        # Désactiver le bouton d'arrêt et activer le bouton de démarrage
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

        # Enregistrer le texte reconnu dans un fichier
        filename = "enregistrement.wav"
        with open(filename, "wb") as f:
            f.write(self.audio.get_wav_data())

        # Utiliser la reconnaissance vocale pour compter le nombre d'occurrences de chaque mot
        result = {}
        with sr.AudioFile(filename) as source:
            audio_data = self.r.record(source)
            text = self.r.recognize_google(audio_data, language="fr-FR")
            for mot in self.mots:
                occurrences = text.count(mot)
                if occurrences > 0:
                    result[mot] = occurrences

        # Afficher le résultat dans l'étiquette de sortie
        output_text = ""
        for mot, occurrences in result.items():
            output_text += f"{mot}: {occurrences}\n"
        self.output_label.config(text=output_text)

    def update_progressbar(self):
        # Mettre à jour la barre de progression
        elapsed_time = self.r.get_current_time() - self.progressbar_start_time
        if elapsed_time < self.record_seconds * 1000:
            self.progressbar["value"] = elapsed_time / (self.record_seconds * 10)
            self.after(100, self.update_progressbar)
        else:
            self.progressbar["value"] = 100

    def detect(self):
        with self.microphone as source:
            self.r.adjust_for_ambient_noise(source)
            self.audio = self.r.listen(source, phrase_time_limit=self.record_seconds)

        try:
            text = self.r.recognize_google(self.audio, language="fr-FR")
            self.textbox.insert(tk.END, text)
        except:
            pass

        self.after(100, self.detect)


if __name__ == "__main__":
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        MessageBox(str(e)).mainloop()
