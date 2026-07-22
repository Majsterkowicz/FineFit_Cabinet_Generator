# Architecture

FineFit Cabinet Engine
│
├── Projects
├── Models
├── Generators
├── Exporters
├── Validators
└── Outputs

# FineFit Cabinet Engine - Architecture

## 1. Cel projektu

FineFit Cabinet Engine jest silnikiem do projektowania oraz technologicznego przygotowania mebli na wymiar.

Projekt rozwijany jest zgodnie z architekturą Domain Driven Design (DDD), gdzie modele domenowe są oddzielone od logiki biznesowej oraz interfejsu użytkownika.

---

# 2. Struktura projektu

src/

    core/
        logika działania programu

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

---

# 3. Modele domenowe

Project

Section

Cabinet

W przyszłości:

Part

Front

Hardware

Material

Edge

Board

---

# 4. Identyfikatory

Każdy obiekt posiada niezmienne ID systemowe.

Format:

PXXX-EYYY

Przykład:

P015-E001

ID:

- jest unikalne,
- nigdy nie jest ponownie wykorzystywane,
- służy do powiązań pomiędzy obiektami.

---

# 5. Oznaczenia robocze

Program przechowuje również oznaczenia technologiczne.

Przykład:

1.1

1.2

2.3

Oznaczenia mogą ulegać zmianie.

ID systemowe pozostaje niezmienne.

---

# 6. Numeracja elementów

Za tworzenie identyfikatorów odpowiada wyłącznie:

services/id_generator.py

Żaden inny moduł nie generuje własnych numerów.

---

# 7. Zasady modeli

Każdy model posiada:

to_dict()

from_dict()

Modele nie zapisują plików.

Modele nie komunikują się z użytkownikiem.

---

# 8. Zasady Services

Services realizują logikę biznesową.

Przykłady:

ProjectManager

IdGenerator

W przyszłości:

PartGenerator

BOMGenerator

PricingEngine

ReportGenerator

---

# 9. UI

Warstwa UI odpowiada wyłącznie za komunikację z użytkownikiem.

Nie zawiera logiki biznesowej.

---

# 10. Roadmap

v0.8.x

Budowa silnika projektowania.

v0.9.x

Generator formatek.

v1.0

Pierwsza kompletna technologia wykonania mebla.

---

# Wizards

Workspace nigdy nie tworzy modeli domenowych bezpośrednio.

Każdy Workspace uruchamia odpowiedni Wizard.

Wizard:

- pobiera dane od użytkownika,
- wyświetla podsumowanie,
- tworzy kompletny model domenowy,
- zwraca gotowy obiekt.

Workspace:

- dodaje obiekt do projektu,
- zapisuje projekt,
- zarządza nawigacją.