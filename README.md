# DailyPri

Privater Podcast-Feed für ein tägliches Morgen-Briefing (nur öffentliche Quellen).

- Podcast-Seite: https://apri69.github.io/DailyPri/
- Feed: https://apri69.github.io/DailyPri/feed.xml

## Neue Folge veröffentlichen

```bash
bash folge-hochladen.sh /pfad/zur/folge.mp3
```

Das Skript legt die Datei als `JJJJ-MM-TT.mp3` (Datum Europe/Berlin) in den Zweig `gh-pages`,
löscht Folgen älter als 7 Tage, baut `feed.xml` und `index.html` neu und schreibt `gh-pages`
als **einen** Commit ohne Geschichte (Force-Push). So wächst das Repo nicht.

Danach steht die Folge unter `https://apri69.github.io/DailyPri/JJJJ-MM-TT.mp3`
(GitHub Pages braucht nach dem Push etwa 1 Minute).
