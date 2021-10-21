import random
import traceback
import numpy as np

from .mcts import MCTS

# 自分用のSnakeを作るには、battlesnakeで定義されているSnakeを継承する必要がある
from battlesnake import Snake

# class名を変更。他のチームとかぶらないように
class MonteBot(Snake):
    def __init__(self, name):
        super().__init__(name)
        self.size = 0
        self.searcher = MCTS(self.name, self.size)

    # 終了時(ゲームオーバー or 勝利)に呼ばれる
    def end(self, data):
        # print(f"{self.name} end")
        pass

    def __get_board(self, data):
        self.size = data["size"]
        board = np.zeros((self.size, self.size), dtype=int)

        for x, y in data["food"]:
            board[x, y] = 1

        for player in data["players"]:
            v = 2 if player["name"] == self.name else 3

            for x, y in player["body"]:
                board[x, y] = v

        return board

    # 近くにfoodがある場合は取りに行く。
    # 基本は移動できるところをランダムで
    def move(self, data):
        board = self.__get_board(data)
        player = [p for p in data["players"] if p["name"] == self.name][0]
        head = player["body"][0]
        
        x, y = head
        d = []

        if x + 1 < self.size and board[x + 1, y] == 0:
            d.append("RIGHT")
        if x + 1 < self.size and board[x + 1, y] == 1:#食べ物
            print("defined RIGHT")
            return "RIGHT"

        if x - 1 > -1 and board[x - 1, y] == 0:
            d.append("LEFT")
        if x - 1 > -1 and board[x - 1, y] == 1:
            print("defined LEFT")
            return "LEFT"

        if y + 1 < self.size and board[x, y + 1] == 0:
            d.append("UP")
        if y + 1 < self.size and board[x, y + 1] == 1:
            print("defined UP")
            return "UP"

        if y - 1 > -1 and board[x, y - 1] == 0:
            d.append("DOWN")
        if y - 1 > -1 and board[x, y - 1] == 1:
            print("defined DOWN")
            return "DOWN"

        if len(d) == 0:
            return "UP"
        else:
            rand_d = random.choice(d)
            #return rand_d
            
            #'''
            try:
                direction = self.searcher.monte_direction_indicator(player, data, board)
                if direction in d:
                    print(direction)
                    #traceback.print_exc()
                    return direction
                    #return rand_d
                else:
                    print("Command RAND")
                    #===================================from v1.0.3
                    fx=fy=6
                    mindis=20
                    for i,j in data["food"]:
                        distance=abs(i-x)+abs(j-y)
                        if mindis>distance:
                            mindis=distance
                            fx=i
                            fy=j
                    if fx-x>0 and (board[x + 1, y] <2 ) and "RIGHT" in d:
                        return "RIGHT"
                    elif fx-x<0 and (board[x - 1, y] <2 ) and "LEFT" in d:
                        return "LEFT"
                    elif fy-y>0 and (board[x , y + 1] <2 ) and "UP" in d:
                        return "UP"
                    elif fy-y<0 and (board[x , y - 1] <2 ) and "DOWN" in d:
                        return "DOWN"
                    elif len(d) == 0:
                        return "UP"
                    #===================================
                    else:
                        return rand_d
            except:
                traceback.print_exc()
                print("rand_d = ",rand_d)
                return rand_d
            #'''

            