import math
import sys
from typing import Optional

import chess
import pygame


# ----------------------------
# Configuration
# ----------------------------

LARGEUR = 720
LONGUEUR = 760
TAILLE_TABLEAU = 720
TAILLE_SQ = TAILLE_TABLEAU // 8
FPS = 60

CARRE_BLANC = (240, 217, 181)
CARRE_NOIR = (181, 136, 99)
SOULIGNER = (246, 246, 105)
MOOVE_CONSEILLE = (106, 166, 74)
TEXT_COULEUR = (25, 25, 25)
FOND_COULEUR = (235, 235, 235)
CHECK_COULEUR = (220, 80, 80)

NIVEAU_BOT = 3 # 2 = plus rapide, 3 = plus fort


# Unicode des pièces
PIECES = {
    "P": "♙",
    "N": "♘",
    "B": "♗",
    "R": "♖",
    "Q": "♕",
    "K": "♔",
    "p": "♟",
    "n": "♞",
    "b": "♝",
    "r": "♜",
    "q": "♛",
    "k": "♚",}


# Valeurs matérielles
VALEUR_PIECES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,}


# Tables positionnelles simples
PAWN_TABLE = [
    0, 0, 0, 0, 0, 0, 0, 0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5, 5, 10, 25, 25, 10, 5, 5,
    0, 0, 0, 20, 20, 0, 0, 0,
    5, -5, -10, 0, 0, -10, -5, 5,
    5, 10, 10, -20, -20, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0,]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20, 0, 5, 5, 0, -20, -40,
    -30, 5, 10, 15, 15, 10, 5, -30,
    -30, 0, 15, 20, 20, 15, 0, -30,
    -30, 5, 15, 20, 20, 15, 5, -30,
    -30, 0, 10, 15, 15, 10, 0, -30,
    -40, -20, 0, 0, 0, 0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10, 5, 0, 0, 0, 0, 5, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10, 0, 10, 10, 10, 10, 0, -10,
    -10, 5, 5, 10, 10, 5, 5, -10,
    -10, 0, 5, 10, 10, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,]

ROOK_TABLE = [
    0, 0, 5, 10, 10, 5, 0, 0,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    -5, 0, 0, 0, 0, 0, 0, -5,
    5, 10, 10, 10, 10, 10, 10, 5,
    0, 0, 0, 0, 0, 0, 0, 0,]

QUEEN_TABLE = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10, 0, 5, 0, 0, 0, 0, -10,
    -10, 5, 5, 5, 5, 5, 0, -10,
    0, 0, 5, 5, 5, 5, 0, -5,
    -5, 0, 5, 5, 5, 5, 0, -5,
    -10, 0, 5, 5, 5, 5, 0, -10,
    -10, 0, 0, 0, 0, 0, 0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20,]

KING_TABLE_MID = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20, 0, 0, 0, 0, 20, 20,
    20, 30, 10, 0, 0, 10, 30, 20,]


def index_miroir(index: int) -> int:
# Miroir vertical pour les pièces noires.
    rang = index // 8
    file_ = index % 8
    return (7 - rang) * 8 + file_


def piece_carre_valeur(piece: chess.Piece, carre: chess.Square) -> int:
    idx = carre
    if piece.color == chess.BLACK:
        idx = index_miroir(carre)

    if piece.piece_type == chess.PAWN:
        return PAWN_TABLE[idx]
    if piece.piece_type == chess.KNIGHT:
        return KNIGHT_TABLE[idx]
    if piece.piece_type == chess.BISHOP:
        return BISHOP_TABLE[idx]
    if piece.piece_type == chess.ROOK:
        return ROOK_TABLE[idx]
    if piece.piece_type == chess.QUEEN:
        return QUEEN_TABLE[idx]
    if piece.piece_type == chess.KING:
        return KING_TABLE_MID[idx]
    return 0


def evaluation_tableau(tab: chess.Board) -> int:
# Évaluation depuis le point de vue des noirs. Score positif = avantage noir.

    if tab.is_checkmate():
        if tab.turn == chess.WHITE:
        # Blanc doit jouer mais est mat -> noir a gagné
            return 100000
        else:
        # Noir doit jouer mais est mat -> blanc a gagné
            return -100000

    if (tab.is_stalemate() or tab.is_insufficient_material() or tab.can_claim_threefold_repetition() or tab.can_claim_fifty_moves()):
        return 0

    score = 0

    for carre, piece in tab.piece_map().items():
        carre = VALEUR_PIECES[piece.piece_type] + piece_carre_valeur(piece, carre)
        if piece.color == chess.BLACK:
            score += carre
        else:
            score -= carre

    # Petite prime à la mobilité
    mobilite = len(list(tab.legal_moves))
    if tab.turn == chess.BLACK:
        score += mobilite * 2
    else:
        score -= mobilite * 2

    return score


def ordre_mouvement(tab: chess.Board) -> list[chess.Move]:
    # Trie simple : captures et promotions d'abord.
    def moove_score(move: chess.Move) -> int:
        score = 0
        if tab.is_capture(move):
            victime = tab.piece_at(move.to_square)
            attaquant = tab.piece_at(move.from_square)
            if victime and attaquant:
                score += 10 * VALEUR_PIECES[victime.piece_type] - VALEUR_PIECES[attaquant.piece_type]
            else:
                score += 100
        if move.promotion:
            score += 800
        if tab.gives_check(move):
            score += 50
        return score

    moves = list(tab.legal_moves)
    moves.sort(key=moove_score, reverse=True)
    return moves


def minimax(board: chess.Board, depth: int, alpha: int, beta: int, maximizing: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluation_tableau(board)

    moves = ordre_mouvement(board)

    if maximizing:
        max_eval = -math.inf
        for move in moves:
            board.push(move)
            eval_ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_)
            alpha = max(alpha, eval_)
            if beta <= alpha:
                break
        return int(max_eval)
    else:
        min_eval = math.inf
        for move in moves:
            board.push(move)
            eval_ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_)
            beta = min(beta, eval_)
            if beta <= alpha:
                break
        return int(min_eval)

def otenir_meilleur_coup(board: chess.Board, depth: int) -> Optional[chess.Move]:
# Le bot joue les noirs.
    if board.is_game_over():
        return None

    best_move = None
    best_eval = -math.inf

    for move in ordre_mouvement(board):
        board.push(move)
        eval_ = minimax(board, depth - 1, -math.inf, math.inf, False)
        board.pop()

        if eval_ > best_eval:
            best_eval = eval_
            best_move = move

    return best_move


def square_to_screen(square: chess.Square) -> tuple[int, int]:
    file_ = chess.square_file(square)
    rank = chess.square_rank(square)
    x = file_ * TAILLE_SQ
    y = (7 - rank) * TAILLE_SQ
    return x, y


def screen_to_square(pos: tuple[int, int]) -> Optional[chess.Square]:
    x, y = pos
    if x < 0 or x >= TAILLE_TABLEAU or y < 0 or y >= TAILLE_TABLEAU:
        return None
    file_ = x // TAILLE_SQ
    rank = 7 - (y // TAILLE_SQ)
    return chess.square(file_, rank)


def interface(
    affichage: pygame.Surface,
    tableau: chess.Board,
    piece_font: pygame.font.Font,
    ui_font: pygame.font.Font,
    selection_carre: Optional[chess.Square],
    coup_legal: list[chess.Square],
    status_text: str,
) -> None:
    affichage.fill(FOND_COULEUR)

    # Cases
    for rank in range(8):
        for file_ in range(8):
            x = file_ * TAILLE_SQ
            y = rank * TAILLE_SQ
            color = CARRE_BLANC if (rank + file_) % 2 == 0 else CARRE_NOIR
            pygame.draw.rect(affichage, color, (x, y, TAILLE_SQ, TAILLE_SQ))

    # Surligner roi en échec
    if tableau.is_check():
        king_square = tableau.king(tableau.turn)
        if king_square is not None:
            x, y = square_to_screen(king_square)
            pygame.draw.rect(affichage, CHECK_COULEUR, (x, y, TAILLE_SQ, TAILLE_SQ))

    # Case sélectionnée
    if selection_carre is not None:
        x, y = square_to_screen(selection_carre)
        pygame.draw.rect(affichage, SOULIGNER, (x, y, TAILLE_SQ, TAILLE_SQ))

        # Cibles légales
    for sq in coup_legal:
        x, y = square_to_screen(sq)
        center = (x + TAILLE_SQ // 2, y + TAILLE_SQ // 2)
        pygame.draw.circle(affichage, MOOVE_CONSEILLE, center, 12)

    # Pièces
    for square, piece in tableau.piece_map().items():
        x, y = square_to_screen(square)
        symbol = PIECES[piece.symbol()]
        texte = piece_font.render(symbol, True, TEXT_COULEUR)
        text_rect = texte.get_rect(center=(x + TAILLE_SQ // 2, y + TAILLE_SQ // 2 + 4))
        affichage.blit(texte, text_rect)

    # Coordonnées
    coordonnee_police = pygame.font.SysFont("Arial", 18)
    for file_ in range(8):
        lettre = chr(ord("a") + file_)
        texte = coordonnee_police.render(lettre, True, (60, 60, 60))
        affichage.blit(texte, (file_ * TAILLE_SQ + 4, TAILLE_TABLEAU - 22))
    for rank in range(8):
        nombre = str(8 - rank)
        texte = coordonnee_police.render(nombre, True, (60, 60, 60))
        affichage.blit(texte, (4, rank * TAILLE_SQ + 4))

    # Bandeau UI
    pygame.draw.rect(affichage, (245, 245, 245), (0, TAILLE_TABLEAU, LARGEUR, LONGUEUR - TAILLE_TABLEAU))
    info = ui_font.render(status_text, True, (30, 30, 30))
    affichage.blit(info, (16, TAILLE_TABLEAU + 16))

    aide_texte = "R: restart | Z: undo last full move | Bot: noirs"
    aide_surface = ui_font.render(aide_texte, True, (80, 80, 80))
    affichage.blit(aide_surface, (16, TAILLE_TABLEAU + 48))

    pygame.display.flip()


def obtenir_coup_legal(board: chess.Board, from_square: chess.Square) -> list[chess.Square]:
    return [move.to_square for move in board.legal_moves if move.from_square == from_square]


def trouver(board: chess.Board, from_square: chess.Square, to_square: chess.Square, promotion_piece: int = chess.QUEEN,) -> Optional[chess.Move]:
    # Trouve un coup légal correspondant au déplacement. Gère la promotion en dame par défaut.
    candidate = chess.Move(from_square, to_square)
    if candidate in board.legal_moves:
        return candidate

    # Promotion
    promo_candidate = chess.Move(from_square, to_square, promotion=promotion_piece)
    if promo_candidate in board.legal_moves:
        return promo_candidate

    return None


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Python Chess AI - Joue contre l'assistant de AmZzPYJS")
    affichage = pygame.display.set_mode((LARGEUR, LONGUEUR))
    temps = pygame.time.Clock()

    piece_police = pygame.font.SysFont("DejaVu Sans", 64)
    ui_police = pygame.font.SysFont("Arial", 24)

    tab = chess.Board()
    case_selectionne: Optional[chess.Square] = None
    coup_legal: list[chess.Square] = []

    jouer = True
    bot_reflechi = False
    texte_statut = "À toi de jouer !"

    while jouer:
        temps.tick(FPS)

        # Tour du bot
        if tab.turn == chess.BLACK and not tab.is_game_over() and not bot_reflechi:
            bot_reflechi = True
            texte_statut = "L'assistant de AmZzPYJS réfléchit..."
            interface(affichage, tab, piece_police, ui_police, case_selectionne, coup_legal, texte_statut)

            meilleur_coup = otenir_meilleur_coup(tab, NIVEAU_BOT)
            if meilleur_coup is not None:
                tab.push(meilleur_coup)

            bot_reflechi = False

            if tab.is_checkmate():
                texte_statut = "Échec et mat. L'assistant de AmZzPYJS a gagné."
            elif tab.is_stalemate():
                texte_statut = "Pat."
            elif tab.is_check():
                texte_statut = "Échec contre les blancs."
            else:
                texte_statut = "À toi de jouer !"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                jouer = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    tab = chess.Board()
                    case_selectionne = None
                    coup_legal = []
                    texte_statut = "Nouvelle partie. À toi de jouer !"

                elif event.key == pygame.K_z:
                    # Annule le dernier coup blanc + noir si possible
                    if len(tab.move_stack) >= 2:
                        tab.pop()
                        tab.pop()
                        case_selectionne = None
                        coup_legal = []
                        texte_statut = "Dernier tour annulé."
                    elif len(tab.move_stack) == 1:
                        tab.pop()
                        case_selectionne = None
                        coup_legal = []
                        texte_statut = "Dernier coup annulé."

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if tab.turn != chess.WHITE or tab.is_game_over():
                    continue

                square = screen_to_square(event.pos)
                if square is None:
                    continue

                piece = tab.piece_at(square)

                # Aucune pièce sélectionnée : on en choisit une blanche
                if case_selectionne is None:
                    if piece is not None and piece.color == chess.WHITE:
                        case_selectionne = square
                        coup_legal = obtenir_coup_legal(tab, square)

                else:
                    # Clique sur une autre pièce blanche : on change la sélection
                    if piece is not None and piece.color == chess.WHITE:
                        case_selectionne = square
                        coup_legal = obtenir_coup_legal(tab, square)
                    else:
                        move = trouver(tab, case_selectionne, square)
                        if move is not None:
                            tab.push(move)
                            case_selectionne = None
                            coup_legal = []

                            if tab.is_checkmate():
                                texte_statut = "Échec et mat. Tu as gagné."
                            elif tab.is_stalemate():
                                texte_statut = "Pat."
                            elif tab.is_check():
                                texte_statut = "Échec contre les noirs."
                            else:
                                texte_statut = "Coup joué. Le bot va répondre."
                        else:
                            # Désélection si coup illégal
                            case_selectionne = None
                            coup_legal = []

        # Fin de partie
        if tab.is_game_over():
            outcome = tab.outcome()
            if outcome is not None:
                if outcome.winner is True:
                    texte_statut = "Partie terminée : les blancs gagnent."
                elif outcome.winner is False:
                    texte_statut = "Partie terminée : les noirs gagnent."
                else:
                    texte_statut = "Partie terminée : nulle."

        interface(affichage, tab, piece_police, ui_police, case_selectionne, coup_legal, texte_statut)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
