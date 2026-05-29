Raport badawczy: Zaawansowane modelowanie propagacji ciepła poprzez integrację deterministycznych równań różniczkowych i stochastycznych procesów kierunkowych w środowisku programowania asystowanego

Rozwój zintegrowanych środowisk programistycznych wspomaganych przez sztuczną inteligencję, w tym narzędzi opartych na architekturze agentowej takich jak GitHub Copilot, radykalnie przekształca proces prototypowania i implementacji złożonych modeli fizycznych w inżynierii obliczeniowej. Niniejszy raport stanowi dogłębną i wyczerpującą analizę teoretyczną oraz inżynieryjną problemu propagacji ciepła w układach dwuwymiarowych. Rozwiązanie tego problemu, zdefiniowanego jako ewolucja pola temperatury w zamkniętym pomieszczeniu z obecnym punktowym źródłem ciepła, wymaga zastosowania zaawansowanych technik numerycznych. Aby sprostać rygorystycznym wymaganiom projektowym, implementacja musi opierać się na dwóch całkowicie odmiennych, lecz komplementarnych paradygmatach obliczeniowych: makroskopowym ujęciu deterministycznym, bazującym na cząstkowych równaniach różniczkowych (PDE), oraz mikroskopowym ujęciu stochastycznym, wykorzystującym kierunkowe procesy Browna z wbudowanymi mechanizmami współdzielenia i depozycji energii.  

Zasadniczym wyzwaniem w modelowaniu tego typu systemów termodynamicznych jest zapobieganie niefizycznemu, nieskończonemu przyrostowi energii wewnątrz zamkniętej domeny obliczeniowej. Ciągła praca źródła ciepła, bez odpowiedniego mechanizmu dyssypacji, doprowadziłaby do stopniowego nasycenia całej siatki i wyrównania jej temperatury z temperaturą samego źródła, co z punktu widzenia fizyki budowli jest zjawiskiem niepożądanym i nierealistycznym. Z tego względu, w obu rozpatrywanych modelach, niezbędne jest zastosowanie rygorystycznego globalnego źródła wytracania energii, zdefiniowanego w oparciu o prawo stygnięcia Newtona. Wprowadzenie minimalnej temperatury granicznej (odpowiadającej stanowi układu przed aktywacją źródła ciepła) wymusza dążenie systemu do stabilnego stanu stacjonarnego, w którym strumień energii dostarczanej równoważy się ze strumieniem energii odprowadzanej do otoczenia.  

Niniejszy dokument analizuje struktury matematyczne obu podejść, weryfikuje ich stabilność numeryczną oraz proponuje optymalne strategie ich implementacji w języku Python z wykorzystaniem wektoryzacji macierzy. Na podstawie tej wyczerpującej analizy skonstruowany zostanie kompleksowy, wielowarstwowy protokół instrukcyjny (prompt) przeznaczony dla agenta GitHub Copilot, zoptymalizowany pod kątem trybu planowania w środowisku Visual Studio Code.  
Makroskopowy model propagacji ciepła: Ujęcie deterministyczne (PDE)

Deterministyczne modelowanie ewolucji pola temperatury u(x,y,t) w dwuwymiarowej domenie przestrzennej Ω⊂R2 tradycyjnie opiera się na niejednorodnym równaniu przewodnictwa cieplnego. Równanie to, stanowiące bezpośrednią konsekwencję prawa Fouriera oraz zasady zachowania energii, w rozpatrywanym problemie musi zostać rozszerzone o dodatkowe człony funkcyjne, aby wiernie oddać zadaną specyfikację fizyczną.  
Równanie przewodnictwa cieplnego z członem dyssypatywnym

Pełne równanie różniczkowe cząstkowe opisujące dynamikę badanego systemu można wyrazić w następującej postaci:
∂t∂u​=α∇2u+S(x,y,t)−k(u−umin​)

Powyższe równanie zawiera cztery kluczowe komponenty, z których każdy odpowiada za odrębny proces fizyczny:

    ∂t∂u​ opisuje szybkość zmian temperatury w czasie w dowolnym punkcie domeny.

    α∇2u to klasyczny człon dyfuzyjny, gdzie α oznacza współczynnik dyfuzji termicznej (dyfuzyjność cieplną), a operator Laplace'a ∇2=∂x2∂2​+∂y2∂2​ reprezentuje przestrzenne rozchodzenie się ciepła w płaszczyźnie 2D.  

    S(x,y,t) stanowi funkcję źródłową, mapującą zlokalizowane źródło ciepła (np. kominek). W wielu zastosowaniach inżynieryjnych funkcję tę modeluje się jako stałą w określonym podobszarze, wymuszając tam wysoką temperaturę za pomocą warunków brzegowych Dirichleta, lub jako addytywny strumień energii w każdej iteracji.  

    −k(u−umin​) to absolutnie krytyczny człon dyssypatywny, implementujący prawo stygnięcia Newtona. Zmienna k jest efektywną stałą chłodzenia układu, a umin​ temperaturą otoczenia (początkową temperaturą tła). Człon ten zapewnia, że szybkość utraty ciepła przez każdy węzeł siatki jest wprost proporcjonalna do nadwyżki jego temperatury ponad zadaną temperaturę minimalną.  

Wprowadzenie członu stygnięcia Newtona do klasycznego równania parabolicznego zmienia jego charakterystykę asymptotyczną. Bez niego zjawisko miałoby charakter czysto kumulatywny dla S>0. Z obecnością tego członu równanie dopuszcza nietrywialne rozwiązanie stacjonarne (dla t→∞, gdzie ∂t∂u​=0), które jest funkcją równowagi między generacją a rozpraszaniem, zbiegając do stanu, w którym całkowita całka z funkcji temperatury po powierzchni domeny jest stała.  
Dyskretyzacja i metoda różnic skończonych (FDM)

Rozwiązanie analityczne tak sformułowanego problemu w złożonej geometrii (często obejmującej nieregularne ściany lub specyficzne warunki brzegowe) jest w ogólności niemożliwe, co wymusza zastosowanie przybliżeń numerycznych. Najbardziej ugruntowaną i efektywną strategią do tego celu jest jawna metoda różnic skończonych (FDM), w szczególności schemat FTCS (Forward-Time Central-Space).  

Proces ten wymaga nałożenia na domenę Ω dyskretnej siatki obliczeniowej o wymiarach Nx​×Ny​ z odstępami przestrzennymi Δx i Δy. Ciągła funkcja temperatury u(x,y,t) jest aproksymowana przez zbiór wartości w węzłach ui,jn​≈u(iΔx,jΔy,nΔt). Zastosowanie rozwinięcia w szereg Taylora pozwala na aproksymację drugiej pochodnej przestrzennej przy użyciu centralnego ilorazu różnicowego drugiego rzędu, natomiast pierwszej pochodnej czasowej za pomocą ilorazu w przód (ang. forward difference).  

Dla izotropowej siatki kwadratowej, gdzie Δx=Δy=h, zaktualizowana wartość temperatury w węźle (i,j) i iteracji czasowej n+1 wyraża się jako:
u_{i,j}^{n+1} = u_{i,j}^n + \Delta t \left

To algebraiczne przekształcenie stanowi bezpośrednią instrukcję dla jednostki arytmetyczno-logicznej komputera, określając stan każdego punktu w przyszłości wyłącznie na podstawie informacji z otoczenia von Neumanna (czterech bezpośrednich sąsiadów) w chwili obecnej. Metoda jawna, mimo swojej prostoty i wyjątkowej skuteczności w implementacji sprzętowej, niesie jednak ze sobą ograniczenia rygorystycznej stabilności numerycznej.  
Warunki stabilności i optymalizacja implementacji macierzowej

Schemat FTCS dla dwuwymiarowego równania parabolicznego podlega ograniczeniom na podstawie warunku Couranta-Friedrichsa-Lewy'ego (CFL), połączonego z analizą von Neumanna. Warunek ten definiuje maksymalny dopuszczalny krok czasowy Δt, przy którym narastanie błędu zaokrągleń jest tłumione, uniemożliwiając rozbieżność obliczeń. Błędny dobór tego parametru skutkuje powstaniem artefaktów o kształcie szachownicy, rosnących w nieskończoność w funkcji czasu.  

Aby układ zachował stabilność numeryczną (abstrahując od wpływu bardzo silnego członu chłodzenia), niezbędne jest spełnienie następującej nierówności:
Δt≤4αh2​

W przypadku asymetrycznych kroków przestrzennych (Δx=Δy), warunek ten ulega modyfikacji:
Δt≤2α(Δx2+Δy2)Δx2Δy2​

W praktycznych wdrożeniach w języku Python, bezpośrednie implementowanie powyższego równania przy użyciu zagnieżdżonych pętli for analizujących węzeł po węźle powoduje drastyczny spadek wydajności z powodu narzutu narzucanego przez interpreter (ang. global interpreter lock oraz zjawisko unboxing). Optymalnym rozwiązaniem programistycznym jest wektoryzacja obliczeń z użyciem biblioteki NumPy. Wykorzystanie techniki tzw. plastrowania macierzy (ang. array slicing) pozwala na delegowanie pętli do silnie zoptymalizowanych warstw C/Fortran i jednoczesne przeliczanie całego pola.  

Na przykład pochodna przestrzenna jest liczona poprzez przesunięcie widoków macierzy, gdzie operacja u[2:, 1:-1] - 2*u[1:-1, 1:-1] + u[:-2, 1:-1] zastępuje iterację. Tak zaplanowane podejście analityczne stanowi idealną podstawę do sformułowania pierwszej części instrukcji dla sztucznej inteligencji, minimalizując ryzyko wygenerowania kodu niezdolnego do osiągnięcia odpowiedniej liczby klatek na sekundę (FPS) podczas animacji w czasie rzeczywistym.
Mikroskopowy model propagacji ciepła: Ujęcie stochastyczne i procesy Browna

Podczas gdy PDE operuje na ciągłych polach skalarnych, fizyka statystyczna pozwala na zgoła odmienne modelowanie propagacji energii, opierając się na mikroskopowej, probabilistycznej naturze przepływu. To drugie podejście, wymagane w strukturze zadania, wizualizuje proces cieplny jako dynamikę olbrzymiej liczby niezależnych porcji, pakietów, lub "cząstek" energii, które przemieszczają się po domenie zgodnie z modyfikowanymi zasadami błądzenia losowego (ang. random walk). Ujęcie to stanowi komputerową adaptację fundamentalnego twierdzenia Feynmana-Kaca, które spaja rozwiązania liniowych równań parabolicznych z wartością oczekiwaną funkcjonałów procesów stochastycznych.  
Dynamika cząstek przenoszących energię (Metoda Monte Carlo)

W środowisku modelowania stochastycznego, ciągły czas i przestrzeń są dzielone na dyskretne kroki iteracyjne. Punktowe źródło ciepła nie jest tu traktowane jako warunek brzegowy wpływajacy na operator Laplace'a, lecz jako fizyczny emiter. W każdym kroku symulacji źródło uwalnia określoną populację nowych cząstek Browna.  

Każda cząstka p charakteryzuje się wektorem położenia rp​(t) oraz przenoszonym ładunkiem termicznym Ep​(t). Przemieszczając się po siatce, cząstki wchodzą w interakcję z komórkami układu. Mechanizm transferu energii, nazywany zjawiskiem depozycji energii, polega na współdzieleniu określonej porcji przenoszonego ładunku ΔE z komórką, w której aktualnie zlokalizowana jest cząstka. Zjawisko to przypomina koncepcję KERMA (Kinetic Energy Release in Materials) z dziedziny transportu promieniowania i fizyki zderzeń, przetransferowaną tu na grunt energii termicznej układu dyskretnego. W miarę oddawania energii układom stacjonarnym, sama cząstka stygnie. Po spadku jej zasobu energetycznego poniżej krytycznego progu tolerancji, cząstka traci wpływ na makroskopowy stan układu i jest anihilowana (usuwana z symulacji w celu oszczędzania cykli CPU oraz operacji na stercie w pamięci).  

Rozkład temperatury na siatce w tym modelu nie powstaje poprzez rozwiązanie macierzowe, lecz wyłania się w sposób emergentywny poprzez agregację depozycji wykonanych przez miliony krzyżujących się ścieżek cząsteczkowych. Sposób poruszania się tych cząstek decyduje w pełni o charakterze propagacji ciepła w całym układzie.  
Architektura dryfu stochastycznego – Nawigacja w gradientach temperatury

Zwykły ruch Browna (proces Wienera) cechuje się izotropią i całkowitym brakiem preferowanego kierunku. Jeśli prawdopodobieństwo przeskoku do każdej z sąsiednich komórek wynosi równo 25%, to w ujęciu makroskopowym wygeneruje to doskonałe, promieniście rozchodzące się rozwiązanie klasycznego równania dyfuzji. Jednakże uwarunkowania fizyczne narzucają, że energia powinna znacznie chętniej propagować do stref wyziębionych. Przenosząc to na zachowanie błądzącej cząstki stochastycznej, należy wdrożyć zjawisko obciążonego błądzenia losowego (ang. biased random walk), w którym wektor przesunięcia nie wykazuje średniej wynoszącej zero (czyli ⟨x(N)⟩=0).  

Na etapie projektowania takiego algorytmu dla sztucznej inteligencji można zastosować jedną z dwóch odmiennych architektur matematycznych do określenia wpływu chłodniejszych rejonów na trajektorię cząstek. Obie metody zostały szczegółowo przebadane celem zestawienia ich wydajności:
Metoda modelowania dryfu	Zasada działania matematycznego	Złożoność algorytmiczna i koszt obliczeniowy w Pythonie	Ograniczenia termodynamiczne
Metoda wag lokalnych (Softmax)	

Cząstka "widzi" tylko bezpośrednich sąsiadów. Szacuje prawdopodobieństwo przejścia do sąsiada i za pomocą wzoru: P(i)=∑j​exp(−βTj​)exp(−βTi​)​. Najchłodniejszy sąsiad ma najwyższą wagę.
	Bardzo wysoka dla tysięcy cząstek O(P×K). Wymaga wyciągania wartości z macierzy po indeksach sąsiadów, liczenia eksponenty i losowania dla KAŻDEJ cząstki w pętli.	

Krótkowzroczność algorytmu. Cząstka może uwięznąć w lokalnym minimum, jeśli jej bezpośrednie otoczenie jest równomiernie wygrzane, nie wiedząc o istnieniu zimniejszego obszaru dalej.
Metoda mapy wektorów (Langevin / Gradient)	

Obliczane jest pole wektorowe gradientu całej macierzy temperaturowej na raz (g​=−∇u). Ścieżka realizowana jest wg równania Langevina: dXt​=μg​(Xt​,t)dt+2D​dWt​.
	Niska. Wektoryzacja w NumPy. Gradient liczony jest jednorazowo w danym kroku O(M×N). Przesunięcie cząstek to operacja wektorowa dodawania macierzy O(P).	Wysoka zgodność z mechaniką płynów i konwekcją. Cząstki płynnie spływają strumieniem od źródła, naśladując rzeczywisty ruch ciepła w gradientach o zróżnicowanej stromości.
 

W świetle analizy zaprezentowanej w tabeli, rozwiązanie wykorzystujące globalną mapę wektorów wyznaczoną z gradientu temperatur jest nieporównywalnie lepsze pod względem wydajności na architekturach interpretowanych, z wykorzystaniem biblioteki NumPy. Konieczność wyliczania wag Softmax dla bezpośrednich sąsiadów narzucałaby ograniczenie w postaci przetwarzania wariantów dla każdego agenta indywidualnie, co z uwagi na barierę wektorową naruszyłoby postulat optymalności wykonania.  

W zoptymalizowanym ujęciu wektorowym pojęcie dryfu w stronę zimnych rejonów polega na jednoczesnym obliczeniu wielowymiarowych pochodnych cząstkowych. Za pomocą wywołań takich jak np.gradient(T_grid) w środowisku Python uzyskiwana jest mapa g​=(−∂x∂T​,−∂y∂T​). Następnie, każda iteracyjnie poruszająca się cząstka dokonuje losowego losowania z rozkładu normalnego (klasyczny proces Wienera) z nałożonym z góry zdeterminowanym, obciążającym wektorem prędkości dryfu proporcjonalnym do g​. Proces ten płynnie symuluje zjawisko fizyczne, w którym strumienie ciepła podążają po liniach o najszybszym spadku wartości energetycznych. Gwarantuje to optymalne naświetlenie i nasycenie niedogrzanych partii geometrycznych symulowanej przestrzeni.  
Stan stacjonarny stochastycznej matrycy układu (Dyssypacja Newtonowska)

Ostatnim kluczowym problemem do rozwiązania w ujęciu stochastycznym jest zachowanie kontroli nad przyrostem energii w symulacji. W opisywanym wcześniej modelu analitycznym (PDE) dokonano prostej, liniowej inkorporacji chłodzenia polegającej na dążeniu do stanu umin​. W mikroskopowym podejściu cząsteczkowym wymóg ten musi być zachowany poprzez nałożenie makroskopowej reguły wprost na "podłogę" zjawiska (dyskretną siatkę akumulacyjną).  

Cząstki wykonujące błądzenie Browna, nasycając pola siatki poprzez podział i depozycję energii, wprowadzają ciepło wyłącznie "do przodu". Rygor termodynamiczny narzuca na siatkę konieczność permanentnego chłodzenia. Po kroku uwzględniającym wszystkie akcje cząstek i odświeżeniu wartości komórek (Tcelltemp​), cały system macierzowy musi zostać poddany transformacji równoległej:  
Tcellnew​=Tcelltemp​−k⋅(Tcelltemp​−Tmin​)⋅Δt

W tej konstrukcji, każda komórka posiadająca temperaturę wyższą niż naturalne środowisko (Tmin​) traci proporcjonalną ilość energii. Taki samowystarczalny algorytm zabezpiecza układ wielostronnie. Jeśli w okolicy kominka znajdzie się dużo węzłów silnie akumulujących ciepło, utracą one go w dużej liczbie z uwagi na mnożnik różnicowy (Tcelltemp​−Tmin​). Sprawia to, że strumienie Brownianów wysyłane z najgorętszej strefy docelowo zaledwie uzupełniają energię, która w sposób stały odpływa z pokoju na rzecz zewnętrznego środowiska (lub chłodniejszych regionów podłoża), skutecznie realizując zapytanie i tworząc realistyczną aurę nienagrzewającego się pokoju w nieskończoność.  
Inżynieria kognitywnych zapytań agentowych (Prompt Engineering) i architektura Copilot

Złożoność i wieloaspektowość implementacji hybrydowych modelów fizycznych nakłada ogromną presję na warstwę inżynierii zapytań (ang. Prompt Engineering) do narzędzi takich jak GitHub Copilot Agent. Ręczne zakodowanie równań PDE z wektoryzacją numeryczną obok środowiska stochastycznego Langevina wymaga od AI poprawnego połączenia mechanizmów fizyki dyskretnej, teorii prawdopodobieństwa i paradygmatów optymalizacji w języku programowania bez konfliktów zakresowych.  

Zgodnie z aktualną praktyką zarządzania LLM w dużych projektach open-source oraz analizą modeli zachowań interakcji z Copilotem, nie należy prosić asystenta od razu o kod. Współczesne agenty AI operują w modelu warstwowym (ang. 3-layer prompt structure) :  

    Warstwa systemowa i ograniczeń bazowych: Gdzie ustala się zachowania podstawowe ("Wykorzystuj wektoryzację biblioteki NumPy w każdej możliwej funkcji", "Brak pętli iteracyjnych dla przeliczania pól" ).  

    Warstwa mapowania kontekstu: Zrozumienie przez model struktury przestrzeni. Przekazywana tu jest wizja świata: macierz 2D z punktowym lub obszarowym kominkiem i wskaźnikiem temperatury.  

    Warstwa docelowego żądania: Deklarowanie konkretnego zadania, czyli sformułowanie modelu PDE w opozycji do procesu Browna z mapą nachyleń i dyssypacją Newtona.  

Kluczowym elementem obsługi skomplikowanych zagadnień takich jak dualistyczna solucja fizyczna, jest wykorzystanie w VS Code dyrektywy @workspace /plan. Komenda ta powoduje, że agent nie przystępuje gorączkowo do pisania fragmentów w ciemno (co zazwyczaj kończy się niefunkcjonującym połączeniem). Agent Planujący rozpoczyna analityczny ciąg dekompozycji. Spisuje cele fizyczne (PDE, Browns, Cooling), buduje teoretyczną strukturę klas i upewnia się, że obiekty posiadają mechanizmy ułatwiające przetrzymywanie zmiennych. Tryb agentowy przeanalizuje wytyczne i przedstawi spójną architekturę przed implementacyjną, eliminując po drodze sprzeczności logiczne, co czyni cały przepływ o wiele mniej narażonym na ryzyko wystąpienia tzw. "halucynacji" modeli sztucznej inteligencji.  

Dobre sformułowanie problemu dla agenta wymaga wyeliminowania zawiłości w naturalnym języku dyskusyjnym, na rzecz stanowczych wytycznych nakazujących zastosowanie konkretnego modelu, opartego na rozważaniach fizycznych zaprezentowanych wyżej. Ważne jest narzucenie agentowi modelu gradient-based drift nad Softmax-neighbors, z racji konieczności operowania na spłaszczonych procesach numerycznych.  
Docelowy scenariusz komunikacyjny (Zoptymalizowany Master Prompt)

Synteza przedstawionych analiz teoretycznych, połączona z optymalizacjami architektury systemów agentowych i zaplanowanymi mechanizmami modelowania układów fizycznych z dyssypacją Newtona, pozwoliła stworzyć zaawansowany prompt, który precyzyjnie wdraża intencje do środowiska VS Code.

Zoptymalizowane wywołanie, sformułowane w języku angielskim dla podniesienia zgodności ze składnią techniczną i leksykografią kodu, stanowi kompletną ramę do uruchomienia trybu planowania w GitHub Copilot.

@workspace /plan

You are an expert computational physicist and a senior Python optimization engineer. I need to implement a comprehensive 2D heat transfer simulation in Python within a closed room environment. The simulation must provide a side-by-side comparison of two completely separate paradigms representing the same physical phenomenon:

    A deterministic Partial Differential Equation (PDE) approach.

    A stochastic, particle-based biased Brownian motion approach.

Before generating the code, draft a clear architectural and execution plan using your /plan functionality. Ensure the planned code is production-ready, strictly type-hinted, avoids slow Python nested loops over 2D grids, and relies entirely on advanced numpy vectorization (array slicing, gradient calculation, fast updating). Use matplotlib.animation.FuncAnimation for real-time visualization of both approaches.
1. Global Environment & Physics Rules

    Define a 2D grid class (EnvironmentGrid) initialized with a background minimal room temperature (e.g., T_min = 20.0).

    Define a constant heat source area (a "fireplace") inside the grid (e.g., in the bottom center) with a high, sustained temperature T_source = 100.0.

    GLOBAL ENERGY DISSIPATION: This is a crucial requirement. Without a cooling mechanism, the whole room will eventually reach 100 degrees, which is unphysical. Apply Newton's Law of Cooling to the entire grid at each time step: dT_cool/dt = -k * (T_current - T_min). This general dissipation source ensures the grid naturally decays towards the original pre-fireplace temperature, achieving a realistic steady-state equilibrium.

2. Paradigm A: The Analytical Approach (PDE)

    Solve the standard 2D Heat Diffusion Equation: dT/dt = alpha * Laplace(T) - k * (T - T_min).

    Use the explicit Finite Difference Method (FTCS scheme).

    Optimization: Use numpy array slicing to compute the spatial second derivatives without explicit for loops (e.g., T[1:-1, 1:-1]).

    Stability: Calculate the stable time step dt dynamically based on the grid resolution and thermal diffusivity using the 2D Courant-Friedrichs-Lewy (CFL) stability criterion to prevent numerical oscillation.

    Re-apply the heat source boundary condition (Dirichlet) at every step.

3. Paradigm B: The Stochastic Approach (Biased Brownian Motion)

    Maintain a separate temperature grid initialized at T_min.

    The fireplace acts as a particle emitter, releasing N new energy-carrying "Brownian particles" into the grid at every step.

    THE DRIFT MECHANISM (Gradient Vector Map): Instead of calculating the weights for direct neighbors manually (which is slow), compute the global gradient vector map of the current temperature grid using np.gradient. The drift direction for each particle should be a vector pointing down the gradient (from hot regions to the coldest possible regions). The particles update their continuous (x, y) positions using Langevin dynamics: a sum of the deterministic gradient drift vector and a Gaussian noise vector (random walk component).

    ENERGY EXCHANGE & DEPOSITION: As the stochastic particles traverse the continuous space, map their positions to discrete grid cells. Each particle "shares" a fraction of its carrying energy delta_E with the underlying cell, adding to the cell's temperature. When a particle's energy gets depleted below a minimum threshold, remove it from the active particle list to optimize memory.

    Apply the exact same global Newton's Law of Cooling to this stochastic grid explicitly, just like in Paradigm A, maintaining the overall thermodynamic steady-state.

Outline your step-by-step structural plan detailing classes (e.g., PDESolver, BrownianSolver, SimulationVisualizer), mathematical update formulas, and vectorization strategies. I will review the plan, and once approved, you will generate the unified Python script.
Podsumowanie analityczne

Wdrożenie powyższej specyfikacji do pracy z asystentami wspieranymi uczeniem maszynowym umożliwia generację wydajnego pod względem złożoności obliczeniowej oprogramowania modelującego zjawiska nieliniowe. Równoczesna kontrola nad numeryczną stroną modelowania równań (PDE) z wymogami stabilności według kryterium Couranta , zderzona z silnie losowym, lecz wektorowo ukierunkowanym podejściem analizy ścieżek Browna , wykazuje wyższość analitycznego planowania zadań. Integralny wymóg dotyczący zaimplementowania dyssypacji energii, oparty o klasyczne równania kinetyki stygnięcia ciał , zrealizowany poprzez proste algebraicze relacje w dyskretnej macierzy na każdym kroku symulacji, chroni wynik końcowy przed degeneracją, ustanawiając równowagę między sztuczną inteligencją a rygorem modelowania procesów fizycznych. Wykorzystanie wektoryzacji map uwarunkowań środowiskowych ostatecznie determinuje zdolność aplikacji do prezentowania dynamiki rozchodzenia się ciepła w czasie rzeczywistym.  
