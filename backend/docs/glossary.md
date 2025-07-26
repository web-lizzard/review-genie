# Glosariusz DDD - AI Code Review System

## Agregaty

### Project
Agregat reprezentujący pojedyncze repozytorium kodu podłączone do systemu AI Code Review.

**Atrybuty:**
- ID - unikalny identyfikator repozytorium (obiekt wartości)
- Repository ID (id ze zewnętrznego repozytorium)
- Repository Name - nazwa repozytorium
- Provider - dostawca usługi (GitHub, GitLab, Bitbucket)
- Owner - właściciel repozytorium
- URL - adres repozytorium
- Policies - zasady tworzenia analiz (obiekt wartości)
- Rules - reguły code review (obiekt wartości)

**Zachowania biznesowe:**
- `update_rules()` - aktualizacja reguł code review
- `start_analysis()` - metoda wytwórcza dla agregatu Analysis

**Wydarzenia domenowe:**
- `ProjectTracked` - projekt został dodany do trackingu
- `ProjectDeleted` - projekt został usunięty
- `ProjectRulesUpdated` - reguły projektu zostały zaktualizowane

**Ograniczenia biznesowe:**
- Provider musi być jednym ze wspieranych (GitHub, GitLab, Bitbucket)
- Przy tworzeniu należy zweryfikować istnienie repozytorium
- **MVP: Wspierane są tylko publiczne repozytoria GitHub**
- Policies są wymagane (domyślne, nie wybierane przez użytkownika)
- Rules nie są wymagane (ustawiane domyślne wartości)
- Usunięcie projektu powoduje usunięcie wszystkich powiązanych analiz
- Brak ograniczeń na edycję policies (na obecnym etapie)
- Projekty "martwe" (bez aktywności) są akceptowalne (MVP)
- Project jest agregatem głównym - kontroluje dostęp do swoich obiektów wartości

### Analysis
Agregat reprezentujący jedną analizę konkretnego Pull Requesta.

**Atrybuty:**
- ID - unikalny identyfikator analizy
- Project ID - identyfikator powiązanego projektu
- Pull Request ID - identyfikator Pull Requesta
- Diff - różnice kodu z Pull Requesta
- Status - aktualny status analizy (obiekt wartości)
- Context - kontekst analizy (obiekt wartości)
- Created At - timestamp utworzenia analizy
- Ready At - timestamp gotowości do review
- Comments - kolekcja komentarzy wygenerowanych przez AI (encje, lazy loaded)

**Zachowania biznesowe:**
- `conduct_analysis()` - ustawienie analizy na status "gotowa do review" → `CommentsGenerated`
- `approve_analysis()` - zaaprobowanie analizy przez użytkownika
- `reject_analysis()` - odrzucenie analizy
- `retry_analysis()` - ponowna analiza z dodatkowym kontekstem
- `delete_analysis()` - usunięcie analizy → `AnalysisDeleted`
- `create_comment()` - metoda wytwórcza dla Comment w ramach analizy

**Sposoby tworzenia:**
1. **Automatyczne** - przy nowym/zmodyfikowanym PR (zgodnie z Policies projektu)
2. **Przez użytkownika** - przy ponownej analizie z nowym kontekstem (z zachowaniem Policies)

**Wydarzenia domenowe:**
- `AnalysisCreated` - analiza została utworzona
- `CommentsGenerated` - AI wygenerowało komentarze
- `AllCommentsReviewed` - wszystkie komentarze zostały przejrzane
- `AnalysisApproved` - analiza została zaaprobowana
- `AnalysisRejected` - analiza została odrzucona
- `AnalysisDeleted` - analiza została usunięta
- `AnalysisRetried` - analiza została ponowiona
- `ContextAdded` - dodano dodatkowy kontekst

**Ograniczenia biznesowe:**
- Analysis musi być zawsze powiązana z konkretnym Pull Request
- Nie może istnieć bez Project
- Ponowienie analizy = utworzenie nowej Analysis + odrzucenie poprzedniej
- Utworzenie musi spełniać Policies projektu
- **Approval wymaga: wszystkie Comments muszą mieć status (rejected/approved) + min. 1 Comment approved**
- **Comments mogą być modyfikowane tylko przy statusie Analysis "gotowa do review"**
- Analysis jest agregatem głównym - kontroluje dostęp do swoich encji

## Encje

### Comment
Encja reprezentująca komentarz wygenerowany przez AI w ramach analizy.

**Atrybuty:**
- ID - unikalny identyfikator komentarza
- Analysis ID - identyfikator powiązanej analizy
- Content - treść komentarza
- File Path - ścieżka do pliku
- Line Number - numer linii
- Severity Level - poziom ważności
- Status - status komentarza (obiekt wartości)
- Created At - timestamp utworzenia
- Modified At - timestamp ostatniej modyfikacji

**Zachowania biznesowe:**
- `update_content()` - modyfikacja treści komentarza przez użytkownika
- `set_status()` - ustawienie statusu (approved/rejected/pending)

**Wydarzenia domenowe:**
- `CommentConfirmed` - emitowane przy ustawieniu statusu approved
- `CommentModified` - emitowane przy zmianie treści komentarza
- `CommentDeleted` - emitowane przy ustawieniu statusu rejected

**Ograniczenia biznesowe:**
- Comment może być modyfikowany tylko gdy Analysis ma status "gotowa do review"
- Status może być zmieniony dowolnie (approved ↔ rejected ↔ pending)
- Content może być edytowany przez użytkownika
- Comment nie może być usunięty, tylko rejected
- Użytkownik nie może dodawać własnych komentarzy (MVP)

## Obiekty Wartości

### ID
Unikalny identyfikator repozytorium w formacie provider:owner:repo_id.

**Struktura:**
- Format: `{provider}:{owner}:{repo_id}`
- Przykład: `github:microsoft:typescript`

**Ograniczenia:**
- Provider musi być wspieranym dostawcą
- Owner i repo_id nie mogą być puste
- Identyfikator musi być unikalny w całym systemie

### AnalysisStatus
Status określający aktualny etap analizy.

**Możliwe wartości:**
- `utworzony` - analiza została utworzona, ale nie przeprowadzona przez AI
- `gotowa do review` - AI ukończył pracę, komentarze zostały wygenerowane
- `zaaprobowana` - wszystkie komentarze zostały przejrzane przez użytkownika
- `odrzucona` - użytkownik odrzucił analizę definitywnie lub ponowił ją

**Reguły przejść:**
- utworzony → gotowa do review (po wygenerowaniu komentarzy)
- gotowa do review → zaaprobowana (po review wszystkich komentarzy)
- gotowa do review → odrzucona (przez użytkownika)
- zaaprobowana → odrzucona (przy ponowieniu analizy)

### CommentStatus
Status określający stan przeglądu komentarza przez użytkownika.

**Możliwe wartości:**
- `pending` - komentarz oczekuje na przegląd (domyślny status)
- `approved` - komentarz zaakceptowany przez użytkownika
- `rejected` - komentarz odrzucony przez użytkownika

**Reguły przejść:**
- pending → approved (użytkownik akceptuje komentarz)
- pending → rejected (użytkownik odrzuca komentarz)
- approved ↔ rejected (użytkownik może zmienić decyzję)
- Zmiana statusu możliwa tylko gdy Analysis ma status "gotowa do review"

### Diff
Obiekt wartości reprezentujący różnice kodu z Pull Requesta w znormalizowanym formacie.

**Odpowiedzialność:**
- Normalizacja różnic z różnych providerów (GitHub, GitLab, Bitbucket) do wspólnego standardu
- Dostarczenie ujednoliconego interfejsu do analizy zmian w kodzie
- Enkapsulacja logiki parsowania i walidacji różnic

**Ograniczenia:**
- Immutable - nie może być modyfikowany po utworzeniu
- Musi być poprawnie sparsowany z źródłowego formatu
- Zawiera tylko dane niezbędne do analizy kodu

### Context
Kontekst analizy zawierający informacje pomocne dla AI.

**Struktura:**
- Komentarze z poprzedniej analizy (jeśli istnieje)
- Lista dodatkowych tekstów wprowadzonych przez użytkownika
- Metadane Pull Requesta

**Odpowiedzialność:**
- Dostarczenie AI szerszego kontekstu o Pull Request
- Zachowanie historii z poprzednich analiz
- Umożliwienie użytkownikowi wpływu na analizę

### Policies
Zasady określające sposób tworzenia i zarządzania analizami w projekcie.

**Struktura:**
- Pull Request Policy - enum określający kiedy tworzyć analizy
- Retry Limit Type - enum określający typ limitu powtórzeń
- Retry Limit Value - wartość limitu (na MVP: maksymalnie 2)

**Ograniczenia biznesowe:**
- Pull Request Policy może być rozszerzany o nowe opcje
- Retry Limit Value obecnie ograniczony do maksymalnie 2 prób
- Policies są ustawiane domyślnie (w przyszłości mogą zależeć od planu subskrypcji)

### Rules
Reguły i konwencje dotyczące przeprowadzania code review.

**Struktura:**
- Lista tekstowa zawierająca reguły projektu

**Odpowiedzialność:**
- Definiuje konwencje dodawania komentarzy do code review
- Określa standardy i zasady projektu
- Zawiera reguły specyficzne dla danego repozytorium
- Łatwa do zarządzania przez użytkowników
- Opcjonalne (system ustawi domyślne wartości jeśli nie określono)

## Serwisy Domenowe

### ProjectCreationService
Serwis odpowiedzialny za tworzenie nowych projektów.

**Odpowiedzialność:**
- Weryfikacja istnienia repozytorium w zewnętrznym systemie
- Sprawdzenie invariantów zewnętrznych
- Koordynacja z ProjectFactory

### ProjectFactory
Fabryka odpowiedzialna za konstrukcję agregatu Project.

**Odpowiedzialność:**
- Walidacja spójności wewnętrznych invariantów
- Utworzenie agregatu Project z poprawnymi obiektami wartości
- Ustawienie domyślnych Policies i Rules

### ProjectDeletionService
Serwis odpowiedzialny za usuwanie projektów.

**Odpowiedzialność:**
- Usunięcie projektu wraz ze wszystkimi powiązanymi analizami
- Koordynacja procesu usuwania między agregatami

### AnalysisRetryService
Serwis odpowiedzialny za ponowną analizę z dodatkowym kontekstem.

**Odpowiedzialność:**
- Pobranie komentarzy z poprzedniej analizy
- Pobranie analizy do skopiowania
- Delegacja do Analysis utworzenia kopii z nowym kontekstem
- Wywołanie `conduct_analysis()` na nowej analizie
- Odrzucenie poprzedniej analizy

### CommentCreationService
Serwis odpowiedzialny za tworzenie komentarzy na podstawie wyników AI.

**Odpowiedzialność:**
- Koordynacja procesu tworzenia komentarzy
- Korzystanie z AICodeReviewPort do otrzymania danych o komentarzach
- Wywołanie metody wytwórczej `create_comment()` na agregacie Analysis
- Mapowanie struktur z portu na encje Comment

### AICodeReviewService
Serwis domenowy odpowiedzialny za orchestrację procesu analizy kodu przez AI.

**Odpowiedzialność:**
- Przygotowanie danych dla serwisu AI (Diff, Context, Rules)
- Korzystanie z AICodeReviewPort do komunikacji z zewnętrznym serwisem AI
- Koordynacja między Analysis, Project i CommentCreationService
- Obsługa flow tworzenia komentarzy

## Porty (Hexagonal Architecture)

### AICodeReview
Port (interfejs) dla komunikacji z zewnętrznym serwisem AI do analizy kodu.

**Odpowiedzialność:**
- Definicja kontraktu dla serwisu AI
- Przyjmowanie danych: Diff, Context, Rules projektu
- Zwracanie ustrukturyzowanych danych o komentarzach
- Abstrakcja dla różnych implementacji AI (GPT, Claude, etc.)

**Kontrakt:**
- Input: Analysis data (Diff, Context, Project Rules)
- Output: Structured comment data (content, file path, line number, severity)
- Obsługa błędów i timeoutów
- Asynchroniczne przetwarzanie

### ProjectRepository
Port (interfejs) dla operacji persistencji agregatu Project.

**Operacje:**
- `save(project: Project)` - zapisanie nowego lub zaktualizowanego projektu
- `findById(id: ID)` - wyszukanie projektu po identyfikatorze
- `delete(id: ID)` - usunięcie projektu

**Ograniczenia:**
- Implementacja musi zapewnić spójność transakcyjną
- Operacje na agregacie muszą być atomowe
- Concurrent access handling dla aktualizacji

### AnalysisRepository
Port (interfejs) dla operacji persistencji agregatu Analysis.

**Operacje:**
- `save(analysis: Analysis)` - zapisanie nowej lub zaktualizowanej analizy
- `findById(id: AnalysisId)` - wyszukanie analizy po identyfikatorze
- `delete(id: AnalysisId)` - usunięcie analizy

**Ograniczenia:**
- Comments są ładowane lazy loading domyślnie
- Implementacja musi obsługiwać kaskadowe usuwanie Comments
- Concurrent access handling dla status changes

### CommentRepositoryPort
Port (interfejs) dla operacji na encji Comment w ramach Analysis.

**Operacje:**
- `save(comments: List<Comment>)` - zapisanie komentarzy dla analizy
- `findApprovedByAnalysisId(analysisId: AnalysisId)` - pobranie zaakceptowanych komentarzy

**Ograniczenia:**
- Comments zawsze należą do konkretnej Analysis
- Nie ma bezpośredniego usuwania Comments (tylko status rejected)
- Batch operations dla lepszej wydajności

### RemoteRepository
Port (interfejs) dla komunikacji z zewnętrznymi systemami kontroli wersji.

**Operacje:**
- `verifyRepositoryExists(provider: string, owner: string, repoName: string)` - sprawdzenie istnienia repozytorium
- `fetchPullRequestDiff(provider: string, owner: string, repoName: string, prId: string)` - pobranie różnic PR
- `sendCommentsToRepository(repoDetails: RepositoryDetails, prId: string, comments: List<Comment>)` - wysłanie komentarzy
- `getPullRequestMetadata(provider: string, owner: string, repoName: string, prId: string)` - pobranie metadanych PR

**Ograniczenia:**
- Obsługa różnych providerów (GitHub, GitLab, Bitbucket)
- Rate limiting i retry policies
- Authentication handling per provider
- Error handling dla niedostępnych repozytoriów
