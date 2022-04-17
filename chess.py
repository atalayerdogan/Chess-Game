#!/usr/bin/env python3

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChessBoard(QMainWindow):
    BOARD_COLORS = ["#f5ede4", "#d6a360"]
    HIGHLIGHT_COLOR = "#f582ac"

    def __init__(self):
        super().__init__()
        self.W, self.H = 640, 640
        self.resize(self.W, self.H)
        self.setup_game()

    def paintEvent(self, event):
        self.painter = QPainter(self)
        pen = QPen()
        pen.setColor(QColor("transparent"))
        self.painter.setPen(pen)

        self.painter.setBrush(QBrush(QColor("#42f584"),Qt.SolidPattern))
        for y in range(8): # y
            for x in range(8): # x
                self.painter.setBrush(QBrush(QColor(self.BOARD_COLORS[int((x+y)%2)]),Qt.SolidPattern))

                if self.highlights:
                    for coord in self.highlights:
                        if x == coord[0] and y == 7-coord[1]:
                            self.painter.setBrush(QBrush(QColor(self.HIGHLIGHT_COLOR),Qt.SolidPattern))

                r = self.W//8
                self.painter.drawRect(x*r, y*r, r, r)

        self.painter.end()
    
    def setup_game(self):
        rook_capabilities = [*[[i,0] for i in range(8)],*[[0,i] for i in range(8)],*[[-i,0] for i in range(8)],*[[0,-i] for i in range(8)]] # lol
        bishop_capabilities = [*[[i, i] for i in range(8)],*[[-i, -i] for i in range(8)],*[[i, -i] for i in range(8)],*[[-i, i] for i in range(8)]]
        """
        self.pieces = {
            "B": Bishop("pieces/wB.svg", pos=[2 ,0], move_capabilities = bishop_capabilities, team = "white"),
            "K": King("pieces/wK.svg", pos=[4 ,0], move_capabilities = [[0, 1],[0, -1],[1, 0],[-1, 0],[1, 1],[-1, -1],[-1, 1],[1, -1]], team = "white"),
            "N": Knight("pieces/wN.svg", pos=[1 ,0], move_capabilities = [[1, 2], [2, 1], [-1, 2], [2, -1], [-1, -2], [-2, 1], [1, -2], [-2, -1]], team = "white"),
            "P": Pawn("pieces/wP.svg", pos=[0 ,1], move_capabilities =[[0, 1], [0, 2]], team = "white"),
            "Q": Queen("pieces/wQ.svg", pos=[5 ,0], move_capabilities =rook_capabilities+bishop_capabilities, team = "white"),
            "R": Rook("pieces/wR.svg", pos=[0 ,0], move_capabilities =rook_capabilities, team="white"),

            "b": Bishop("pieces/bB.svg", pos=[2 ,7], move_capabilities = bishop_capabilities, team = "black"),
            "k": King("pieces/bK.svg", pos=[4 ,7], move_capabilities = [[0, 1],[0, -1],[1, 0],[-1, 0],[1, 1],[-1, -1],[-1, 1],[1, -1]], team = "black"),
            "n": Knight("pieces/bN.svg", pos=[1 ,7], move_capabilities = [[1, 2], [2, 1], [-1, 2], [2, -1], [-1, -2], [-2, 1], [1, -2], [-2, -1]], team = "black"),
            "p": Pawn("pieces/bP.svg", pos=[0 ,6], move_capabilities =[[0, -1], [0, -2]], team = "black"),
            "q": Queen("pieces/bQ.svg", pos=[5 ,7], move_capabilities =rook_capabilities+bishop_capabilities, team = "black"),
            "r": Rook("pieces/bR.svg", pos=[0 ,7], move_capabilities =rook_capabilities, team="black")
        }
        """
        self.pieces = {
            "R": Rook("pieces/wR.svg", pos=[0 ,0], move_capabilities =rook_capabilities, team="white"),

            "r": Rook("pieces/bR.svg", pos=[0 ,7], move_capabilities =rook_capabilities, team="black")
        }
        self.highlights = []
        self.current_clicked_piece = None
        
        for piece in self.pieces.values():
            piece.setParent(self)

    def update_piece_pos(self, piece): # moves the piece to its position (set the position before moving)
        piece.move((self.W//8)*piece.x, (self.W//8)*(7-piece.y))

    # events
    #
    def resizeEvent(self, e):
        w = self.width()
        self.resize(w, w)
        self.W, self.H = w, w
        self.update()

        for piece in self.pieces.values():
            piece.adjust_size_with_resize()
            self.update_piece_pos(piece)

    def mouseReleaseEvent(self, e):
        x, y = e.x()//(self.W/8), 7 - e.y()//(self.W/8)
        if self.current_clicked_piece:
            if [int(x), int(y)] in self.highlights: # checking if clicked square in highlights
                self.current_clicked_piece.x, self.current_clicked_piece.y = int(x) , int(y)
                self.update_piece_pos(self.current_clicked_piece)
                self.current_clicked_piece.piece_moved()
                self.highlights = []
                self.update()
            else:
                self.highlights = []
                self.update()

class Piece(QPushButton):
    def __init__(self, img="", pos=[], move_capabilities=[], team=""):
        super().__init__()
        self.x, self.y = pos
        self.team = team
        self.move_capabilities = move_capabilities
        self.clicked.connect(self.on_click_event)
        self.setStyleSheet("background: transparent;")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setIcon(QIcon(img))
        self.is_clicked = False 
        self.move_count = 0

    def adjust_size_with_resize(self):
        size = self.parent().width() // 8
        self.setIconSize(QSize(size, size))
        self.setFixedSize(size, size)

    def on_click_event(self):
        if [p for p in self.parent().pieces.values() if p.is_clicked]: # some other piece was already clicked on
            self.parent().highlights = []
            for piece in self.parent().pieces.values():
                piece.is_clicked = False

        self.is_clicked = not self.is_clicked
        if self.is_clicked: # piece clicked
            self.parent().current_clicked_piece = self
            for move in self.move_capabilities:
                self.parent().highlights.append([move[0]+self.x, move[1]+self.y])
            
            #print(self.parent().highlights)

        self.parent().update()

class Pawn(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def piece_moved(self):
        self.move_count += 1
        if self.move_count == 1 and self.team == "white":
            if [0, 2] in self.move_capabilities:
                self.move_capabilities.remove([0, 2])
        elif self.move_count == 1 and self.team == "black":
            if [0, -2] in self.move_capabilities:
                self.move_capabilities.remove([0, -2])

        if self.y == 7:
            print("promote")

class Rook(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def piece_moved(self):
        self.move_count += 1

class Bishop(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def piece_moved(self):
        self.move_count += 1

class Queen(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def piece_moved(self):
        self.move_count += 1

class King(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def piece_moved(self):
        self.move_count += 1

class Knight(Piece):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def piece_moved(self):
        self.move_count += 1

def main():
    app = QApplication([])
    window = ChessBoard()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
