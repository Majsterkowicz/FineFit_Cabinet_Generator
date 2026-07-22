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
        logika działania programu
        workspaces
        wizards

    models/
        modele domenowe

    services/
        usługi biznesowe

    utils/
        funkcje pomocnicze

    ui/
        interfejs tekstowy (CLI)

docs/

    dokumentacja projektu
```

---

# 3. Modele domenowe

Obecne modele:

- Project
- Section
- Cabinet

Planowane modele:

- Part
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

- ProjectManager
- IdGenerator

Planowane:

- CabinetGenerator
- PartGenerator
- BOMGenerator
- PricingEngine
- ReportGenerator

Services mogą tworzyć modele domenowe.

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
- walidację danych,
- wyświetlenie podsumowania,
- utworzenie kompletnego modelu,
- zwrócenie gotowego obiektu.

Wizard nie zapisuje projektu.

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

Warstwa UI odpowiada wyłącznie za komunikację z użytkownikiem.

Nie zawiera logiki biznesowej.

Cała logika znajduje się w:

- Services
- Wizards
- Models

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

Za walidację odpowiada Wizard.

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