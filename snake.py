import random

import numpy as np

# 自分用のSnakeを作るには、battlesnakeで定義されているSnakeを継承する必要がある
from battlesnake import Snake

# class名を変更。他のチームとかぶらないように


class Bot(Snake):
    def __init__(self, name):
        super().__init__(name)
        self.size = 0

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

    def __avoid_collision(self, x, y, player, enemies):
        enemies_head = [enemy["body"][0] for enemy in enemies]
        player_len = len(player["body"])
        enemies_len = [len(enemy["body"]) for enemy in enemies]

        for i, enemy_head in enumerate(enemies_head):
            enemy_x, enemy_y = enemy_head
            if abs(x - enemy_x) + abs(y - enemy_y) == 1 and player_len <= enemies_len[i]:
                return False

        return True

    # 近くにfoodがある場合は取りに行く。
    # 基本は移動できるところをランダムで
    def move(self, data):
        board = self.__get_board(data)
        player = [p for p in data["players"] if p["name"] == self.name][0]
        head = player["body"][0]

        enemies = [p for p in data["players"] if p["name"] != self.name]

        x, y = head
        d = []
        d2 = []
        
        min_dist = 100
        min_fx = -1
        min_fy = -1
        for fx, fy in data["food"]:
            dist = abs(fx - x) + abs(fy - y)
            if min_dist > dist:
                min_dist = dist
                min_fx = fx
                min_fy = fy

        if x + 1 < self.size and board[x + 1, y] < 2 and not(x+1==data["size"]-1 and (y==0 or y==data["size"]-1)):
            if self.__avoid_collision(x + 1, y, player, enemies):
                if min_fx - x > 0:
                    return "RIGHT"
                d.append("RIGHT")
            d2.append("RIGHT")
        if x - 1 > -1 and board[x - 1, y] < 2 and not(x-1==0 and (y==0 or y==data["size"]-1)):
            if self.__avoid_collision(x - 1, y, player, enemies):
                if min_fx - x < 0:
                    return "LEFT"
                d.append("LEFT")
            d2.append("LEFT")
        if y + 1 < self.size and board[x, y + 1] < 2 and not(y+1==data["size"]-1 and (x==0 or x==data["size"]-1)):
            if self.__avoid_collision(x, y + 1, player, enemies):
                if min_fy - y > 0:
                    return "UP"
                d.append("UP")
            d2.append("UP")
        if y - 1 > -1 and board[x, y - 1] < 2 and not(y-1==0 and (x==0 or x==data["size"]-1)):
            if self.__avoid_collision(x, y - 1, player, enemies):
                if min_fy - y < 0:
                    return "DOWN"
                d.append("DOWN")
            d2.append("DOWN")

        if len(d2) == 0:
            return "UP"
        elif len(d) == 0:
            d = d2

        return random.choice(d)
