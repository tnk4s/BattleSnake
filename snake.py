import random
import traceback
import numpy as np
import queue

from .mts_2 import MTS

# 自分用のSnakeを作るには、battlesnakeで定義されているSnakeを継承する必要がある
from battlesnake import Snake

# class名を変更。他のチームとかぶらないように
class MonteBotRe(Snake):
    def __init__(self, name):
        super().__init__(name)
        self.size = 0
        self.searcher = MTS(self.name, self.size)
        self.ene_names = []

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
            if not player["name"] == self.name:
                if player["name"] not in self.ene_names:
                    self.ene_names.append(player["name"])
            v = 2 if player["name"] == self.name else 3

            for x, y in player["body"]:
                board[x, y] = v

        return board

    def __get_my_data(self, data):
        for i in data["players"]:
            if i["name"] == self.name:
                return i

    def __get_ene_data(self, data):
        ene_datas = []
        for i in data["players"]:
            if i["name"] != self.name:
                ene_datas.append(i)
        
        return ene_datas
    
    def dangerous_food(self, data, fx, fy):
        my_data = self.__get_my_data(data)
        ene_datas = self.__get_ene_data(data)
        for e in ene_datas:
            ex, ey = e["body"][0]
            print("ex ey = ", ex, ey)
            print("food ", fx, fy)
            if fx + 1 == ex and fy == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    return True
            if fx - 1 == ex and fy == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    return True
            if fx == ex and fy + 1 == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    return True
            if fx == ex and fy - 1 == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    return True
        return False

    def __dangerous_direction(self, data, enenames, will_direction):
        my_data = self.__get_my_data(data)
        
        ene_datas = self.__get_ene_data(data)
        
        x,y = my_data["body"][0]
        if will_direction == 0:
            x = x + 1
        elif will_direction == 1:
            x = x - 1
        elif will_direction == 2:
            y = y + 1
        elif will_direction == 3:
            y = y - 1
        
        d_flag = False
        for e in ene_datas:
            if len(e["body"]) < 1:
                continue
            ex, ey = e["body"][0]
            if x + 1 == ex and y == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    d_flag = True
            if x - 1 == ex and y == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    d_flag = True
            if x == ex and y + 1 == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    d_flag = True
            if x == ex and y - 1 == ey:
                if len(e["body"]) >= len(my_data["body"]):
                    d_flag = True
            
            if d_flag:
                print("==WARNIGN High Lv Enemies==")
                return True
        return False

    def __check_dead_end(self, player_data, v_board, direction):#幅優先ぽい
        hx, hy = player_data["body"][0]
        if direction == 0:
            x = hx + 1
            y = hy
        elif direction == 1:
            x = hx - 1
            y = hy
        elif direction == 2:
            x = hx
            y = hy + 1
        elif direction == 3:
            x = hx
            y = hy - 1

        if x >= self.size or x < 0:
            return False
        elif y >= self.size or y < 0:
            return False

        N = 4 #4無かったらFalse
        dist = {}
        already = [(hx,hy)]

        que = queue.Queue()
        
        #s_key = "(" + str(x) + "," + str(y) + ")" #(x,y)
        s_key = (x,y)
        dist[s_key] = 0
        que.put((x,y))

        while not que.empty():
            #print("before que.qsize() ", que.qsize())
            v = que.get() # キューから先頭頂点を取り出す
            #print("after que.qsize() ", que.qsize())
            if s_key == None:
                x,y = v
                #s_key = "(" + str(x) + "," + str(y) + ")" #(x,y)
                s_key = (x,y)
            
            for d in range(4):
                if d == 0:
                    if x+1 >= self.size or (x+1,y) in dist.keys():#既に発見済みなら探索しない
                        continue
                    if  v_board[x+1, y] < 2:
                        #new_key = "(" + str(x+1) + "," + str(y) + ")" #(x,y)
                        new_key = (x+1, y)
                        dist[new_key] = dist[s_key] + 1
                        #already.append((x+1, y))
                        que.put((x+1, y))
                elif d == 1:
                    if x-1 < 0 or (x-1,y) in dist.keys():
                        continue
                    if v_board[x-1, y] < 2:
                        #new_key = "(" + str(x-1) + "," + str(y) + ")" #(x,y)
                        new_key = (x-1, y)
                        dist[new_key] = dist[s_key] + 1
                        #already.append((x-1, y))
                        que.put((x-1, y))
                elif d == 2:
                    if y+1 >= self.size or (x,y+1) in dist.keys():
                        continue
                    if v_board[x, y+1] < 2:
                        #new_key = "(" + str(x) + "," + str(y+1) + ")" #(x,y)
                        new_key = (x, y+1)
                        dist[new_key] = dist[s_key] + 1
                        #already.append((x, y+1))
                        que.put((x, y+1))
                elif d == 3:
                    if y-1 < 0 or (x,y-1) in dist.keys():
                        continue
                    if v_board[x, y-1] < 2:
                        #new_key = "(" + str(x) + "," + str(y-1) + ")" #(x,y)
                        new_key = (x, y-1)
                        dist[new_key] = dist[s_key] + 1
                        #already.append((x, y-1))
                        que.put((x, y-1))
                if dist[s_key] >= N :
                    print("N = ", dist[s_key])
                    return True
            s_key = None
        
        buf = -1
        for v in dist.values():
            if buf < v:
                buf = v
        
        print("N = ", buf)
        if buf < N:
            print("==WARNING DEAD END==")
            return False
        return True

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
            if self.dangerous_food(data, x + 1, y):
                print("==================WARNING!============")
            else:
                print("defined RIGHT")
                return "RIGHT"

        if x - 1 > -1 and board[x - 1, y] == 0:
            d.append("LEFT")
        if x - 1 > -1 and board[x - 1, y] == 1:
            if self.dangerous_food(data, x - 1, y):
                print("==================WARNING!============")
            else:
                print("defined LEFT")
                return "LEFT"

        if y + 1 < self.size and board[x, y + 1] == 0:
            d.append("UP")
        if y + 1 < self.size and board[x, y + 1] == 1:
            if self.dangerous_food(data, x, y+1):
                print("==================WARNING!============")
            else:
                print("defined UP")
                return "UP"

        if y - 1 > -1 and board[x, y - 1] == 0:
            d.append("DOWN")
        if y - 1 > -1 and board[x, y - 1] == 1:
            if self.dangerous_food(data, x, y-1):
                print("==================WARNING!============")
            else:
                print("defined DOWN")
                return "DOWN"

        if len(d) == 0:
            print("Dead end. Good bye.")
            return "UP"
        else:
            rand_d = random.choice(d)
            #return rand_d
            
            #'''
            try:
                direction = self.searcher.monte_direction_indicator(self.size, player, self.ene_names, data, board)
                if direction in d:
                    print("MCTS choice", direction)
                    #traceback.print_exc()
                    return direction
                    #return rand_d
                else:
                    print("Command MASSA")
                    #===================================from v1.0.3
                    fx=fy=6
                    mindis=20
                    for i,j in data["food"]:
                        distance=abs(i-x)+abs(j-y)
                        if mindis>distance:
                            mindis=distance
                            fx=i
                            fy=j
                    if fx-x>0 and (board[x + 1, y] <2 ) and "RIGHT" in d and self.__check_dead_end(player, board, 0) and not self.__dangerous_direction(data, self.ene_names, 0):
                        print("MASSA RIGHT")
                        return "RIGHT"
                    elif fx-x<0 and (board[x - 1, y] <2 ) and "LEFT" in d and self.__check_dead_end(player, board, 1) and not self.__dangerous_direction(data, self.ene_names, 1):
                        print("MASSA LEFT")
                        return "LEFT"
                    elif fy-y>0 and (board[x , y + 1] <2 ) and "UP" in d and self.__check_dead_end(player, board, 2) and not self.__dangerous_direction(data, self.ene_names, 2):
                        print("MASSA UP")
                        return "UP"
                    elif fy-y<0 and (board[x , y - 1] <2 ) and "DOWN" in d and self.__check_dead_end(player, board, 3) and not self.__dangerous_direction(data, self.ene_names, 3):
                        print("MASSA DOWN")
                        return "DOWN"
                    elif len(d) == 0:
                        print("Dead end. Good bye.")
                        return "UP"
                    #===================================
                    else:
                        return rand_d
            except:
                #traceback.print_exc()
                print("Command MASSA in Exception")
                #===================================from v1.0.3
                fx=fy=6
                mindis=20
                for i,j in data["food"]:
                    distance=abs(i-x)+abs(j-y)
                    if mindis>distance:
                        mindis=distance
                        fx=i
                        fy=j
                if fx-x>0 and (board[x + 1, y] <2 ) and "RIGHT" in d :
                    print("MASSA RIGHT")
                    return "RIGHT"
                elif fx-x<0 and (board[x - 1, y] <2 ) and "LEFT" in d :
                    print("MASSA LEFT")
                    return "LEFT"
                elif fy-y>0 and (board[x , y + 1] <2 ) and "UP" in d :
                    print("MASSA UP")
                    return "UP"
                elif fy-y<0 and (board[x , y - 1] <2 ) and "DOWN" in d :
                    print("MASSA DOWN")
                    return "DOWN"
                elif len(d) == 0:
                    print("Dead end. Good bye.")
                    return "UP"
                #===================================
                else:
                    return rand_d
            #'''

            