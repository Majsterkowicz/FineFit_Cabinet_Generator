## v0.8.5

Dodanie interfejsu tworzenia szafek z szufladami oraz niezbędnym zestawem narzedzi do przeliczania rozmiarów formatek

- Dodanie nowej wersji szafki z szufladami
- Bazowy interfejs korpusu jest identyczny jak dla szafki stojącej
- Utworzenie  interfejsu do podziału frontów (wysokości)
- Program powinien pokazać nominalną wysokość frontów, czyli całkowitą wysokość korpusu
- Fronty są liczone zawsze od góry do dołu
- Podział frontów może odbywać się na dwa sposoby, dla przykładu frontów o nominalnej wysokości łącznie 800:
    - Podział ułamkowy, np. 1/4 + 1/4 + 1/2
    - Podział liczbowy, np. 200 + 200 + 400
- Interfesj powinien zadbać, aby na koniec wyświetlić wysokości frontów w przeliczeniu na milimetry.
- Jeżeli z podziały wynika, że wysokość nominalna frontu nie jest liczbą całkowitą, należy ją zaokrąglić w dół
- Interfejs powinien wyświetlić sumę wysokości nominalnych wszystkich frontów i porównać ją z wysokością korpusu
- Poprawny wynik tego porównania jest wtedy, gdy:
    - suma nominalnych wysokości frontów jest taka sama jak wysokość korpusu
    - suma nominalnych wysokości frontów jest mniejsza o 1 lub 2 niż wysokość korpusu
- Program musi wyświetlić komunikat w sytuacji, gdy suma nominalnych wysokości frontów jest większa od wysokości korpusu