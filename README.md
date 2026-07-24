# FineFit Cabinet Engine

Wersja: v0.9.0

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

### Inny katalog projektów

```bash
FINEFIT_PROJECTS_DIR=/sciezka/do/projektow uv run uvicorn src.api.app:app
```

## Co program potrafi

- projekty, sekcje, szafki wraz z zapisem do JSON,
- automatyczne generowanie formatek (bok, wieniec, półka, plecy, front),
- listę rozkroju z podsumowaniem powierzchni i długości obrzeża,
- eksport listy rozkroju do CSV,
- rysunek elewacji sekcji (SVG),
- automatyczną numerację technologiczną z przeliczaniem po usunięciu.

## Struktura

```
src/
    api/          REST API (FastAPI)
    core/         interfejs tekstowy - workspaces, wizards
    models/       modele domenowe
    services/     logika biznesowa
    generators/   generatory technologiczne
web/              frontend (bez etapu budowania)
projects/         dane projektów
docs/             dokumentacja
```

Szczegóły w `docs/Architecture.md`.
