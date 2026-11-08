#!/usr/bin/env python3
"""Erzeugt aus veranstaltungen.yaml zwei Kalenderdateien für ein Jahr.

  <jahr>.ics          Termine mit Status "bestätigt" oder "berechnet"
  <jahr>-pruefen.ics  Erinnerungen "Termin prüfen" für offene/geschätzte Termine
                      plus Platzhalter "(?)" für geschätzte Termine mit Datum

Aufruf:  python3 kalender.py [jahr]      (Standard: nächstes Jahr)
"""
import datetime as dt
import hashlib
import sys
from pathlib import Path

import yaml

HIER = Path(__file__).parent
MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli",
          "August", "September", "Oktober", "November", "Dezember"]


def esc(text):
    return (str(text).replace("\\", "\\\\").replace(";", "\\;")
            .replace(",", "\\,").replace("\n", "\\n"))


def fold(zeile):
    """Zeilen nach RFC 5545 auf 75 Bytes umbrechen."""
    raw = zeile.encode("utf-8")
    if len(raw) <= 75:
        return zeile
    teile, aktuell = [], b""
    for ch in zeile:
        b = ch.encode("utf-8")
        if len(aktuell) + len(b) > (75 if not teile else 74):
            teile.append(aktuell.decode("utf-8"))
            aktuell = b""
        aktuell += b
    teile.append(aktuell.decode("utf-8"))
    return "\r\n ".join(teile)


def ereignis(uid_basis, titel, von, bis=None, beschreibung="", ort="", link="", vorlaeufig=False):
    bis = bis or von
    uid = hashlib.sha1(uid_basis.encode()).hexdigest()[:16] + "@logbuch-veranstaltungen"
    zeilen = [
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}",
        f"DTSTART;VALUE=DATE:{von:%Y%m%d}",
        f"DTEND;VALUE=DATE:{bis + dt.timedelta(days=1):%Y%m%d}",
        f"SUMMARY:{esc(titel)}",
        "TRANSP:TRANSPARENT",
        f"STATUS:{'TENTATIVE' if vorlaeufig else 'CONFIRMED'}",
    ]
    if ort:
        zeilen.append(f"LOCATION:{esc(ort)}")
    if link:
        zeilen.append(f"URL:{link}")
    if beschreibung:
        zeilen.append(f"DESCRIPTION:{esc(beschreibung)}")
    zeilen.append("END:VEVENT")
    return zeilen


def kalender(name, events):
    zeilen = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//logbuch//veranstaltungen//DE",
              "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{esc(name)}"]
    for e in events:
        zeilen += e
    zeilen.append("END:VCALENDAR")
    return "\r\n".join(fold(z) for z in zeilen) + "\r\n"


def datum(wert):
    if isinstance(wert, dt.date):
        return wert
    return dt.date.fromisoformat(str(wert)) if wert else None


def main():
    jahr = int(sys.argv[1]) if len(sys.argv) > 1 else dt.date.today().year + 1
    eintraege = yaml.safe_load((HIER / "veranstaltungen.yaml").read_text(encoding="utf-8"))

    termine, pruefen = [], []
    for v in eintraege:
        t = (v.get("termine") or {}).get(jahr) or {"status": "offen"}
        status = t.get("status", "offen")
        von, bis = datum(t.get("von")), datum(t.get("bis"))
        name, ort, link = v["name"], v.get("ort", ""), v.get("link", "")
        info = [x for x in (v.get("regel"), v.get("ungefähr"), v.get("notiz"), t.get("quelle")) if x]

        if status in ("bestätigt", "berechnet") and von:
            text = "\n".join(info)
            if status == "berechnet":
                text = "Aus der Regel berechnet – noch nicht offiziell bestätigt.\n" + text
            termine.append(ereignis(f"{name}|{jahr}", name, von, bis, text, ort, link,
                                    vorlaeufig=status == "berechnet"))

        elif status in ("offen", "geschätzt"):
            monat = v.get("pruefen_ab")
            if monat in MONATE:
                m = MONATE.index(monat) + 1
                # Prüfmonat liegt nach dem üblichen Termin -> im Vorjahr prüfen
                ueblich = v.get("monat")
                j = jahr - 1 if ueblich in MONATE and m > MONATE.index(ueblich) + 1 else jahr
                pruefen.append(ereignis(
                    f"{name}|{jahr}|pruefen", f"Termin prüfen: {name} {jahr}",
                    dt.date(j, m, 1), beschreibung="\n".join(info), link=link))
            if status == "geschätzt" and von:
                pruefen.append(ereignis(
                    f"{name}|{jahr}|schaetzung", f"{name} (?)", von, bis,
                    "Geschätzter Termin – noch nicht bestätigt.\n" + "\n".join(info),
                    ort, link, vorlaeufig=True))

    (HIER / f"{jahr}.ics").write_text(
        kalender(f"Veranstaltungen {jahr}", termine), encoding="utf-8", newline="")
    (HIER / f"{jahr}-pruefen.ics").write_text(
        kalender(f"Veranstaltungen {jahr} – prüfen", pruefen), encoding="utf-8", newline="")
    print(f"{jahr}.ics: {len(termine)} Termine, {jahr}-pruefen.ics: {len(pruefen)} Einträge")


if __name__ == "__main__":
    main()
