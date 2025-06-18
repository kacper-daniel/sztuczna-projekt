import random
import copy
import time
import math
from typing import Optional, Tuple, List, Dict
from collections import defaultdict

class Game:
    """
    Klasa reprezentująca rozgrywkę Connect 4 z grawitacją.
    """
    def __init__(self, n_rows: int = 7, n_columns: int = 7, winning_length: int = 4):
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
    
    def undo_move(self, column: int):
        """Cofa ruch - dla optymalizacji bez kopiowania."""
        if self.board[column]:
            self.board[column].pop()
            self.move_history.pop()
            self.current_player = 1 - self.current_player
    
    def is_terminal(self) -> bool:
        """Sprawdza czy gra się skończyła."""
        return self.check_winner() is not None or self.is_board_full()
    
    def is_board_full(self) -> bool:
        """Sprawdza czy plansza jest pełna."""
        return all(len(col) >= self.n_rows for col in self.board)
    
    def check_winner(self) -> Optional[int]:
        """Sprawdza czy ktoś wygrał grę - zoptymalizowana wersja."""
        # Sprawdź tylko ostatni ruch zamiast całej planszy
        if not self.move_history:
            return None
            
        last_col = self.move_history[-1]
        last_row = len(self.board[last_col]) - 1
        last_player = self.board[last_col][last_row]
        
        return self.check_winner_from_position(last_col, last_row, last_player)
    
    def check_winner_from_position(self, col: int, row: int, player: int) -> Optional[int]:
        """Sprawdza zwycięstwo od konkretnej pozycji."""
        directions = [
            (0, 1),   # poziomo
            (1, 0),   # pionowo  
            (1, 1),   # ukośnie \
            (1, -1)   # ukośnie /
        ]
        
        for dx, dy in directions:
            count = 1  # Zlicz aktualny pionek
            
            # Sprawdź w jedną stronę
            for i in range(1, self.winning_length):
                new_col = col + i * dx
                new_row = row + i * dy
                if not self.is_valid_position(new_col, new_row) or \
                   self.board[new_col][new_row] != player:
                    break
                count += 1
            
            # Sprawdź w drugą stronę
            for i in range(1, self.winning_length):
                new_col = col - i * dx
                new_row = row - i * dy
                if not self.is_valid_position(new_col, new_row) or \
                   self.board[new_col][new_row] != player:
                    break
                count += 1
            
            if count >= self.winning_length:
                return player
        
        return None
    
    def is_valid_position(self, col: int, row: int) -> bool:
        """Sprawdza czy pozycja jest prawidłowa."""
        return (0 <= col < self.n_columns and 
                0 <= row < len(self.board[col]))

    # Pozostałe metody check_* zachowane dla kompatybilności
    def check_line_vertical(self, column: list[int], player: int, winning_length: int) -> bool:
        if len(column) < winning_length:
            return False
        count = 0
        for symbol in column:
            if symbol == player:
                count += 1
                if count >= winning_length:
                    return True
            else:
                count = 0
        return False

    def check_line_horizontal(self, row: int, player: int, winning_length: int) -> bool:
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
        # Sprawdź ukos \
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
        
        # Sprawdź ukos /
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

class UnbeatableAI:
    """NIEPRZEZWYCIĘŻONA wersja AI - używa zaawansowanych technik."""
    
    def __init__(self, max_depth: int = 12):
        self.team_name = "UNBEATABLE AI"
        self.team_members = ["Deep Blue Reborn"]
        self.max_depth = max_depth
        
        # Statystyki
        self.nodes_visited = 0
        self.pruning_count = 0
        self.search_time = 0
        self.current_depth = 0
        
        # Zaawansowane struktury danych
        self.transposition_table = {}
        self.killer_moves = [[] for _ in range(max_depth + 1)]
        self.history_table = defaultdict(int)
        
        # Prekalkulowane wzorce
        self.threat_patterns = self.precompute_threat_patterns()
        
        # Opening book - najlepsze pierwsze ruchy
        self.opening_book = {
            7: [3, 2, 4, 1, 5, 0, 6],  # Dla planszy 7x7
            6: [2, 3, 1, 4, 0, 5],     # Dla planszy 6x6
            5: [2, 1, 3, 0, 4]         # Dla planszy 5x5
        }
        
    def precompute_threat_patterns(self) -> Dict:
        """Prekalkuluje wzorce zagrożeń."""
        patterns = {
            'winning_threats': [],
            'blocking_threats': [],
            'fork_threats': []
        }
        # Można rozszerzyć o konkretne wzorce
        return patterns
        
    def reset_stats(self):
        """Resetuje statystyki przeszukiwania."""
        self.nodes_visited = 0
        self.pruning_count = 0
        self.killer_moves = [[] for _ in range(self.max_depth + 1)]

    def make_move(self, game: Game) -> int:
        """Zwraca najlepszy ruch używając wszystkich technik."""
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0
        
        # Opening book - pierwsze ruchy
        if len(game.move_history) <= 2:
            return self.get_opening_move(game, valid_moves)
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        # Sprawdź natychmiastowe zwycięstwo
        winning_move = self.find_winning_move(game, valid_moves)
        if winning_move is not None:
            print("🎯 Znaleziono wygrywający ruch!")
            return winning_move
        
        # Sprawdź czy trzeba blokować przeciwnika
        blocking_move = self.find_blocking_move(game, valid_moves)
        if blocking_move is not None:
            print("🛡️ Blokowanie przeciwnika!")
            return blocking_move
        
        # Resetuj statystyki
        self.reset_stats()
        self.current_depth = self.max_depth
        
        # Iterative deepening - zwiększaj głębokość stopniowo
        best_move = valid_moves[0]
        start_time = time.time()
        
        for depth in range(4, self.max_depth + 1, 2):
            if time.time() - start_time > 5.0:  # Time limit 5 sekund
                break
                
            self.current_depth = depth
            try:
                _, move = self.alpha_beta_with_enhancements(
                    game, depth, float('-inf'), float('inf'), True, 0
                )
                if move is not None:
                    best_move = move
                    print(f"📊 Głębokość {depth}: wybrano kolumnę {move}")
            except KeyboardInterrupt:
                break
        
        end_time = time.time()
        self.search_time = end_time - start_time
        
        # Wyświetl statystyki
        self.print_advanced_stats()
        
        return best_move if best_move in valid_moves else random.choice(valid_moves)

    def get_opening_move(self, game: Game, valid_moves: List[int]) -> int:
        """Zwraca najlepszy ruch z opening book."""
        if game.n_columns in self.opening_book:
            for move in self.opening_book[game.n_columns]:
                if move in valid_moves:
                    print(f"📚 Opening book: kolumna {move}")
                    return move
        
        # Fallback - środek planszy
        center = game.n_columns // 2
        return center if center in valid_moves else valid_moves[0]

    def find_winning_move(self, game: Game, valid_moves: List[int]) -> Optional[int]:
        """Znajduje ruch dający natychmiastowe zwycięstwo."""
        for col in valid_moves:
            if self.simulate_move_wins(game, col, game.current_player):
                return col
        return None

    def find_blocking_move(self, game: Game, valid_moves: List[int]) -> Optional[int]:
        """Znajduje ruch blokujący zwycięstwo przeciwnika."""
        opponent = 1 - game.current_player
        for col in valid_moves:
            # Symuluj ruch przeciwnika
            if self.simulate_move_wins(game, col, opponent):
                return col
        return None

    def simulate_move_wins(self, game: Game, col: int, player: int) -> bool:
        """Symuluje ruch i sprawdza czy daje zwycięstwo."""
        if len(game.board[col]) >= game.n_rows:
            return False
        
        # Wykonaj ruch
        row = len(game.board[col])
        game.board[col].append(player)
        
        # Sprawdź zwycięstwo
        wins = game.check_winner_from_position(col, row, player) == player
        
        # Cofnij ruch
        game.board[col].pop()
        
        return wins

    def alpha_beta_with_enhancements(self, game: Game, depth: int, alpha: float, beta: float, 
                                   maximizing_player: bool, ply: int) -> Tuple[float, Optional[int]]:
        """Zaawansowana wersja alpha-beta z wszystkimi optymalizacjami."""
        self.nodes_visited += 1
        
        # Transposition table lookup
        board_hash = self.hash_board(game)
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                if entry['type'] == 'exact':
                    return entry['value'], entry['move']
                elif entry['type'] == 'lower' and entry['value'] >= beta:
                    return entry['value'], entry['move']
                elif entry['type'] == 'upper' and entry['value'] <= alpha:
                    return entry['value'], entry['move']
        
        # Terminal node check
        winner = game.check_winner()
        if winner is not None:
            score = self.evaluate_terminal(game, winner, depth, ply)
            return score, None
        
        if depth == 0 or game.is_board_full():
            score = self.evaluate_position_advanced(game)
            return score, None
        
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0, None
        
        # Advanced move ordering
        valid_moves = self.order_moves_advanced(game, valid_moves, ply)
        
        best_move = valid_moves[0]
        original_alpha = alpha
        
        if maximizing_player:
            max_eval = float('-inf')
            for col in valid_moves:
                # Make move without copying
                game.board[col].append(game.current_player)
                game.move_history.append(col)
                game.current_player = 1 - game.current_player
                
                eval_score, _ = self.alpha_beta_with_enhancements(
                    game, depth - 1, alpha, beta, False, ply + 1
                )
                
                # Undo move
                game.undo_move(col)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
                
                alpha = max(alpha, eval_score)
                
                # Alpha-beta pruning with killer move update
                if beta <= alpha:
                    self.pruning_count += 1
                    self.update_killer_moves(col, ply)
                    self.history_table[(col, game.current_player)] += depth * depth
                    break
            
            # Store in transposition table
            self.store_transposition(board_hash, depth, max_eval, best_move, original_alpha, beta)
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for col in valid_moves:
                # Make move without copying
                game.board[col].append(game.current_player)
                game.move_history.append(col)
                game.current_player = 1 - game.current_player
                
                eval_score, _ = self.alpha_beta_with_enhancements(
                    game, depth - 1, alpha, beta, True, ply + 1
                )
                
                # Undo move
                game.undo_move(col)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
                
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    self.pruning_count += 1
                    self.update_killer_moves(col, ply)
                    self.history_table[(col, game.current_player)] += depth * depth
                    break
            
            self.store_transposition(board_hash, depth, min_eval, best_move, original_alpha, beta)
            return min_eval, best_move

    def order_moves_advanced(self, game: Game, valid_moves: List[int], ply: int) -> List[int]:
        """Zaawansowane sortowanie ruchów."""
        move_scores = []
        center = game.n_columns // 2
        
        for col in valid_moves:
            score = 0
            
            # 1. Sprawdź wygrywające ruchy (najwyższy priorytet)
            if self.simulate_move_wins(game, col, game.current_player):
                score += 100000
            
            # 2. Sprawdź blokowanie przeciwnika
            if self.simulate_move_wins(game, col, 1 - game.current_player):
                score += 50000
            
            # 3. Killer moves
            if col in self.killer_moves[ply]:
                score += 10000
            
            # 4. History heuristic
            score += self.history_table.get((col, game.current_player), 0)
            
            # 5. Kontrola środka
            score += (center - abs(col - center)) * 100
            
            # 6. Analiza zagrożeń (threats)
            score += self.analyze_column_threats(game, col)
            
            # 7. Pozycyjne preferencje
            score += self.evaluate_column_structure(game, col)
            
            move_scores.append((score, col))
        
        # Sortuj malejąco
        move_scores.sort(reverse=True)
        return [col for _, col in move_scores]

    def analyze_column_threats(self, game: Game, col: int) -> float:
        """Analizuje zagrożenia w kolumnie."""
        if len(game.board[col]) >= game.n_rows:
            return -1000  # Pełna kolumna
        
        score = 0
        row = len(game.board[col])
        
        # Symuluj postawienie pionka
        game.board[col].append(game.current_player)
        
        # Sprawdź wszystkie kierunki dla potencjalnych zagrożeń
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            # Zlicz pionki gracza w tym kierunku
            count = self.count_in_direction(game, col, row, dx, dy, game.current_player)
            if count >= 2:
                score += count * 50
            
            # Zlicz zagrożenia przeciwnika
            opp_count = self.count_in_direction(game, col, row, dx, dy, 1 - game.current_player)
            if opp_count >= 2:
                score += opp_count * 30
        
        # Cofnij symulację
        game.board[col].pop()
        
        return score

    def count_in_direction(self, game: Game, start_col: int, start_row: int, 
                          dx: int, dy: int, player: int) -> int:
        """Liczy pionki gracza w danym kierunku."""
        count = 1  # Początkowy pionek
        
        # Sprawdź w jedną stronę
        for i in range(1, game.winning_length):
            col = start_col + i * dx
            row = start_row + i * dy
            if not self.is_valid_and_player(game, col, row, player):
                break
            count += 1
        
        # Sprawdź w drugą stronę
        for i in range(1, game.winning_length):
            col = start_col - i * dx
            row = start_row - i * dy
            if not self.is_valid_and_player(game, col, row, player):
                break
            count += 1
        
        return count

    def is_valid_and_player(self, game: Game, col: int, row: int, player: int) -> bool:
        """Sprawdza czy pozycja jest prawidłowa i zawiera pionek gracza."""
        return (0 <= col < game.n_columns and 
                0 <= row < len(game.board[col]) and
                game.board[col][row] == player)

    def evaluate_column_structure(self, game: Game, col: int) -> float:
        """Ocenia strukturę kolumny."""
        score = 0
        height = len(game.board[col])
        
        # Preferuj niższe pozycje
        score += (game.n_rows - height) * 10
        
        # Unikaj tworzenia dziur
        if height > 0:
            # Sprawdź sąsiednie kolumny
            for neighbor in [col - 1, col + 1]:
                if 0 <= neighbor < game.n_columns:
                    neighbor_height = len(game.board[neighbor])
                    height_diff = abs(height - neighbor_height)
                    if height_diff > 2:
                        score -= 20  # Kara za duże różnice wysokości
        
        return score

    def update_killer_moves(self, move: int, ply: int):
        """Aktualizuje killer moves."""
        if ply < len(self.killer_moves):
            if move not in self.killer_moves[ply]:
                self.killer_moves[ply].append(move)
                if len(self.killer_moves[ply]) > 2:  # Zachowaj tylko 2 najlepsze
                    self.killer_moves[ply].pop(0)

    def store_transposition(self, board_hash: str, depth: int, value: float, 
                          best_move: int, alpha: float, beta: float):
        """Zapisuje pozycję w transposition table."""
        entry_type = 'exact'
        if value <= alpha:
            entry_type = 'upper'
        elif value >= beta:
            entry_type = 'lower'
        
        self.transposition_table[board_hash] = {
            'depth': depth,
            'value': value,
            'move': best_move,
            'type': entry_type
        }
        
        # Ogranicz rozmiar tabeli
        if len(self.transposition_table) > 100000:
            # Usuń 25% najstarszych wpisów
            items = list(self.transposition_table.items())
            self.transposition_table = dict(items[25000:])

    def hash_board(self, game: Game) -> str:
        """Szybka funkcja hash planszy."""
        # Używamy tuple dla lepszej wydajności
        board_tuple = tuple(tuple(col) for col in game.board)
        return str(hash((board_tuple, game.current_player)))

    def get_valid_moves(self, game: Game) -> List[int]:
        """Zwraca listę dostępnych kolumn."""
        return [col for col in range(game.n_columns) if len(game.board[col]) < game.n_rows]

    def evaluate_terminal(self, game: Game, winner: int, depth: int, ply: int) -> float:
        """Ocenia pozycję końcową."""
        if winner == game.current_player:
            return -10000 - depth + ply  # Im głębiej, tym gorzej
        else:
            return 10000 + depth - ply   # Im płycej, tym lepiej

    def evaluate_position_advanced(self, game: Game) -> float:
        """Zaawansowana funkcja ewaluacyjna."""
        score = 0
        current_player = game.current_player
        opponent = 1 - current_player
        
        # 1. Kontrola środka (zwiększona waga)
        center_score = self.evaluate_center_control(game, current_player)
        score += center_score * 1.5
        score -= self.evaluate_center_control(game, opponent) * 1.5
        
        # 2. Ocena wszystkich wzorców wygrywających
        pattern_score = self.evaluate_winning_patterns(game, current_player)
        score += pattern_score
        score -= self.evaluate_winning_patterns(game, opponent) * 1.1  # Przeciwnik nieco ważniejszy
        
        # 3. Ocena struktury i pozycji
        structure_score = self.evaluate_board_structure(game, current_player)
        score += structure_score
        score -= self.evaluate_board_structure(game, opponent)
        
        # 4. Ocena potencjalnych zagrożeń
        threat_score = self.evaluate_threats(game, current_player)
        score += threat_score
        score -= self.evaluate_threats(game, opponent) * 1.2
        
        # 5. Ocena mobilności (dostępne ruchy)
        mobility_score = self.evaluate_mobility(game, current_player)
        score += mobility_score
        score -= self.evaluate_mobility(game, opponent)
        
        return score

    def evaluate_center_control(self, game: Game, player: int) -> float:
        """Ocenia kontrolę nad środkiem planszy."""
        score = 0
        center = game.n_columns // 2
        
        # Główna kolumna środkowa
        for piece in game.board[center]:
            if piece == player:
                score += 5
        
        # Kolumny blisko środka
        for offset in [1, 2]:
            for col in [center - offset, center + offset]:
                if 0 <= col < game.n_columns:
                    weight = 3 / offset  # Im dalej od środka, tym mniejsza waga
                    for piece in game.board[col]:
                        if piece == player:
                            score += weight
        
        return score

    def evaluate_winning_patterns(self, game: Game, player: int) -> float:
        """Ocenia wzorce wygrywające."""
        score = 0
        win_len = game.winning_length
        
        # Dla każdej możliwej linii wygrywającej
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(game.n_rows):
            for col in range(game.n_columns):
                for dx, dy in directions:
                    if self.can_form_line(game, col, row, dx, dy, win_len):
                        window = self.get_line_window(game, col, row, dx, dy, win_len)
                        score += self.evaluate_window_advanced(window, player)
        
        return score

    def can_form_line(self, game: Game, start_col: int, start_row: int, 
                     dx: int, dy: int, length: int) -> bool:
        """Sprawdza czy można utworzyć linię o danej długości."""
        end_col = start_col + (length - 1) * dx
        end_row = start_row + (length - 1) * dy
        
        return (0 <= end_col < game.n_columns and 
                0 <= end_row < game.n_rows)

    def get_line_window(self, game: Game, start_col: int, start_row: int,
                       dx: int, dy: int, length: int) -> List:
        """Pobiera okno linii."""
        window = []
        for i in range(length):
            col = start_col + i * dx
            row = start_row + i * dy
            
            if len(game.board[col]) > row:
                window.append(game.board[col][row])
            else:
                window.append(None)  # Puste pole
        
        return window

    def evaluate_window_advanced(self, window: List, player: int) -> float:
        """Zaawansowana ocena okna."""
        score = 0
        opponent = 1 - player
        
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(None)
        
        # Jeśli przeciwnik blokuje, okno nie ma wartości
        if opponent_count > 0:
            return 0
        
        # Ocena na podstawie wzorców
        if player_count == 4:
            score += 10000  # Wygrana
        elif player_count == 3 and empty_count == 1:
            score += 500    # Zagrożenie
        elif player_count == 2 and empty_count == 2:
            # Sprawdź rozkład pustych pól
            if self.is_open_window(window):
                score += 50   # Otwarte okno
            else:
                score += 10   # Zamknięte okno
        elif player_count == 1 and empty_count == 3:
            score += 1      # Początek formacji
        
        return score

    def is_open_window(self, window: List) -> bool:
        """Sprawdza czy okno jest otwarte (puste pola po bokach)."""
        if len(window) < 4:
            return False
        return window[0] is None or window[-1] is None

    def evaluate_board_structure(self, game: Game, player: int) -> float:
        """Ocenia strukturę planszy."""
        score = 0
        
        # Preferuj niskie pozycje (stabilniejsze)
        for col in range(game.n_columns):
            for row, piece in enumerate(game.board[col]):
                if piece == player:
                    height_bonus = (game.n_rows - row) * 0.5
                    score += height_bonus
        
        # Preferuj równomierny rozkład pionków
        for col in range(game.n_columns - 1):
            height_diff = abs(len(game.board[col]) - len(game.board[col + 1]))
            if height_diff > 2:
                score -= 5  # Kara za nierównomierność
        
        return score

    def evaluate_threats(self, game: Game, player: int) -> float:
        """Ocenia zagrożenia i możliwości."""
        score = 0
        
        # Sprawdź wszystkie pozycje gdzie gracz może postawić pionek
        for col in range(game.n_columns):
            if len(game.board[col]) < game.n_rows:
                row = len(game.board[col])
                
                # Symuluj postawienie pionka
                game.board[col].append(player)
                
                # Sprawdź czy tworzy zagrożenia
                threat_level = self.analyze_position_threats(game, col, row, player)
                score += threat_level
                
                # Cofnij symulację
                game.board[col].pop()
        
        return score

    def analyze_position_threats(self, game: Game, col: int, row: int, player: int) -> float:
        """Analizuje zagrożenia z danej pozycji."""
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            # Sprawdź linie w obu kierunkach
            line_strength = self.calculate_line_strength(game, col, row, dx, dy, player)
            
            if line_strength >= game.winning_length:
                score += 1000  # Natychmiastowe zwycięstwo
            elif line_strength == game.winning_length - 1:
                score += 100   # Bezpośrednie zagrożenie
            elif line_strength == game.winning_length - 2:
                score += 20    # Potencjalne zagrożenie
            else:
                score += line_strength  # Podstawowa wartość
        
        return score

    def calculate_line_strength(self, game: Game, col: int, row: int, 
                               dx: int, dy: int, player: int) -> int:
        """Oblicza siłę linii w danym kierunku."""
        count = 1  # Aktualny pionek
        
        # Sprawdź w jedną stronę
        for i in range(1, game.winning_length):
            new_col = col + i * dx
            new_row = row + i * dy
            if (0 <= new_col < game.n_columns and 
                0 <= new_row < len(game.board[new_col]) and
                game.board[new_col][new_row] == player):
                count += 1
            else:
                break
        
        # Sprawdź w drugą stronę
        for i in range(1, game.winning_length):
            new_col = col - i * dx
            new_row = row - i * dy
            if (0 <= new_col < game.n_columns and 
                0 <= new_row < len(game.board[new_col]) and
                game.board[new_col][new_row] == player):
                count += 1
            else:
                break
        
        return count

    def evaluate_mobility(self, game: Game, player: int) -> float:
        """Ocenia mobilność gracza."""
        mobility = 0
        
        # Liczba dostępnych kolumn
        available_columns = sum(1 for col in range(game.n_columns) 
                               if len(game.board[col]) < game.n_rows)
        mobility += available_columns * 2
        
        # Ocena jakości dostępnych ruchów
        for col in range(game.n_columns):
            if len(game.board[col]) < game.n_rows:
                # Dodaj bonus za ruchy w środku planszy
                center_distance = abs(col - game.n_columns // 2)
                mobility += (game.n_columns - center_distance) * 0.5
        
        return mobility

    def print_advanced_stats(self):
        """Wyświetla zaawansowane statystyki przeszukiwania."""
        print("\n" + "="*60)
        print("🧠 STATYSTYKI UNBEATABLE AI")
        print("="*60)
        print(f"🔍 Odwiedzone węzły: {self.nodes_visited:,}")
        print(f"✂️  Przycinania α-β: {self.pruning_count:,}")
        print(f"⏱️  Czas przeszukiwania: {self.search_time:.3f}s")
        print(f"🏆 Transposition table: {len(self.transposition_table):,} wpisów")
        
        if self.search_time > 0:
            nodes_per_second = self.nodes_visited / self.search_time
            print(f"⚡ Węzłów/sekundę: {nodes_per_second:,.0f}")
        
        pruning_efficiency = (self.pruning_count / max(self.nodes_visited, 1)) * 100
        print(f"📊 Skuteczność przycinania: {pruning_efficiency:.1f}%")
        print("="*60)

class HumanPlayer:
    """Klasa reprezentująca gracza człowieka."""
    
    def __init__(self):
        self.team_name = "Human Player"
        self.team_members = ["You"]

    def make_move(self, game: Game) -> int:
        """Pobiera ruch od gracza."""
        game.print_board()
        
        valid_moves = [col for col in range(game.n_columns) 
                      if len(game.board[col]) < game.n_rows]
        
        while True:
            try:
                print(f"\nDostępne kolumny: {valid_moves}")
                move = input(f"Gracz {'X' if game.current_player == 0 else 'O'}, "
                           f"wybierz kolumnę (0-{game.n_columns-1}): ").strip()
                
                if move.lower() in ['q', 'quit', 'exit']:
                    print("Rezygnacja!")
                    return -1
                
                col = int(move)
                if col in valid_moves:
                    return col
                else:
                    print(f"❌ Nieprawidłowa kolumna! Wybierz z: {valid_moves}")
                    
            except ValueError:
                print("❌ Wprowadź liczbę!")
            except KeyboardInterrupt:
                print("\nGra przerwana!")
                return -1

class SimpleAI:
    """Prosty AI do testów i porównań."""
    
    def __init__(self, depth: int = 6):
        self.team_name = f"Simple AI (depth {depth})"
        self.team_members = ["Basic Bot"]
        self.max_depth = depth
        self.nodes_visited = 0

    def make_move(self, game: Game) -> int:
        """Zwraca ruch używając prostego minimax."""
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0
        
        # Sprawdź natychmiastowe zwycięstwo
        for col in valid_moves:
            if self.simulate_move_wins(game, col, game.current_player):
                return col
        
        # Sprawdź blokowanie
        for col in valid_moves:
            if self.simulate_move_wins(game, col, 1 - game.current_player):
                return col
        
        # Użyj minimax
        self.nodes_visited = 0
        _, best_move = self.minimax(game, self.max_depth, True)
        
        print(f"Simple AI - węzły: {self.nodes_visited}")
        return best_move if best_move in valid_moves else random.choice(valid_moves)

    def minimax(self, game: Game, depth: int, maximizing: bool) -> Tuple[float, int]:
        """Podstawowy minimax."""
        self.nodes_visited += 1
        
        if depth == 0 or game.is_terminal():
            return self.evaluate_simple(game), None
        
        valid_moves = self.get_valid_moves(game)
        if not valid_moves:
            return 0, None
        
        best_move = valid_moves[0]
        
        if maximizing:
            max_eval = float('-inf')
            for col in valid_moves:
                game.board[col].append(game.current_player)
                game.move_history.append(col)
                game.current_player = 1 - game.current_player
                
                eval_score, _ = self.minimax(game, depth - 1, False)
                
                game.undo_move(col)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = col
            
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for col in valid_moves:
                game.board[col].append(game.current_player)
                game.move_history.append(col)
                game.current_player = 1 - game.current_player
                
                eval_score, _ = self.minimax(game, depth - 1, True)
                
                game.undo_move(col)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = col
            
            return min_eval, best_move

    def evaluate_simple(self, game: Game) -> float:
        """Prosta funkcja ewaluacyjna."""
        winner = game.check_winner()
        if winner == game.current_player:
            return -1000
        elif winner == (1 - game.current_player):
            return 1000
        
        # Podstawowa ocena pozycji
        score = 0
        center = game.n_columns // 2
        
        # Bonus za środek
        for piece in game.board[center]:
            if piece == game.current_player:
                score += 3
            else:
                score -= 3
        
        return score

    def get_valid_moves(self, game: Game) -> List[int]:
        """Zwraca dostępne ruchy."""
        return [col for col in range(game.n_columns) if len(game.board[col]) < game.n_rows]

    def simulate_move_wins(self, game: Game, col: int, player: int) -> bool:
        """Sprawdza czy ruch daje zwycięstwo."""
        if len(game.board[col]) >= game.n_rows:
            return False
        
        row = len(game.board[col])
        game.board[col].append(player)
        
        wins = game.check_winner_from_position(col, row, player) == player
        
        game.board[col].pop()
        return wins

class GameManager:
    """Menedżer gier i turniejów."""
    
    def __init__(self):
        self.games_played = 0
        self.results = []

    def play_single_game(self, player1, player2, game_config: Dict = None) -> Dict:
        """Rozgrywa pojedynczą grę."""
        if game_config is None:
            game_config = {'rows': 7, 'columns': 7, 'winning_length': 4}
        
        game = Game(game_config['rows'], game_config['columns'], game_config['winning_length'])
        players = [player1, player2]
        
        print(f"\n🎮 NOWA GRA: {player1.team_name} vs {player2.team_name}")
        print(f"Plansza: {game_config['rows']}x{game_config['columns']}, "
              f"Do wygranej: {game_config['winning_length']}")
        
        start_time = time.time()
        move_count = 0
        
        while not game.is_terminal():
            current_player_obj = players[game.current_player]
            
            try:
                move = current_player_obj.make_move(game)
                
                if move == -1:  # Rezygnacja
                    winner = 1 - game.current_player
                    result = {
                        'winner': winner,
                        'reason': 'resignation',
                        'moves': move_count,
                        'time': time.time() - start_time,
                        'player1': player1.team_name,
                        'player2': player2.team_name
                    }
                    print(f"🏆 {players[winner].team_name} wygrywa przez rezygnację!")
                    return result
                
                if game.make_move(move):
                    move_count += 1
                    
                    # Sprawdź zwycięstwo
                    winner = game.check_winner()
                    if winner is not None:
                        game.print_board()
                        result = {
                            'winner': winner,
                            'reason': 'victory',
                            'moves': move_count,
                            'time': time.time() - start_time,
                            'player1': player1.team_name,
                            'player2': player2.team_name
                        }
                        print(f"🏆 {players[winner].team_name} wygrywa!")
                        return result
                    
                    # Sprawdź remis
                    if game.is_board_full():
                        game.print_board()
                        result = {
                            'winner': None,
                            'reason': 'draw',
                            'moves': move_count,
                            'time': time.time() - start_time,
                            'player1': player1.team_name,
                            'player2': player2.team_name
                        }
                        print("🤝 Remis!")
                        return result
                else:
                    print("❌ Nieprawidłowy ruch!")
                    
            except Exception as e:
                print(f"❌ Błąd gracza {current_player_obj.team_name}: {e}")
                winner = 1 - game.current_player
                result = {
                    'winner': winner,
                    'reason': 'error',
                    'moves': move_count,
                    'time': time.time() - start_time,
                    'player1': player1.team_name,
                    'player2': player2.team_name
                }
                print(f"🏆 {players[winner].team_name} wygrywa przez błąd przeciwnika!")
                return result

    def run_tournament(self, players: List, rounds: int = 1, 
                      game_configs: List[Dict] = None) -> Dict:
        """Organizuje turniej."""
        if game_configs is None:
            game_configs = [{'rows': 7, 'columns': 7, 'winning_length': 4}]
        
        print(f"\n🏆 TURNIEJ: {len(players)} graczy, {rounds} rund(y)")
        print("="*60)
        
        results = []
        standings = {player.team_name: {'wins': 0, 'draws': 0, 'losses': 0, 'points': 0} 
                    for player in players}
        
        for round_num in range(rounds):
            print(f"\n📅 RUNDA {round_num + 1}/{rounds}")
            print("-" * 40)
            
            # Wszystkie pary graczy
            for i in range(len(players)):
                for j in range(i + 1, len(players)):
                    for config in game_configs:
                        # Gra 1: i vs j
                        result1 = self.play_single_game(players[i], players[j], config)
                        results.append(result1)
                        self.update_standings(standings, result1)
                        
                        # Gra 2: j vs i (zmiana kolorów)
                        result2 = self.play_single_game(players[j], players[i], config)
                        results.append(result2)
                        self.update_standings(standings, result2)
        
        # Podsumowanie
        self.print_tournament_results(standings, results)
        
        return {
            'standings': standings,
            'games': results,
            'total_games': len(results)
        }

    def update_standings(self, standings: Dict, result: Dict):
        """Aktualizuje tabelę wyników."""
        player1_name = result['player1']
        player2_name = result['player2']
        
        if result['winner'] is None:  # Remis
            standings[player1_name]['draws'] += 1
            standings[player1_name]['points'] += 1
            standings[player2_name]['draws'] += 1
            standings[player2_name]['points'] += 1
        elif result['winner'] == 0:  # Wygrywa gracz 1
            standings[player1_name]['wins'] += 1
            standings[player1_name]['points'] += 3
            standings[player2_name]['losses'] += 1
        else:  # Wygrywa gracz 2
            standings[player2_name]['wins'] += 1
            standings[player2_name]['points'] += 3
            standings[player1_name]['losses'] += 1

    def print_tournament_results(self, standings: Dict, results: List[Dict]):
        """Wyświetla wyniki turnieju."""
        print("\n" + "="*80)
        print("🏆 WYNIKI TURNIEJU")
        print("="*80)
        
        # Sortuj według punktów
        sorted_standings = sorted(standings.items(), 
                                 key=lambda x: x[1]['points'], reverse=True)
        
        print(f"{'Pozycja':<8} {'Gracz':<25} {'Punkty':<8} {'Wygrane':<8} {'Remisy':<8} {'Przegrane':<10}")
        print("-" * 80)
        
        for idx, (name, stats) in enumerate(sorted_standings, 1):
            print(f"{idx:<8} {name:<25} {stats['points']:<8} "
                  f"{stats['wins']:<8} {stats['draws']:<8} {stats['losses']:<10}")
        
        print("\n" + "="*80)
        print(f"Łączna liczba gier: {len(results)}")
        
        # Statystyki dodatkowe
        avg_moves = sum(r['moves'] for r in results) / len(results)
        avg_time = sum(r['time'] for r in results) / len(results)
        
        print(f"Średnia liczba ruchów: {avg_moves:.1f}")
        print(f"Średni czas gry: {avg_time:.2f}s")
        print("="*80)

def main():
    """Główna funkcja programu."""
    print("🎮 CONNECT 4 Z GRAWITACJĄ")
    print("="*50)
    
    while True:
        print("\nWybierz opcję:")
        print("1. Gra: Człowiek vs Unbeatable AI")
        print("2. Gra: Człowiek vs Simple AI")
        print("3. Gra: Unbeatable AI vs Simple AI")
        print("4. Turniej AI")
        print("5. Konfiguracja planszy")
        print("6. Wyjście")
        
        choice = input("\nTwój wybór (1-6): ").strip()
        
        if choice == '1':
            human = HumanPlayer()
            ai = UnbeatableAI(max_depth=10)
            manager = GameManager()
            
            # Wybór kto zaczyna
            start_choice = input("Kto zaczyna? (h)uman lub (a)i: ").strip().lower()
            if start_choice.startswith('h'):
                manager.play_single_game(human, ai)
            else:
                manager.play_single_game(ai, human)
                
        elif choice == '2':
            human = HumanPlayer()
            ai = SimpleAI(depth=6)
            manager = GameManager()
            
            start_choice = input("Kto zaczyna? (h)uman lub (a)i: ").strip().lower()
            if start_choice.startswith('h'):
                manager.play_single_game(human, ai)
            else:
                manager.play_single_game(ai, human)
                
        elif choice == '3':
            ai1 = UnbeatableAI(max_depth=8)
            ai2 = SimpleAI(depth=6)
            manager = GameManager()
            
            print("Unbeatable AI vs Simple AI")
            manager.play_single_game(ai1, ai2)
            
        elif choice == '4':
            print("\n🏆 TURNIEJ AI")
            
            # Tworzenie graczy
            players = [
                UnbeatableAI(max_depth=8),
                UnbeatableAI(max_depth=6),
                SimpleAI(depth=8),
                SimpleAI(depth=6)
            ]
            
            # Różne konfiguracje planszy
            configs = [
                {'rows': 6, 'columns': 7, 'winning_length': 4},
                {'rows': 7, 'columns': 7, 'winning_length': 4},
                {'rows': 8, 'columns': 8, 'winning_length': 5}
            ]
            
            manager = GameManager()
            tournament_results = manager.run_tournament(players, rounds=1, game_configs=configs)
            
        elif choice == '5':
            print("\n⚙️ KONFIGURACJA PLANSZY")
            try:
                rows = int(input("Liczba wierszy (4-10): "))
                cols = int(input("Liczba kolumn (4-10): "))
                win_len = int(input("Długość do wygranej (3-6): "))
                
                if 4 <= rows <= 10 and 4 <= cols <= 10 and 3 <= win_len <= 6:
                    config = {'rows': rows, 'columns': cols, 'winning_length': win_len}
                    
                    human = HumanPlayer()
                    ai = UnbeatableAI(max_depth=8)
                    manager = GameManager()
                    
                    manager.play_single_game(human, ai, config)
                else:
                    print("❌ Nieprawidłowe wartości!")
                    
            except ValueError:
                print("❌ Wprowadź liczby!")
                
        elif choice == '6':
            print("👋 Dziękujemy za grę!")
            break
            
        else:
            print("❌ Nieprawidłowy wybór!")

if __name__ == "__main__":
    main()