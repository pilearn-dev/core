# Installationsanleitung

Um &pi;-Learn zu installieren, benötigst du eine Version von Python 3. Diese Anleitung ist für Python 3.5.2 erstellt, sollte aber auch für andere Versionen funktionieren.

Als erstes musst du &pi;-Learn von GitHub herunterladen:

```
$ mkdir pilearn
$ cd pilearn
$ git clone https://github.com/pilearn-dev/core.git .
```

Anschließend musst du die Abhängigkeiten installieren. Wahrscheinlich willst du dafür eine Virtuelle Umgebung nutzen. Sobald du diese betreten hast (oder, wenn du dies nicht möchtest), musst du diesen Kommandozeilenbefehl ausführen:

```
$ pip3 install -r requirements.txt
```

Nachfolgend musst du das Setup-Script ausführen und den Anweisungen folgen:

```
$ ./setup.py
```

Zuletzt kannst du den Entwicklungsserver starten, indem du folgenden Befehl ausführst:

```
$ ./pilearn.py
```

Eventuell erhältst du einen ImportError für `werkzeug.middleware`, was die Schuld von Flask zu sein scheint. Du musst dann die folgenden beiden Befehle ausführen:

```
$ pip uninstall werkzeug
$ pip install werkzeug==0.15
```

Außerdem solltest du einen cronjob für `jobs/badges.py` einrichen, der mindestens täglich läuft. In der Entwicklungsumgebung kannst du ihn auch manuell ausführen.