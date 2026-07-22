# FineFit Cabinet Engine

Wersja: v0.9.0

## Cel

Silnik do projektowania oraz technologicznego przygotowania mebli na wymiar.

> Projektant podejmuje decyzje projektowe, program odpowiada za zadania
> powtarzalne, techniczne oraz podatne na błędy.

## Uruchomienie

Projekt korzysta z `uv`.

### Interfejs graficzny (zalecany)

```bash
uv run uvicorn src.api.app:app --reload
```

Następnie: http://127.0.0.1:8000

Dokumentacja API: http://127.0.0.1:8000/docs

### Interfejs tekstowy (CLI)

```bash
uv run python main.py
```

Oba interfejsy korzystają z tych samych usług i zapisują do tych samych
plików `projects/*/project.json`.

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
