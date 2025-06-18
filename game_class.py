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
    Klasa reprezentująca program grający z algorytmem alpha-beta pruning.
    """
    def __init__(self):
        self.team_name = "1"
        self.team_members = ["Kacper Daniel", "Paweł Karwecki", "Tadeusz Jagniewski"]
        self.max_depth = 7

    def make_move(self, game: Game) -> int:
        """Zwraca kolumnę dla najlepszego ruchu."""
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        _, best_column = self.alpha_beta(game, self.max_depth, float('-inf'), float('inf'), True)
        
        if best_column is None or best_column not in valid_moves:
            return random.choice(valid_moves)
        
        return best_column

    def alpha_beta(self, game: Game, depth: int, alpha: float, beta: float, maximizing_player: bool):
        """Implementacja algorytmu alpha-beta pruning."""
        winner = game.check_winner()
        if winner is not None or depth == 0:
            return self.evaluate_position(game, winner), None
        
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return self.evaluate_position(game, winner), None
        
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
                    break
            
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
                    break
            
            return min_eval, best_column

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

    def evaluate_position(self, game: Game, winner: int) -> float:
        """Ocenia pozycję na planszy."""
        if winner is not None:
            if winner == game.current_player:
                return -1000
            else:
                return 1000
        
        score = 0
        
        # Preferuj środek planszy
        center_col = game.n_columns // 2
        for row_idx in range(len(game.board[center_col])):
            if game.board[center_col][row_idx] == game.current_player:
                score += 3
        
        # Ocena potencjalnych linii
        score += self.evaluate_windows(game, game.current_player)
        score -= self.evaluate_windows(game, 1 - game.current_player)
        
        return score

    def evaluate_windows(self, game: Game, player: int) -> float:
        """Ocenia potencjalne okna wygrywające."""
        score = 0
        win_len = game.winning_length
        
        # Poziome okna
        for row in range(game.n_rows):
            for col in range(game.n_columns - win_len + 1):
                window = []
                for c in range(col, col + win_len):
                    if len(game.board[c]) > row:
                        window.append(game.board[c][row])
                    else:
                        window.append(None)
                score += self.evaluate_window(window, player)
        
        # Pionowe okna
        for col in range(game.n_columns):
            for row in range(game.n_rows - win_len + 1):
                window = []
                for r in range(row, row + win_len):
                    if len(game.board[col]) > r:
                        window.append(game.board[col][r])
                    else:
                        window.append(None)
                score += self.evaluate_window(window, player)
        
        return score

    def evaluate_window(self, window: list, player: int) -> float:
        """Ocenia pojedyncze okno."""
        score = 0
        opp_player = 1 - player
        
        player_count = window.count(player)
        opp_count = window.count(opp_player)
        empty_count = window.count(None)
        
        if player_count == 4:
            score += 100
        elif player_count == 3 and empty_count == 1:
            score += 10
        elif player_count == 2 and empty_count == 2:
            score += 2
        
        if opp_count == 4:
            score -= 200
        elif opp_count == 3 and empty_count == 1:
            score -= 20
        
        return score

# Stwórz nową grę
game = Game()

# Stwórz gracza AI
ai_player = Player()

# Przykładowa gra 
winner = None
i = 0
while winner is None and i < 15:
    game.make_move(random.randint(0, game.n_columns - 1))
    winner = game.check_winner()
    i += 1

if winner is not None:
    game.print_board()
    print(f"wygral gracz {winner}")
    
else:
    game.print_board()
    best_move = ai_player.make_move(game)
    print(f"Wybrana kolumna: {best_move}")

    # Wykonaj ruch
    game.make_move(best_move)
    game.print_board()

    winner = game.check_winner()
    if winner is not None:
        print(f"wygral gracz {winner}")