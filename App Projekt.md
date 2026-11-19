- App (sowohl WebApp, als auch später Smartphone App), die Ziele definiert, Wochen plant und Tage strukturiert!
	- für WebApp: soll in Docker Container eines Servers laufen und auf diesem Server soll auch die Datenbank laufen, auf der auch die Smartphone App zugreift, soll mit python Programmiert sein. (geeignetes Framework = django?)
- soll umfassen:
	- **Daily Dashboard**, das den Nutzer fortan durch jeden Tag begleiten wird.
	- **Zielsetzung**, Methodik, um ambitionierte Ziele zu setzen und herunterzubrechen
	- **Weekly Review**, mit der der Nutzer jede Woche deinen Fortschritt bewertet und ggf. den Kurs korrigiert
	- **Dokumente-Verzeichnis**, in dem man Notizen sowie Bücher, Filme, Podcasts und ähnliche Medien ablegt
	- ein **Tagebuch** für tägliches Journaling und Morgenroutine
	-  **Habit Tracker**, damit man James Clear stolz machen und gute Angewohnheiten entwickeln kannst
	- Den **Fitness-Tracker** für den Traumkörper 
	- einen **Schulplaner**, bei dem man Fächer, Themen und Übungsblätter integrieren kann

**NutzerAccount:** 
- Name, Vorname, Geburtstag, Größe, Gewicht

**Jeder Tag**
- eine Instanz - wird jeden Tag erzeugt
	- Morgenroutine, Abendroutine, (Checkboxen, zum Beispiel "Liegestütze" oder "Wasser getrunken") definiert der Nutzer selbst
	- Tagebuch - Nutzer schreibt Text jeden Tag in die TagesInstanz
- andere Tage können angeschaut werden

**Zielsetzung**
- Nutzer definiert höchstens 3 Jahresziele
	- Jedes Jahresziel wird eindeutig per Text definiert (Beispiel: Sportlich werden = 100 Liegestütze am Stück schaffen; Seit 1 Monat durchgängig in das Gym gehen)
- pro Ziel 3 Meilensteine
- pro Meilenstein mehrere Projekte
	- man definiert Das Enddatum eines Projektes, wann man fertig sein will
- TODO Liste
	- TODO mit Enddatum und Beschreibung
	- TODO kann einem Projekt zugeordnet werden
- jede Woche: Weekly Review 
	- Übersicht über erfüllte DailyHabits, abhaken von Weekly Habits
	- "Zoom out":Übersicht über erfüllte Projekte und welcher Prozentsatz die Meilensteine haben, Übersicht, wann die Projekte fertig sein sollen (Kalenderansicht)
	- Text aufschreiben: "Was war gut? Was könnte diese Woche besser sein?"
	- "Notizen in Projekte verwandeln oder archivieren? Irgendwas favorisieren oder neu kategorisieren?"
	- jedes Weekly review checken:
		- "Sind alle Zahlen aktuell? Sind die aktiven Projekte wirklich die wichtigsten?" (Jahresziele, Meilensteine, Projekte)
	- "Zoom in": Welche Projekte verfolge ich diese Woche?, welche habe ich letzte Woche verfolgt?
	- Review Wochenziel erreicht? Warum ja, warum nein?
	- Fitness Übersicht: was habe ich letzte Woche trainiert? Wieviel Kalorien, Wieviel Proteine?
		- Alle 3 Monate Muskelkraft messen (erst ab Januar 2027)

**FitnessTracker**
- Jeden Tag: Eintragen, welche Übung man gemacht hat, wieviele Wiederholungen und welches Gewicht
- Übungen sollen je auch eine Instanz sein, die man "Wiederverwenden" kann (nicht jedes mal manuell "Latzug" eintragen)
	- Vergleichbarkeit zwischen verschiedenen Tagen (wie habe ich mich verbessert?)
	- Gerätenummer identifiziert Gerät eindeutig, Übung, wie zum Beispiel "Liegestütze" haben keine Gerätenummer, sollen aber trotzdem ID haben
	- Jede Übung hat Kategorien: Beine, Brust, Bizeps, Trizeps, Rücken, Schulter
	- Jeden Tag auswählen: "Heute trainiere ich beine und Brust" (Checkboxen) und dann Auflistung von gespeicherten Übungen, die man dann auch auswählt (mehrere Checkboxen), dann jeweils eintragen wieviel Wiederholungen man geschafft hat und vieviel Gewicht
- Essen Tracken, Wieviele Proteine, wieviel Kalorien, kann Rezept zugeordnet werden (Dokument)

**Dokumente**
- verschiedene Typen
	- Buch, Film, Rezept, Notizen, Podcasts, Artikel, Computerspiele
	- Man kann sie als Favoriten markieren, Sie bewerten und einen Text schreiben (Kommentieren) und eine URL anhängen, ggf. "Genre"
	- Status: schon gelesen/ geschaut (konsumiert), Liste zu "konsumierend"
	- Bild anhängen (zum Beispiel Buchcover), sodass es Übersichtlich wird
- Notizen sind einfach "spontane Ideen", die im WeeklyReview zu Projekten umgewandelt werden können oder gelöscht werden

**Habits/ Habittracker**
- werden vom Nutzer definiert und deren Einhaltung wird dokumentiert und getrackt (höchstens 5)
- Weekly Habits
- Daily Habits

**Finanztracker**

- Name der Ausgabe (Netflix, usw.), Tag ("Unterhaltung"), Höhe (10 €), Zeit (18.10.2026 10:30), Kategorie: Fixkosten, Ausgaben, Einnahmen
- soll später noch erweitert werden (Finanzguru ähnlich)
