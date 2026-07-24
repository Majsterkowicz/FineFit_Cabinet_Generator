# FineFit Cabinet Engine

Wersja: v0.10.1

## Cel

Silnik do projektowania oraz technologicznego przygotowania mebli na wymiar.

> Projektant podejmuje decyzje projektowe, program odpowiada za zadania
> powtarzalne, techniczne oraz podatne na błędy.

## Uruchomienie

### Wymagania

- **Python 3.10 lub nowszy** (zdefiniowane w `pyproject.toml`).
- **[uv](https://docs.astral.sh/uv/)** — menedżer środowisk i zależności
  używany przez projekt. Instalacja:

  ```bash
  # Linux / macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

  Pełna instrukcja instalacji: https://docs.astral.sh/uv/getting-started/installation/

### Instalacja zależności

Z katalogu głównego projektu:

```bash
uv sync
```

Komenda tworzy wirtualne środowisko `.venv/` i instaluje zależności zgodnie
z plikiem `uv.lock`. Nie trzeba ręcznie aktywować środowiska — `uv run`
używa go automatycznie.

### Interfejs graficzny (zalecany)

```bash
uv run uvicorn src.api.app:app --reload
```

Następnie: http://127.0.0.1:8000

Dokumentacja API: http://127.0.0.1:8000/docs

Flaga `--reload` automatycznie przeładowuje serwer po zmianach w kodzie
(przydatne przy pracy nad projektem).

### Interfejs tekstowy (CLI)

```bash
uv run python main.py
```

Oba interfejsy korzystają z tych samych usług i zapisują do tych samych
plików `projects/*/project.json`.

### Rozwiązywanie problemów

**`Failed to spawn: uvicorn` / `No such file or directory`**

Środowisko `.venv/` jest nieaktualne (np. po przeniesieniu katalogu projektu
skrypty w `.venv/bin/` wskazują na starą ścieżkę Pythona). Odtwórz środowisko:

```bash
rm -rf .venv && uv sync
```

### Testy

```bash
uv run pytest
```

### Inne ścieżki

```bash
# katalog projektów
FINEFIT_PROJECTS_DIR=/sciezka/do/projektow uv run uvicorn src.api.app:app

# plik ustawień globalnych (domyślnie settings.json w katalogu głównym)
FINEFIT_SETTINGS_FILE=/sciezka/do/settings.json uv run uvicorn src.api.app:app
```

## Co program potrafi

- projekty, sekcje, szafki wraz z zapisem do JSON,
- pełna edycja: dodawanie, zmiana nazwy i usuwanie (projekty, sekcje, szafki),
- automatyczne generowanie formatek (bok, wieniec, półka, plecy, front),
- listę rozkroju z podsumowaniem powierzchni i długości obrzeża,
- eksport listy rozkroju do CSV,
- rysunek elewacji sekcji (SVG),
- automatyczną numerację technologiczną z przeliczaniem po usunięciu,
- orientacyjną wycenę (materiały, obrzeże, okucia),
- **arkusz produkcyjny (Drukuj / PDF)** — elewacje, lista rozkroju, BOM
  oraz wycena na jednej drukowalnej stronie,
- **ustawienia globalne** edytowalne w interfejsie (konstrukcja, materiały,
  ceny domyślne, typy szafek).

Ten sam zestaw operacji dostępny jest w interfejsie tekstowym (CLI) i w API.

## Ustawienia i ceny

Wartości fabryczne pochodzą z `src/config.py`. Przy pierwszym zapisie z UI
powstaje `settings.json` (konstrukcja, materiały, ceny, typy szafek) — od tego
momentu ustawienia są edytowalne bez zmian w kodzie.

Ceny konkretnego projektu to **migawka** ustawień z chwili jego utworzenia,
zapisana w `project.json`. Późniejsza zmiana ustawień globalnych nie zmienia
istniejących wycen; ceny projektu można edytować osobno.

## Struktura

```
src/
    api/          REST API (FastAPI)
    core/         interfejs tekstowy - workspaces, wizards
    models/       modele domenowe
    services/     logika biznesowa (m.in. settings_manager, project_manager)
    generators/   generatory technologiczne (part, bom, pricing)
web/              frontend (bez etapu budowania)
projects/         dane projektów
tests/            testy (pytest)
settings.json     ustawienia globalne (tworzone przy pierwszym zapisie)
docs/             dokumentacja
```

Szczegóły w `docs/Architecture.md`.
