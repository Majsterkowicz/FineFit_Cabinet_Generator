# CHANGELOG

## v0.10.0
- PricingEngine - orientacyjna wycena projektu (materiały, obrzeże, okucia)
  w API, interfejsie przeglądarkowym oraz CLI.
- Ustawienia globalne (settings.json) edytowalne w UI: konstrukcja,
  materiały i ceny domyślne, typy szafek. config.py dostarcza wartości
  fabryczne (seed).
- Ceny per-projekt jako migawka ustawień z chwili utworzenia - zmiana
  ustawień globalnych nie zmienia istniejących wycen; ceny projektu są
  edytowalne osobno.
- Migracja: projekty sprzed wprowadzenia wyceny uzupełniają migawkę cennika
  przy wczytaniu.

## v0.9.1
- Usuwanie projektów (API, interfejs przeglądarkowy oraz CLI).
- Domknięcie parzystości CLI z API: usuwanie i zmiana nazwy sekcji,
  edycja oraz usuwanie szafek w interfejsie tekstowym.
- Migracja starszych projektów: brakujące ID sekcji uzupełniane przy
  wczytaniu (naprawia błąd usuwania sekcji bez ID).
- Zestaw testów (pytest) dla usług, generatorów oraz API.
- Nagłówki no-cache dla zasobów statycznych - przeglądarka nie serwuje
  nieaktualnego JS/CSS.

## v0.9.0
- REST API (FastAPI) oraz interfejs przeglądarkowy.
- Rysunek elewacji sekcji (SVG) generowany z wymiarów szafek.
- Lista rozkroju z podsumowaniem materiału i obrzeża, eksport CSV.
- Wydzielenie usług SectionService i CabinetService - wspólna logika
  dla CLI i API.
- Edycja i usuwanie sekcji oraz szafek.
- Przeliczanie numeracji technologicznej po usunięciu obiektu.
- Atomowy zapis project.json.
- Środowisko uruchomieniowe oparte o uv.

## v0.8.5
- Model Part oraz PartGenerator - generowanie formatek korpusu.
- CabinetWizard, obsługa szafek w SectionWorkspace.

## v0.1
- Utworzenie struktury projektu.
- Dodanie dokumentacji.
- Przygotowanie do implementacji modelu danych.
