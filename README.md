# DetectSpeak

DetectSpeak est un programme Python qui utilise la reconnaissance vocale pour détecter le nombre de fois qu'un mot est
prononcé en temps réel. Le programme utilise l'API de reconnaissance vocale de Google pour reconnaître la parole et
affiche le nombre d'occurrences pour chaque mot à détecter.

## Installation

Cloner le dépôt GitHub.

Aller dans le répertoire detectspeak :

```bash
cd detectspeak
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Exécuter le programme :

```bash
python main.py
```

## Configuration

Les mots à détecter peuvent être configurés en modifiant le fichier mots.json. Ce fichier est un tableau JSON de chaînes
de caractères qui représentent les mots à détecter.

```json
[
  "hello",
  "world",
  "detect",
  "speak"
]
```
