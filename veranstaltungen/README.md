# Veranstaltungen

Sammlung jährlich wiederkehrender Veranstaltungen, auch solcher, deren Termin noch nicht feststeht.

| Datei | Inhalt |
|---|---|
| `veranstaltungen.yaml` | die Liste: Veranstaltungen mit Regel, Rhythmus und den Terminen pro Jahr |
| `2027.ics` | Kalender mit allen bestätigten und berechneten Terminen 2027 |
| `2027-pruefen.ics` | Erinnerungen „Termin prüfen“ und geschätzte Termine mit „(?)“ |
| `kalender.py` | erzeugt die beiden `.ics`-Dateien aus der Liste |

## Ablauf

1. Neue Veranstaltung oder neuen Termin in `veranstaltungen.yaml` eintragen.
   Sobald ein Termin offiziell ist: `von`/`bis` eintragen, `status: bestätigt`, `quelle:` dazu.
2. `python3 kalender.py 2027` ausführen. Das erzeugt `2027.ics` und `2027-pruefen.ics` neu.
3. Die `.ics`-Dateien in den Kalender importieren (oder später als Abo einbinden).

## Status

- **bestätigt**: vom Veranstalter veröffentlicht, kommt in den Kalender
- **berechnet**: aus einer festen Regel abgeleitet (z. B. „2. Sonntag im September“), kommt als vorläufig in den Kalender
- **geschätzt**: grob aus den Vorjahren abgeleitet, nur als „(?)“ im Prüf-Kalender
- **offen**: noch nichts bekannt, nur Erinnerung „Termin prüfen“
- **entfällt**: findet in dem Jahr nicht statt (z. B. Veranstaltungen, die nur alle 2 Jahre stattfinden)
