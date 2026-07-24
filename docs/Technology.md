# Technology

## Hierarchia obiektów

```
Projekt (P)
└── Sekcja (S)
    └── Szafka (C)
        └── Formatka (P)
```

## Identyfikatory systemowe

Niezmienne, unikalne, nigdy nie wykorzystywane ponownie:

```
P020-S001   sekcja
P020-C001   szafka
P020-P001   formatka
```

## Numeracja technologiczna

Numeracja robocza, może się zmieniać po dodaniu lub usunięciu obiektu.
ID systemowe pozostaje niezmienne.

```
1           sekcja
1.1         szafka (sekcja 1, szafka 1)
1.1.1       formatka (sekcja 1, szafka 1, formatka 1)
```

Za nadawanie ID oraz numeracji odpowiada wyłącznie
`src/services/id_generator.py`.
