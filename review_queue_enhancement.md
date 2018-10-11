# Der Moderationslistenerneuerungsprozess (*review queue enhancement progress*)

----

## 1. Teil - Standardflags

Um die neuen Moderationslisten zu ermöglichen, nutzen wir folgende Grundstruktur:

```
TABLE [xxx]_queue
  FIELD id :: INT+PRIMARY_KEY
  FIELD item_id :: INT
  FIELD state :: INT+SET
    SETITEM 0 := "pending"
    SETITEM 1 := "completed"
    SETITEM 2 := "deprecated"
  FIELD result :: INT+SET
    // SETITEMS DEPENDING ON QUEUE
END
```

**SQL:**
```sql
CREATE TABLE user_queue (id INTEGER PRIMARY KEY, item_id INT, state TINYINT, result INT)
```

```
TABLE [xxx]_reviews
  FIELD id :: INT+PRIMARY_KEY
  FIELD queue_id :: INT
  FIELD item_id :: INT
  FIELD reviewer_id :: INT
  FIELD result :: INT+SET
    // SETITEMS DEPENDING ON QUEUE
  FIELD comment :: TEXT
END
```

**SQL:**
```sql
CREATE TABLE user_reviews (id INTEGER PRIMARY KEY, queue_id INT, item_id INT, reviewer_id INT, result INT, comment TEXT)
```

### Ergebnisse von Moderationslisten

### Beiträge schließen `forum/closure_`
1. Überspringen
2. **[hilfreich]** - schließen
3. **[zurückgewiesen]** - bearbeiten
4. **[nicht hilfreich]** - nicht schließen
5. **[hilfreich]** - *(vom System, wenn Beitrag gelöscht)*
6. **[hilfreich]** - *(vom System, wenn Beitrag außerhalb der liste gesperrt)*

### Beiträge wieder öffnen `forum/reopen_`
1. Überspringen
2. **[hilfreich]** - öffnen
3. **[nicht hilfreich]** - geschlossen lassen
4. **[zurückgewiesen]** - *(vom System, wenn Beitrag gelöscht)*
5. **[hilfreich]** - *(vom System, wenn Beitrag außerhalb der Liste geöffnet.)*

### Beitragsmeldungen
1. Überspringen
2. **[hilfreich]** - löschen
3. **[hilfreich]** - ist gefährlich
4. **[zurückgewiesen]** - bearbeiten
5. **[nicht hilfreich]** - keine Probleme gefunden
6. **[zurückgewiesen]** - *(vom System, wenn Beitrag bearbeitet)*
7. **[hilfreich]** - *(vom System, wenn Beitrag gelöscht)*

----

Meldungen/Stimmen haben jetzt diese Struktur:

```
TABLE [xxx]_flags
  FIELD id :: INT+PRIMARY_KEY
  FIELD item_id :: INT
  FIELD queue_id :: INT
  FIELD state :: INT+SET
    SETITEM -2 := "not helpful"
    SETITEM -1 := "disputed"
    SETITEM 0 := "pending"
    SETITEM 1 := "helpful
    SETITEM 2 := "deprecated"
  FIELD flagger_id :: INT
  FIELD type :: VARCHAR(4)+SET
    SETITEM "vote"
    SETITEM "flag"
  FIELD reason :: VARCHAR(20)+SET
    // SETITEMS DEPENDING ON QUEUE
  FIELD comment :: TEXT
END
```

**SQL**:

```sql
CREATE TABLE user_flags (id INTEGER PRIMARY KEY, item_id INT, queue_id INT, state TINYINT, flagger_id INT, type VARCHAR(4), reason VARCHAR(20), comment TEXT)
```

----

## 2. Teil - Andere Meldungen
Um die neuen Moderationslisten zu ermöglichen, nutzen wir folgende Grundstruktur:

```
TABLE custom_flaglist
  FIELD id :: INT+PRIMARY_KEY
  FIELD item_id :: INT
  FIELD item_type :: VARCHAR(30)
  FIELD state :: INT+SET
    SETITEM 0 := "pending"
    SETITEM 1 := "completed"
  FIELD handler :: INT
END
```

**SQL:**

```sql
CREATE TABLE custom_flaglist (id INTEGER PRIMARY KEY, item_id INT, item_type VARCHAR(30), state TINYINT, handler INT)
```
Meldungen/Stimmen haben jetzt diese Struktur:

```
TABLE custom_flag
  FIELD id :: INT+PRIMARY_KEY
  FIELD item_id :: INT
  FIELD item_type :: VARCHAR(30)
  FIELD queue_id :: INT
  FIELD state :: INT+SET
    SETITEM -2 := "not helpful"
    SETITEM -1 := "disputed"
    SETITEM 0 := "pending"
    SETITEM 1 := "helpful
    SETITEM 2 := "deprecated"
  FIELD flagger_id :: INT
  FIELD comment :: TEXT
  FIELD response :: TEXT
END
```

**SQL:**

```sql
CREATE TABLE custom_flag (id INTEGER PRIMARY KEY, item_id INT, item_type VARCHAR(30), queue_id INT, state TINYINT, flagger_id INT, comment TEXT, response TEXT)
```


## 3. Teil- Ausschluss aus Standardflaglisten

Möglich für

a) Moderatoren in allen Foren-spezifischen Listen
b) Administratoren

```
TABLE [xxx]_reviewbans
  FIELD id :: INT+PRIMARY_KEY
  FIELD queue :: VARCHAR(25)
  FIELD user_id :: INT
  FIELD given_by :: INT
  FIELD cancelled_by :: INT
  FIELD start_date :: INT
  FIELD end_date :: INT
  FIELD invalidated :: TINYINT
  FIELD comment :: TEXT
END
```

**SQL:**

```sql
CREATE TABLE reviewbans (id INTEGER PRIMARY KEY, queue VARCHAR(25), user_id INT, given_by INT, cancelled_by INT, start_date INT, end_date INT, invalidated TINYINT, comment TEXT)
```


> Review ban statistics
> ```sql
SELECT COUNT(id), COUNT(invalidated), queue, given_by FROM reviewbans GROUP BY queue, given_by ORDER BY given_by<
   ```
> Format:
> Number of reviewbans, Number of invalidated bans, queue, given by
