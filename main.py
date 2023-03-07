import speech_recognition as sr, tkinter as tk, json, threading, os, time


# PyAudio

class MessageBox(tk.Tk):
    def __init__(self, message):
        super().__init__()
        self.title("Erreur")
        self.geometry("300x100")
        tk.Label(self, text=message).pack(padx=10, pady=10)
        tk.Button(self, text="OK", command=self.destroy).pack(padx=10, pady=10)


class MainWindow(tk.Tk):
    Name_of_the_file_to_save_the_counter: str = "counter.json"
    Name_of_the_file_to_read_the_words_to_detect: str = "mots.json"

    def __init__(self) -> None:
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

        # Ajouter le bouton de comptage
        count_button = tk.Button(self, text="Compter", command=self.update)
        count_button.pack(padx=10, pady=10)

        # Ajouter l'étiquette d'information pour afficher les messages d'erreur
        self.info_label = tk.Label(self, text="")
        self.info_label.pack(padx=10, pady=10)

        # Ajouter l'étiquette de sortie pour afficher le nombre d'occurrences
        self.output_label = tk.Label(self, text="")
        self.output_label.pack(padx=10, pady=10)

        # Ajouter l'étiquette de sortie pour afficher le nombre d'occurrences des 3 mots les plus utilisés
        self.output_label_3 = tk.Label(self, text="")
        self.output_label_3.pack(padx=10, pady=10)

        self.counter: dict = {}

        # Charger les mots à détecter à partir du fichier JSON
        try:
            with open(self.Name_of_the_file_to_read_the_words_to_detect, "r", encoding="utf-8") as f:
                self.mots: list = json.load(f)
        except FileNotFoundError:
            MessageBox("Le fichier mots.json n'a pas été trouvé").mainloop()

        for mot in self.mots:
            self.counter[mot] = 0

        self.stop: bool = True
        self.thread: threading.Thread = None
        self.thread_C: threading.Thread = None
        self.thread_C_All_Words: threading.Thread = None
        self.thread_C_3_Words: threading.Thread = None

    def show(self):
        self.mainloop()

    def start_recording(self) -> None:
        self.stop: bool = False

        # Désactiver le bouton de démarrage
        self.children["!button"].config(state=tk.DISABLED)

        # Activer le bouton d'arrêt
        self.children["!button2"].config(state=tk.NORMAL)

        # Démarrer un thread pour l'enregistrement
        self.thread = threading.Thread(target=self.recorder)
        self.thread.start()

        # Démarrer un thread pour le comptage
        self.thread_C = threading.Thread(target=self.update_counter_auto)
        self.thread_C.start()

        # Démarrer un thread pour le comptage de tous les mots
        self.thread_C_All_Words = threading.Thread(target=self.counter_json_file_all_words_auto)
        self.thread_C_All_Words.start()

        # Démarrer un thread pour le comptage des 3 mots les plus utilisés
        self.thread_C_3_Words = threading.Thread(target=self.counter_json_file_3_words_affichage_auto)
        self.thread_C_3_Words.start()

    def stop_recording(self) -> None:
        # Arrêter l'enregistrement
        self.stop: bool = True

        # Activer le bouton de démarrage
        self.children["!button"].config(state=tk.NORMAL)

        # Désactiver le bouton d'arrêt
        self.children["!button2"].config(state=tk.DISABLED)

    def recorder(self) -> None:
        # Enregistrer le texte reconnu
        with self.microphone as source:
            self.r.adjust_for_ambient_noise(source)
            while not self.stop:
                self.info_label.config(text="Enregistrement en cours...")
                audio = self.r.listen(source)
                try:
                    text = self.r.recognize_google(audio, language="fr-FR")
                    self.textbox.insert(tk.END, text + "\n")
                    self.textbox.see(tk.END)
                except sr.UnknownValueError:
                    self.info_label.config(text="Le texte n'a pas pu être reconnu")
                    pass
                except sr.RequestError as e:
                    self.info_label.config(text="Erreur de connexion : " + str(e))
                    MessageBox(str(e)).mainloop()
                    break
                else:
                    self.info_label.config(text="Enregistrement terminé")

        self.info_label.config(text="")

    def count(self) -> None:
        for mot in self.mots:
            self.counter[mot] = 0

        txt: str = self.textbox.get("1.0", tk.END)
        txt = txt.lower()

        for mot in self.mots:
            self.counter[mot] = txt.count(mot)

    def update_counter_affichage(self) -> None:
        self.output_label.config(text=f"Nombre d'occurrences: {self.counter}")

    def update_counter(self) -> None:
        self.count()
        self.update_counter_affichage()

    def update_counter_auto(self) -> None:
        while not self.stop:
            self.update_counter()

    def update_counter_all_words(self) -> dict:
        txt: str = self.textbox.get("1.0", tk.END)
        txt = txt.lower()
        list_txt: list = txt.split()
        Total_Counter: dict = {}
        Done_words: list = []
        for mot in list_txt:
            if mot not in Done_words:
                Done_words.append(mot)
                Total_Counter[mot] = txt.count(mot)
        return Total_Counter

    def counter_json_file_all_words(self) -> None:
        if not os.path.exists(self.Name_of_the_file_to_save_the_counter):
            with open(self.Name_of_the_file_to_save_the_counter, "w", encoding="utf-8") as f:
                f.write("{}")
        with open("counter.json", "w", encoding="utf-8") as f:
            json.dump(self.update_counter_all_words(), f, indent=4)

    def counter_json_file_all_words_auto(self) -> None:
        while not self.stop:
            self.counter_json_file_all_words()

    def counter_json_file_3_words(self) -> dict:
        Third_Most_Used_Word: dict = {}
        try:
            with open(self.Name_of_the_file_to_save_the_counter, "r", encoding="utf-8") as f:
                Counter: dict = json.load(f)
        except FileNotFoundError:
            pass
        except json.decoder.JSONDecodeError:
            pass
        except Exception as e:
            pass
        else:
            for word in Counter:
                if len(Third_Most_Used_Word) < 3:
                    Third_Most_Used_Word[word] = Counter[word]
                else:
                    for word2 in Third_Most_Used_Word:
                        if Counter[word] > Third_Most_Used_Word[word2]:
                            Third_Most_Used_Word[word2] = Counter[word]
                            break
        return Third_Most_Used_Word

    def counter_json_file_3_words_affichage(self) -> None:
        self.output_label_3.config(text=f"Trois mots les plus utilisés: {self.counter_json_file_3_words()}")

    def counter_json_file_3_words_affichage_auto(self) -> None:
        while not self.stop:
            self.counter_json_file_3_words_affichage()
            time.sleep(1)

    def update(self) -> None:
        self.update_counter()
        self.counter_json_file_all_words()
        self.counter_json_file_3_words_affichage()


if __name__ == "__main__":
    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        MessageBox(str(e)).mainloop()
