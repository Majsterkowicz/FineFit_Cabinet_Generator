# FineFit Cabinet Engine - Architecture

---

# 1. Cel projektu

FineFit Cabinet Engine jest silnikiem do projektowania oraz technologicznego przygotowania mebli na wymiar.

Projekt rozwijany jest zgodnie z architekturą Domain Driven Design (DDD), gdzie modele domenowe są oddzielone od logiki biznesowej oraz interfejsu użytkownika.

Podstawową zasadą projektu jest:

> Projektant podejmuje decyzje projektowe, natomiast program odpowiada za wszystkie zadania powtarzalne, techniczne oraz podatne na błędy.

---

# 2. Struktura projektu

```
src/

    core/
        interfejs tekstowy (CLI)
        workspaces, wizards, prompt

    models/
        modele domenowe

    services/
        usługi biznesowe

    generators/
        generatory technologiczne

    api/
        REST API (FastAPI)

web/
    interfejs przeglądarkowy

docs/
    dokumentacja projektu
```

---

# 3. Modele domenowe

Obecne modele:

- Project
- Section
- Cabinet
- Part

Planowane modele:

- Front
- Hardware
- Material
- Edge
- Board

Każdy model odpowiada wyłącznie za przechowywanie danych.

---

# 4. Identyfikatory systemowe

Każdy obiekt posiada niezmienne ID systemowe.

Przykłady:

```
P020-S001
P020-C001
P020-F001
P020-P001
```

gdzie:

- P - Project
- S - Section
- C - Cabinet
- F - Front
- P - Part

ID systemowe:

- jest unikalne,
- nigdy nie ulega zmianie,
- nigdy nie jest ponownie wykorzystywane,
- służy do powiązań pomiędzy obiektami.

---

# 5. Numeracja technologiczna

Niezależnie od ID systemowego program przechowuje numerację technologiczną.

Przykłady:

Sekcje

```
1
2
3
```

Szafki

```
1.1
1.2
2.1
2.2
```

Numeracja technologiczna może ulegać zmianie.

ID systemowe pozostaje niezmienne.

---

# 6. Generowanie numeracji

Za tworzenie:

- ID systemowych,
- numeracji technologicznej

odpowiada wyłącznie:

```
src/services/id_generator.py
```

Żaden inny moduł nie generuje własnych numerów.

Numeracja technologiczna jest zarządzana przez system.

Program:

- wyznacza kolejny numer,
- gwarantuje jego unikalność,
- zachowuje kolejność numeracji.

Użytkownik odpowiada wyłącznie za opis obiektu
(np. nazwę sekcji).

---

# 7. Modele domenowe

Każdy model posiada:

- to_dict()
- from_dict()

Modele:

- nie zapisują plików,
- nie komunikują się z użytkownikiem,
- nie zawierają logiki biznesowej.

---

# 8. Services

Services realizują logikę biznesową projektu.

Obecne:

- ProjectManager - zapis i odczyt projektów
- IdGenerator - numeracja systemowa i technologiczna
- SectionService - operacje na sekcjach
- CabinetService - operacje na szafkach

Generators wyliczają technologię wykonania.

Obecne:

- PartGenerator - formatki korpusu
- BomGenerator - lista rozkroju

Planowane:

- FrontGenerator
- MaterialGenerator
- PricingEngine
- ReportGenerator

Podział:

- Service tworzy i modyfikuje modele domenowe,
- Generator wylicza dane wynikowe z gotowego modelu,
- IdGenerator wyłącznie nadaje numery i nie tworzy modeli.

---

# 9. Workspaces i Wizards

Workspace nigdy nie tworzy modeli domenowych bezpośrednio.

Schemat działania:

```
Workspace

↓

Wizard

↓

Service

↓

Model

↓

Workspace

↓

ProjectManager.save()
```

### Wizard

Wizard odpowiada za:

- pobranie danych od użytkownika,
- sprawdzenie poprawności formatu (liczba, pusty tekst),
- wyświetlenie podsumowania,
- zlecenie utworzenia modelu usłudze,
- zwrócenie gotowego obiektu.

Wizard nie zapisuje projektu i nie tworzy modeli samodzielnie.

---

### Workspace

Workspace odpowiada za:

- uruchamianie Wizardów,
- dodawanie obiektów do projektu,
- zapis projektu,
- nawigację pomiędzy ekranami.

Workspace nie tworzy modeli domenowych.

---

# 10. Warstwa UI

Program posiada dwa interfejsy:

- CLI (`src/core/`) - workspaces oraz wizards,
- Web (`src/api/` + `web/`) - REST API oraz frontend.

Żaden z nich nie zawiera logiki biznesowej.

Oba korzystają z tych samych usług:

```
CLI Wizard  ─┐
             ├─→ Service ─→ Generator ─→ Model ─→ ProjectManager.save()
REST API    ─┘
```

Wizard pobiera dane od użytkownika i przekazuje je do usługi.
API waliduje dane wejściowe (Pydantic) i przekazuje je do tej samej usługi.

Reguła: logika, która musi działać w obu interfejsach,
nigdy nie znajduje się w Wizardzie.

---

# 11. Standard działania kreatorów

Każdy Wizard powinien posiadać identyczny przebieg.

1. Wyświetlenie nagłówka.

2. Wyświetlenie istniejących obiektów.

3. Wyświetlenie obiektu, który będzie tworzony.

4. Pobranie danych od użytkownika.

5. Wyświetlenie podsumowania.

6. Potwierdzenie:

```
ENTER - zapisz
N - anuluj
```

7. Utworzenie modelu.

8. Zwrot gotowego obiektu.

9. Workspace zapisuje projekt.

---

# 12. Walidacja

Walidacja wykonywana jest możliwie najwcześniej.

Podział odpowiedzialności:

- Wizard oraz schematy API sprawdzają format danych wejściowych,
- Service sprawdza reguły biznesowe i zgłasza ValueError,
- Service zgłasza LookupError, gdy obiekt nie istnieje.

Reguły biznesowe znajdują się wyłącznie w Services, dzięki czemu
CLI oraz API egzekwują dokładnie ten sam kontrakt.

API tłumaczy wyjątki na kody HTTP w jednym miejscu:
ValueError na 400, LookupError na 404.

Program nigdy nie tworzy modelu z niepoprawnymi danymi.

---

# 13. Roadmap

## v0.8.x

Budowa silnika projektu.

- Project Workspace
- Section Workspace
- Cabinet Workspace
- Wizards
- IdGenerator
- Architektura
- Walidacja

---

## v0.9.x

Silnik technologii.

- Cabinet Generator
- Part Generator
- Front Generator
- Material Generator
- BOM

---

## v1.0

Pierwsza kompletna technologia wykonania mebla.

- kompletna dokumentacja wykonawcza,
- BOM,
- eksport danych,
- przygotowanie produkcji.