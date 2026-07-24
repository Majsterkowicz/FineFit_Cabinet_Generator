import json
import os
import tempfile
from pathlib import Path


def atomic_write_json(path, data) -> None:
    """
    Zapisuje dane jako JSON atomowo.

    Plik tymczasowy powstaje w tym samym katalogu i zastępuje docelowy
    jednym os.replace, więc plik docelowy nigdy nie pozostaje w stanie
    częściowo zapisanym. Wspólne dla projektów i ustawień.
    """

    path = Path(path)

    descriptor, temporary_path = tempfile.mkstemp(
        dir=path.parent,
        suffix=".tmp"
    )

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        os.replace(temporary_path, path)

    except BaseException:
        Path(temporary_path).unlink(missing_ok=True)
        raise
