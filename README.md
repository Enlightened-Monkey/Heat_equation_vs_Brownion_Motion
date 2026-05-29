# PDE + Brownian Heat Propagation

Projekt implementuje dwie niezalezne symulacje propagacji ciepla 2D uruchamiane rownolegle:

- Deterministyczny solver PDE (FTCS, Laplasjan liczony wektorowo NumPy)
- Stochastyczny solver czastek Browna z dryfem po gradiencie temperatury

Domyslny plan pomieszczenia to teraz uklad 2 pokojow z przegroda i drzwiami.
Kominek jest w jednym pokoju (domyslnie lewym), a cieplo przechodzi do drugiego przez otwor drzwiowy.
Domyslnie aktywne jest tez drugie zrodlo ciepla w prawym dolnym rogu (`--second-source-enabled`).

Domyslnie w obu modelach dziala globalne chlodzenie zgodne z prawem Newtona:

- `dT/dt = -k * (T - T_min)`

W modelu Brownian mozna je tymczasowo wylaczyc flaga CLI:

- `--no-brownian-global-cooling`

## Struktura

- `main.py` - punkt startowy i parametry CLI
- `heat_sim/config.py` - konfiguracja i geometria zrodla ciepla
- `heat_sim/environment.py` - operacje wspolne na siatce
- `heat_sim/pde_solver.py` - solver deterministyczny PDE
- `heat_sim/brownian_solver.py` - solver stochastyczny czastek
- `heat_sim/visualizer.py` - animacja porownawcza side-by-side

## Uruchomienie

```bash
python -m venv .venv
source .venv/bin/activate
.venv/bin/python -m pip install -r requirements.txt
python main.py
```

Przyklad z parametrami:

```bash
python main.py --nx 150 --ny 110 --emit-count 180 --steps-per-frame 2

# Szybki podglad real-time (PyQtGraph)
python main.py --renderer pyqtgraph --interval-ms 16

# Uklad 2 pokojow: kominek w lewym pokoju, widoczny przeplyw przez drzwi
python main.py --renderer pyqtgraph --interval-ms 16 --two-room-layout --fireplace-room left --door-height 16 --door-center-ratio 0.75 --cooling-k 0.001

# Wylaczenie drugiego zrodla (prawy dolny rog)
python main.py --renderer pyqtgraph --no-second-source-enabled
```

Jesli chcesz szybsze dogrzanie calego pomieszczenia, zwieksz emisje i oslab chlodzenie:

```bash
python main.py --renderer pyqtgraph --emit-count 320 --cooling-k 0.0035 --interval-ms 16
```

Aby mocno wzmocnic sam PDE (szybsze rozchodzenie ciepla i mniejsze tlumienie), uzyj:

```bash
python main.py --renderer pyqtgraph --interval-ms 16 --pde-alpha-boost 3.0 --pde-cooling-scale 0.35
```

Mozesz tez uzyc gotowych presetow:

```bash
# PDE: custom | medium | turbo
python main.py --renderer pyqtgraph --interval-ms 16 --pde-profile turbo

# Brownian: custom | medium | turbo
python main.py --renderer pyqtgraph --interval-ms 16 --brownian-profile medium

# Oba naraz
python main.py --renderer pyqtgraph --interval-ms 16 --pde-profile turbo --brownian-profile turbo
```

Uwaga: profil `turbo` celowo zmniejsza hotspot zrodla (`t_source`, `source_width`, `source_height`) i jednoczesnie
duzo mocniej przyspiesza rozchodzenie ciepla po pokojach.

Gdy czujesz, ze front ciepla "staje" lokalnie, zwieksz dyfuzje siatki Brownian:

```bash
python main.py --renderer pyqtgraph --brownian-grid-alpha 0.12 --cooling-k 0.0035 --interval-ms 16
```

Zapis animacji do GIF (bez otwierania okna):

```bash
python main.py --frames 240 --save-gif outputs/heat.gif --gif-fps 24 --no-show
```

Uwaga: eksport GIF jest obslugiwany przez renderer matplotlib.
# Heat_equation_vs_Brownion_Motion
