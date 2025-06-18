import random
import copy

class Game:
    """
    Klasa reprezentująca rozgrywkę naszej gry. Zawiera następujące pola:

    n_rows, n_columns : 
        liczba wierszy i kolumn na planszy (domyślnie 7)
    winning_legnth : 
        liczba symboli w jednej linii potrzebna, aby wygrać (domyślnie 4)
    board : 
        plansza, reprezentowana jako lista list. Każda lista to jedna kolumna, a symbole na tej liście to symbole w tej kolumnie, od najniższego do     najwyższego. Np. jeśli plansza w grze 4x4 wygląda tak:

        +-+-+-+-+
        | | | | |
        +-+-+-+-+
        | |1| | |
        +-+-+-+-+
        |0|1| | |
        +-+-+-+-+
        |0|0| |1|
        +-+-+-+-+
        
        to zmienna board ma wartość [[0,0], [0,1,1], [], [1]]
    
        Gracze zawsze reprezentowani są symbolami 0 i 1, zaczyna gracz 0.

    current_player : 
        gracz, na którego ruch aktualnie czekamy. Może to być tylko wartość 0 lub 1, na początku gry jest to 0.

    move_history : 
        historia ruchów od początku rozgrywki, w postaci listy kolumn, w których kolejno były umieszczane symbole. Np plansza z przykładu wyżej mogłaby odpowiadać następującej wartości zmiennej move_history : [0,3,1,1,0,1]

    """
    n_rows: int
    n_columns: int
    winning_length: int
    board: list[list[int]]
    move_history: list[int]
    current_player: int

    def __init__(self, n_rows : int = 7, n_columns : int = 7, winning_length : int = 4):
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.winning_length = winning_length
        self.current_player = 0
        self.board = [[] for _ in range(self.n_columns)]
        self.move_history = []

    def print_board(self):
        """Wyświetla planszę w czytelny sposób."""
        print("\n" + "="*50)
        print("Current Board:")
        print("="*50)
        
        # Wyświetl numery kolumn
        print("  ", end="")
        for col in range(self.n_columns):
            print(f" {col} ", end="")
        print()
        
        # Wyświetl planszę od góry do dołu
        for row in range(self.n_rows - 1, -1, -1):
            print(f"{row} ", end="")
            for col in range(self.n_columns):
                if len(self.board[col]) > row:
                    symbol = 'X' if self.board[col][row] == 0 else 'O'
                    print(f"|{symbol}|", end="")
                else:
                    print("| |", end="")
            print()
        
        print("  " + "---" * self.n_columns)
        print(f"Current player: {'X' if self.current_player == 0 else 'O'}")
        print("="*50)

    def make_move(self, column: int) -> bool:
        """Wykonuje ruch w danej kolumnie. Zwraca True jeśli ruch jest prawidłowy."""
        if column < 0 or column >= self.n_columns:
            return False
        
        if len(self.board[column]) >= self.n_rows:
            return False
        
        # Dodaj token gracza do kolumny
        self.board[column].append(self.current_player)
        self.move_history.append(column)
        
        # Zmień gracza
        self.current_player = 1 - self.current_player
        
        return True
    
    def is_full(self) -> bool:
        """Sprawdza czy plansza jest pełna."""
        return all(len(col) >= self.n_rows for col in self.board)
    
    def check_winner(self) -> int:
        """
        Sprawdza czy ktoś wygrał grę.
        
        Returns:
            0 lub 1 jeśli gracz wygrał, None jeśli nikt nie wygrał
        """
        for player in [0, 1]:
            # Sprawdź pionowe linie
            for col in range(self.n_columns):
                if self.check_line_vertical(self.board[col], player, self.winning_length):
                    return player
            
            # Sprawdź poziome linie
            for row in range(self.n_rows):
                if self.check_line_horizontal(row, player, self.winning_length):
                    return player
            
            # Sprawdź ukośne linie
            if self.check_diagonals(player, self.winning_length):
                return player
        
        return None

    def check_line_vertical(self, column: list[int], player: int, winning_length: int) -> bool:
        """Sprawdza pionową linię w kolumnie."""
        if len(column) < winning_length:
            return False
        
        count = 0
        for symbol in reversed(column):  # Od góry do dołu
            if symbol == player:
                count += 1
                if count >= winning_length:
                    return True
            else:
                count = 0
        return False

    def check_line_horizontal(self, row: int, player: int, winning_length: int) -> bool:
        """Sprawdza poziomą linię w danym wierszu."""
        count = 0
        for col in range(self.n_columns):
            if len(self.board[col]) > row and self.board[col][row] == player:
                count += 1
                if count >= winning_length:
                    return True
            else:
                count = 0
        return False

    def check_diagonals(self, player: int, winning_length: int) -> bool:
        """Sprawdza ukośne linie."""
        # Sprawdź ukos z lewego górnego rogu do prawego dolnego
        for start_col in range(self.n_columns - winning_length + 1):
            for start_row in range(self.n_rows - winning_length + 1):
                count = 0
                for i in range(winning_length):
                    col = start_col + i
                    row = start_row + i
                    if (len(self.board[col]) > row and 
                        self.board[col][row] == player):
                        count += 1
                    else:
                        break
                if count >= winning_length:
                    return True
        
        # Sprawdź ukos z lewego dolnego rogu do prawego górnego
        for start_col in range(self.n_columns - winning_length + 1):
            for start_row in range(winning_length - 1, self.n_rows):
                count = 0
                for i in range(winning_length):
                    col = start_col + i
                    row = start_row - i
                    if (len(self.board[col]) > row and 
                        self.board[col][row] == player):
                        count += 1
                    else:
                        break
                if count >= winning_length:
                    return True
        
        return False
    
class Player:
    """ 
    Klasa reprezentująca program grający z algorytmem alpha-beta pruning i tablicą otwarć.
    """
    def __init__(self, player_id: int = 1):
        self.team_name = "Unbeatable AI"
        self.team_members = ["Kacper Daniel", "Paweł Karwecki", "Tadeusz Jagniewski"]
        self.max_depth = 8
        self.player_id = player_id  # ID gracza AI (0 lub 1)
        
        # Tablica otwarć - klucz to tuple z historii ruchów, wartość to najlepszy ruch
        self.opening_book = self._initialize_opening_book()
        
        # Maksymalna głębokość historii ruchów do sprawdzania w tablicy otwarć
        self.max_opening_depth = 8

    def _initialize_opening_book(self) -> dict:
        """Inicjalizuje tablicę otwarć z dobrymi ruchami początkowymi."""
        opening_book = {}
        
        # Pierwszy ruch - zawsze środek planszy (kolumna 3 dla planszy 7x7)
        opening_book[tuple()] = 3
        
        # Odpowiedzi na pierwsze ruchy przeciwnika
        opening_book[(0,)] = 3  # Jeśli przeciwnik gra skraj, my gramy środek
        opening_book[(1,)] = 3
        opening_book[(2,)] = 3
        opening_book[(3,)] = 2  # Jeśli przeciwnik gra środek, my gramy obok
        opening_book[(4,)] = 3
        opening_book[(5,)] = 3
        opening_book[(6,)] = 3
        
        # Niektóre kontynuacje (dla gracza rozpoczynającego środkiem)
        opening_book[(3, 2)] = 4   # Przeciwnik gra po lewej od środka, my po prawej
        opening_book[(3, 4)] = 2   # Przeciwnik gra po prawej od środka, my po lewej
        opening_book[(3, 1)] = 5   # Symetryczna odpowiedź
        opening_book[(3, 5)] = 1   # Symetryczna odpowiedź
        opening_book[(3, 0)] = 6   # Symetryczna odpowiedź
        opening_book[(3, 6)] = 0   # Symetryczna odpowiedź
        
        # Kontynuacje gdy my rozpoczynamy środkiem, a przeciwnik odpowiada
        opening_book[(3, 2, 4)] = 1  # Kontynuacja rozwoju
        opening_book[(3, 4, 2)] = 5  # Kontynuacja rozwoju
        opening_book[(3, 2, 1)] = 4  # Blokowanie formacji przeciwnika
        opening_book[(3, 4, 5)] = 2  # Blokowanie formacji przeciwnika
        
        # Obrona przeciwko niektórym popularnym otwarciom
        opening_book[(2, 3)] = 4    # Przeciwnik 2-3, my blokujemy
        opening_book[(4, 3)] = 2    # Przeciwnik 4-3, my blokujemy
        opening_book[(1, 3)] = 5    # Asymetryczne otwarcie
        opening_book[(5, 3)] = 1    # Asymetryczne otwarcie
        
        # Dodatkowe wzorce dla lepszej gry
        opening_book[(3, 3)] = 2    # Jeśli przeciwnik też gra środek
        opening_book[(2, 4)] = 3    # Formacja 2-4, gramy środek
        opening_book[(4, 2)] = 3    # Formacja 4-2, gramy środek
        
        return opening_book

    def get_opening_move(self, game: Game) -> int:
        """Sprawdza czy istnieje ruch w tablicy otwarć dla aktualnej pozycji."""
        # Sprawdź tylko jeśli historia nie jest zbyt długa
        if len(game.move_history) > self.max_opening_depth:
            return None
            
        # Sprawdź bezpośrednio historię ruchów
        move_tuple = tuple(game.move_history)
        if move_tuple in self.opening_book:
            suggested_move = self.opening_book[move_tuple]
            # Sprawdź czy ruch jest legalny
            if self.is_valid_move(game, suggested_move):
                return suggested_move
        
        # Sprawdź również wzorce symetryczne (odbicie lustrzane)
        # Dla planszy 7x7, kolumny mapują się: 0<->6, 1<->5, 2<->4, 3->3
        symmetric_history = self.get_symmetric_history(game.move_history)
        symmetric_tuple = tuple(symmetric_history)
        
        if symmetric_tuple in self.opening_book:
            suggested_move = self.opening_book[symmetric_tuple]
            # Odbij ruch symetrycznie
            symmetric_move = self.get_symmetric_column(suggested_move, game.n_columns)
            if self.is_valid_move(game, symmetric_move):
                return symmetric_move
        
        return None

    def get_symmetric_history(self, history: list) -> list:
        """Zwraca symetryczne odbicie historii ruchów."""
        return [6 - move for move in history]  # Dla planszy 7x7

    def get_symmetric_column(self, column: int, n_columns: int) -> int:
        """Zwraca symetryczne odbicie kolumny."""
        return n_columns - 1 - column

    def is_valid_move(self, game: Game, column: int) -> bool:
        """Sprawdza czy ruch jest legalny."""
        return (0 <= column < game.n_columns and 
                len(game.board[column]) < game.n_rows)

    def make_move(self, game: Game) -> int:
        """Zwraca kolumnę dla najlepszego ruchu."""
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        opening_move = self.get_opening_move(game)
        if opening_move is not None:
            print(f"Using opening book move: {opening_move}")
            return opening_move
        
        # Sprawdź czy można wygrać w jednym ruchu
        for col in valid_moves:
            game_copy = self.make_move_copy(game, col)
            if game_copy.check_winner() == game.current_player:
                return col
        
        # Sprawdź czy trzeba zablokować przeciwnika
        for col in valid_moves:
            game_copy = copy.deepcopy(game)
            game_copy.current_player = 1 - game_copy.current_player  # Symuluj ruch przeciwnika
            game_copy.board[col].append(game_copy.current_player)
            if game_copy.check_winner() == game_copy.current_player:
                return col
        
        # Użyj alpha-beta
        _, best_column = self.alpha_beta(game, self.max_depth, float('-inf'), float('inf'), True)
        
        if best_column is None or best_column not in valid_moves:
            # Preferuj środek planszy jako fallback
            center_col = game.n_columns // 2
            if center_col in valid_moves:
                return center_col
            return random.choice(valid_moves)
        
        return best_column

    def alpha_beta(self, game: Game, depth: int, alpha: float, beta: float, maximizing_player: bool):
        """Implementacja algorytmu alpha-beta pruning."""
        winner = game.check_winner()
        
        # Warunki końcowe
        if winner is not None:
            return self.evaluate_terminal(game, winner), None
        
        if depth == 0:
            return self.evaluate_position(game), None
        
        if game.is_full():
            return 0, None  # Remis
        
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0, None
        
        # Sortuj ruchy - preferuj środek planszy
        valid_moves = self.order_moves(game, valid_moves)
        
        best_column = valid_moves[0]
        
        if maximizing_player:
            max_eval = float('-inf')
            for col in valid_moves:
                game_copy = self.make_move_copy(game, col)
                eval_score, _ = self.alpha_beta(game_copy, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_column = col
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return max_eval, best_column
        else:
            min_eval = float('inf')
            for col in valid_moves:
                game_copy = self.make_move_copy(game, col)
                eval_score, _ = self.alpha_beta(game_copy, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_column = col
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            return min_eval, best_column

    def order_moves(self, game: Game, moves: list[int]) -> list[int]:
        """Sortuje ruchy - preferuje środek planszy."""
        center = game.n_columns // 2
        return sorted(moves, key=lambda x: abs(x - center))

    def evaluate_terminal(self, game: Game, winner: int) -> float:
        """Ocenia pozycję końcową."""
        if winner == game.current_player:
            return -10000  # Przegraliśmy (to jest zły wynik dla nas)
        else:
            return 10000   # Wygraliśmy

    def get_valid_moves(self, game: Game) -> list[int]:
        """Zwraca listę dostępnych kolumn."""
        return [col for col in range(game.n_columns) if len(game.board[col]) < game.n_rows]

    def make_move_copy(self, game: Game, column: int) -> Game:
        """Tworzy kopię gry z wykonanym ruchem."""
        game_copy = copy.deepcopy(game)
        game_copy.board[column].append(game_copy.current_player)
        game_copy.move_history.append(column)
        game_copy.current_player = 1 - game_copy.current_player
        return game_copy

    def evaluate_position(self, game: Game) -> float:
        """Ocenia pozycję na planszy."""
        score = 0
        
        # Ocena dla obu graczy
        my_player = game.current_player
        opp_player = 1 - my_player
        
        # Ocena wszystkich możliwych okien
        score += self.evaluate_all_windows(game, my_player) * 1.0
        score -= self.evaluate_all_windows(game, opp_player) * 1.1  # Nieco wyższa waga dla obrony
        
        # Bonus za środek planszy
        center_col = game.n_columns // 2
        center_count = sum(1 for piece in game.board[center_col] if piece == my_player)
        score += center_count * 10
        
        return score

    def evaluate_all_windows(self, game: Game, player: int) -> float:
        """Ocenia wszystkie możliwe okna dla danego gracza."""
        score = 0
        win_len = game.winning_length
        
        # Sprawdź wszystkie możliwe okna poziome
        for row in range(game.n_rows):
            for col in range(game.n_columns - win_len + 1):
                window = self.get_horizontal_window(game, row, col, win_len)
                score += self.evaluate_window(window, player)
        
        # Sprawdź wszystkie możliwe okna pionowe
        for col in range(game.n_columns):
            for row in range(game.n_rows - win_len + 1):
                window = self.get_vertical_window(game, col, row, win_len)
                score += self.evaluate_window(window, player)
        
        # Sprawdź wszystkie możliwe okna ukośne (\ direction)
        for row in range(game.n_rows - win_len + 1):
            for col in range(game.n_columns - win_len + 1):
                window = self.get_diagonal_window(game, row, col, win_len, 1)
                score += self.evaluate_window(window, player)
        
        # Sprawdź wszystkie możliwe okna ukośne (/ direction)
        for row in range(win_len - 1, game.n_rows):
            for col in range(game.n_columns - win_len + 1):
                window = self.get_diagonal_window(game, row, col, win_len, -1)
                score += self.evaluate_window(window, player)
        
        return score

    def get_horizontal_window(self, game: Game, row: int, start_col: int, length: int) -> list:
        """Pobiera poziome okno."""
        window = []
        for col in range(start_col, start_col + length):
            if len(game.board[col]) > row:
                window.append(game.board[col][row])
            else:
                window.append(None)
        return window

    def get_vertical_window(self, game: Game, col: int, start_row: int, length: int) -> list:
        """Pobiera pionowe okno."""
        window = []
        for row in range(start_row, start_row + length):
            if len(game.board[col]) > row:
                window.append(game.board[col][row])
            else:
                window.append(None)
        return window

    def get_diagonal_window(self, game: Game, start_row: int, start_col: int, length: int, direction: int) -> list:
        """Pobiera ukośne okno. direction: 1 dla \, -1 dla /"""
        window = []
        for i in range(length):
            row = start_row + (i * direction)
            col = start_col + i
            if 0 <= row < game.n_rows and 0 <= col < game.n_columns and len(game.board[col]) > row:
                window.append(game.board[col][row])
            else:
                window.append(None)
        return window

    def evaluate_window(self, window: list, player: int) -> float:
        """Ocenia pojedyncze okno z lepszą heurystyką."""
        score = 0
        opp_player = 1 - player
        
        player_count = window.count(player)
        opp_count = window.count(opp_player)
        empty_count = window.count(None)
        
        # Jeśli przeciwnik już ma kawałki w tym oknie, nie możemy wygrać
        if opp_count > 0:
            return 0
        
        # Ocena na podstawie liczby naszych kawałków
        if player_count == 4:
            score += 1000
        elif player_count == 3 and empty_count == 1:
            score += 50
        elif player_count == 2 and empty_count == 2:
            score += 10
        elif player_count == 1 and empty_count == 3:
            score += 1
        
        return score
    
# Stwórz nową grę
game = Game()

# Stwórz gracza AI
ai_player = Player()

# Przykładowa gra 
winner = None

while winner is None:
    game.print_board()
    if game.current_player == 0:
        move = int(input())
        game.make_move(move)
    else:
        best_move = ai_player.make_move(game)
        game.make_move(best_move)
    winner = game.check_winner()

game.print_board()
print(f"wygral gracz {winner}")