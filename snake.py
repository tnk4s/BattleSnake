import random

import numpy as np

#自分用のSnakeを作るには、battlesnakeで定義されているSnakeを継承する必要がある
from battlesnake import Snake

# class名を変更。他のチームとかぶらないように

class Bot(Snake):

    def __init__(self, name):
        super().__init__(name)
        self.size = 0
        self.food_closest = False
        self.strategy = "food"
        self.s_count = 0
        self.eruzio_d = ""

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
        enemies = [p for p in data["players"] if p["name"] != self.name]

        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        #自分の体の最後の座標を一時的に0にすることで移動可能マスとして扱う
        if player["health"] != 100 : 
            board[zx,zy] = 0

        if len(enemies) == 1:
            d = self.__1vs1(data,board,player,enemies)
        else:
            d = self.__BattleRoyal(data,board,player,enemies)

        board[zx,zy] = board[ax,ay] 
        print(d)
        return d

    def __BattleRoyal(self,data,board,player,enemies):
        #ene_num = len(enemies)
        d = []
        print("food",data["food"])
        #自分の体の最初と最後の座標を取得
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]
        
        #自分の頭から一番近い餌の座標を取得
        food_mindis,ene_food_mindis,priority_food = self.__get_food_mindis(data,board,player,enemies)
        
        if priority_food != 100:
            fx,fy = data["food"][priority_food]
            fmin = food_mindis[priority_food]
            able_d = self.__move_check(board,player,enemies)
            print("取りに行くべき餌は(",fx,fy,")で最短距離は",fmin,"です")
            best_d,flag = self.__best_route(board,player,fx,fy,0,0)
            if best_d in able_d:
                print(best_d,"に進みます")
                return best_d

            able_d = self.__move_check(board,player,enemies)
            escape_d = self.__escape(board,player,enemies)
            if escape_d in able_d:
                return escape_d
            elif len(able_d) != 0:
                return random.choice(able_d)
            else:
                if ax + 1 < self.size and board[ax + 1, ay] == 0:
                    return "RIGHT" 
                if ax - 1 > -1 and board[ax - 1, ay] == 0:
                    return "LEFT" 
                if ay + 1 < self.size and board[ax, ay + 1] == 0:
                    return "UP" 
                if ay - 1 > -1 and board[ax, ay - 1] == 0:
                    return "DOWN" 
        else:
            print("一番近い餌はありません")
            return self.__escape(board,player,enemies)


    def __1vs1(self,data,board,player,enemies):
        #自分の体の最初と最後の座標を取得
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        #自分の頭から一番近い餌の座標を取得
        food_mindis,ene_food_mindis,priority_food = self.__get_food_mindis(data,board,player,enemies)
        
        if priority_food != 100:
            fx,fy = data["food"][priority_food]
            fmin = food_mindis[priority_food]
            able_d = self.__move_check(board,player,enemies)
            print("取りに行くべき餌は(",fx,fy,")で最短距離は",fmin,"です")
            best_d,flag = self.__best_route(board,player,fx,fy,0,0)
            self.__strategy_decision(board,player,enemies,fx,fy)
            if flag != "ERROR" and self.strategy != "food":
                strategy_d =  self.__strategy(board,player,enemies,fx,fy)
                if strategy_d in able_d:
                    print(strategy_d,"に進みます")
                    return strategy_d
            elif best_d in able_d:
                print(best_d,"に進みます")
                return best_d

            able_d = self.__move_check(board,player,enemies)
            escape_d = self.__escape(board,player,enemies)
            if escape_d in able_d:
                return escape_d
            elif len(able_d) != 0:
                return random.choice(able_d)
            else:
                if ax + 1 < self.size and board[ax + 1, ay] == 0:
                    return "RIGHT" 
                if ax - 1 > -1 and board[ax - 1, ay] == 0:
                    return "LEFT" 
                if ay + 1 < self.size and board[ax, ay + 1] == 0:
                    return "UP" 
                if ay - 1 > -1 and board[ax, ay - 1] == 0:
                    return "DOWN" 
        else:
            print("一番近い餌はありません")
            return self.__escape(board,player,enemies)

                    
    def __get_food_mindis(self,data,board,player,enemies):
        ax,ay = player["body"][0]
        enemies_head = [enemy["body"][0] for enemy in enemies]
        tmp_closest = True
        self.food_closest = False
        mindis = 100
        priority_food = 100
        
        food_mindis=[]
        tmp = []
        ene_food_mindis = []
        for i,food in enumerate(data["food"]):
            fx,fy = food
            food_mindis.append(abs(fx-ax)+abs(fy-ay))
            #餌が角にあったら3マス以上差が無いと取りにいけないようにする
            if (fx==0 or fx==data["size"]-1) and (fy==0 or fy==data["size"]-1):
                food_mindis[i] += 2
            tmp_closest = True
            #餌の最短距離を自分と他の敵で比較する
            for j, enemy_head in enumerate(enemies_head):
                ene_ax, ene_ay = enemy_head
                tmp.append(abs(fx-ene_ax)+abs(fy-ene_ay))
                if food_mindis[i] > tmp[j] or (food_mindis[i] == tmp[j] and len(player["body"]) <= len(enemies[j]["body"])):
                    tmp_closest = False
            #最短距離の餌が複数あるときは,1番距離が短い餌を選ぶ
            if tmp_closest == True:
                self.food_closest = True
                if mindis > food_mindis[i]:
                    mindis = food_mindis[i]
                    priority_food = i
                    
            ene_food_mindis.append(tmp)
            tmp.clear()

        return food_mindis,ene_food_mindis,priority_food


    def __avoid_collision(self, x, y, player, enemies):
        enemies_head = [enemy["body"][0] for enemy in enemies]
        player_len = len(player["body"])
        enemies_len = [len(enemy["body"]) for enemy in enemies]

        for i, enemy_head in enumerate(enemies_head):
            enemy_x, enemy_y = enemy_head
            if abs(x - enemy_x) + abs(y - enemy_y) == 1 and player_len <= enemies_len[i]:
                return False

        return True


    def __move_check(self, board,player,enemies):
        ax,ay = player["body"][0]
        d = []
        if ax - 1 > -1 and board[ax - 1, ay] < 2 and self.__avoid_collision(ax - 1, ay, player, enemies):
            d.append("LEFT")
        if ax + 1 < self.size and board[ax + 1, ay] < 2 and self.__avoid_collision(ax + 1, ay, player, enemies):
            d.append("RIGHT") 
        if ay - 1 > -1 and board[ax , ay - 1] < 2 and self.__avoid_collision(ax, ay - 1, player, enemies):
            d.append("DOWN") 
        if ay + 1 < self.size and board[ax , ay + 1] < 2 and self.__avoid_collision(ax, ay + 1, player, enemies):
            d.append("UP") 

        return d


    def __best_route(self,board,player,fx,fy,x,y):
        ax, ay = player["body"][0]
        d = "ERROR"
        flag = False
        if ax-fx > 0:
            x_code = -1
        else:
            x_code = 1
        if ay-fy > 0:
            y_code = -1
        else:
            y_code = 1

        if (ax-fx > -x and x_code == -1) or (ax-fx < -x and x_code == 1):
            print("aa")
            x += x_code
            if board[ax+x][ay] == 0:
                d,flag = self.__best_route(board,player,fx,fy,x,y)
                print("x",d)
            elif board[ax+x][ay] == 1:
                if x_code == 1:
                    d = "RIGHT"
                elif x_code == -1:
                    d = "LEFT"
                return d, True
            else:
                if  (ay-fy > -y and y_code == -1) or (ay-fy < -y and y_code == 1):
                    x -= x_code
                    y += y_code
                    d,flag = self.__best_route(board,player,fx,fy,x,y)
                else:
                    return "ERROR", False
        
        if d != "ERROR" and flag == True:
            if x_code == 1:
                d = "RIGHT"
            elif x_code == -1:
                d = "LEFT"
            return d, True
        elif (ay-fy > -y and y_code == -1) or (ay-fy < -y and y_code == 1):
            print("bb")
            y += y_code
            if board[ax+x][ay+y] == 0:
                d,flag = self.__best_route(board,player,fx,fy,x,y)
                print("y",d)
            elif board[ax+x][ay+y] == 1:
                if y_code == 1:
                    d = "UP"
                elif y_code == -1:
                    d = "DOWN"
                return d, True
            else:
                return "ERROR", False
        
        if d != "ERROR" and flag == True:
            if y_code == 1:
                    d = "UP"
            elif y_code == -1:
                d = "DOWN"
            return d, True

        return "ERROR", True


    def __strategy_decision(self,board,player,enemies,fx,fy):
        ax, ay = player["body"][0]
        my_health = player["health"]
        ene_health = enemies[0]["health"]
        fmin = abs(fx-ax)+abs(fy-ay)
        """ 長さを敵の長さより1大きくに変更する"""
        #餌まわりに囲いを作れるか判定
        if ((0<fx<self.size-1) and (0<fy<self.size-1)) and((len(player["body"]) == 7)or(len(player["body"]) == 8))and ((fmin<2) or (fmin<3 and self.strategy=="enclosure")):
            if self.strategy == "enclosure":
                self.s_count -= 1
            else:
                self.strategy = "enclosure"
                if my_health > ene_health:
                    self.s_count = my_health - 2
                else:
                    self.s_count = 50
        #作戦が続行できなくなったとき(餌がとられたときなど)は1ターンだけ作戦を続行するようにする
        elif self.strategy != "food" and self.s_count > 0:
            print(self.strategy,"作戦は次ターンで終わり")
            self.s_count = 0
        elif self.s_count == 0:
            self.strategy = "food"
        print("作戦：",self.strategy)


    def __strategy(self,board,player,enemies,fx,fy):
        if self.strategy == "kakomiko":
            d = self.__kakomiko(board,player,fx,fy)
        elif self.strategy == "eruzio":
            d = self.__eruzio(board,player,fx,fy)
        elif self.strategy == "enclosure":
            d = self.__enclosure(board,player,fx,fy)

        if d == "ERROR":
            print("作戦失敗")
        return d

        
    def __kakomiko(self,board,player,fx,fy):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        if zx-ax>0 and ((board[ax + 1, ay] <2 ) or ((ax+1==zx)and(ay==zy))):
            return "RIGHT"
        elif zx-ax<0 and ((board[ax - 1, ay] <2 ) or ((ax-1==zx)and(ay==zy))):
            return "LEFT"
        elif zy-ay>0 and ((board[ax , ay + 1] <2 ) or ((ax==zx)and(ay+1==zy))):
            return "UP"
        elif zy-ay<0 and ((board[ax , ay - 1] <2 ) or ((ax==zx)and(ay-1==zy))):
            return "DOWN"
        else:
            return "ERROR"


    def __eruzio(self,board,player,fx,fy):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        #えるじおが起動して一回目
        if self.s_count == 50:
            if ax + 1 < self.size and board[ax + 1, ay] == 0:
                self.eruzio_d = "RIGHT"
            if ax - 1 > -1 and board[ax - 1, ay] == 0:
                self.eruzio_d = "LEFT"
            if ay + 1 < self.size and board[ax, ay + 1] == 0:
                self.eruzio_d = "UP"
            if ay - 1 > -1 and board[ax, ay - 1] == 0:
                self.eruzio_d = "DOWN"
            else:
                self.eruzio_d = "ERROR"
            return self.eruzio_d

        elif self.s_count == 49:
            if fx-ax>0 and ((board[ax + 1, ay] <2 ) or ((ax+1==zx)and(ay==zy))):
                return "RIGHT"
            elif fx-ax<0 and ((board[ax - 1, ay] <2 ) or ((ax-1==zx)and(ay==zy))):
                return "LEFT"
            elif fy-ay>0 and ((board[ax , ay + 1] <2 ) or ((ax==zx)and(ay+1==zy))):
                return "UP"
            elif fy-ay<0 and ((board[ax , ay - 1] <2 ) or ((ax==zx)and(ay-1==zy))):
                return "DOWN"
            else:
                return "ERROR"
        elif self.s_count == 48:
            return self.eruzio_d
        else:
            if zx-ax>0 and ((board[ax + 1, ay]==0 ) or ((ax+1==zx)and(ay==zy))):
                return "RIGHT"
            elif zx-ax<0 and ((board[ax - 1, ay]==0 ) or ((ax-1==zx)and(ay==zy))):
                return "LEFT"
            elif zy-ay>0 and ((board[ax , ay + 1]==0 ) or ((ax==zx)and(ay+1==zy))):
                return "UP"
            elif zy-ay<0 and ((board[ax , ay - 1]==0 ) or ((ax==zx)and(ay-1==zy))):
                return "DOWN"


    def __enclosure(self,board,player,fx,fy):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]
        d=[]
        if (fx-ax==1 and fy-ay==0) or (fx-ax==-1 and fy-ay==0):
            if ay + 1 < self.size and (board[ax, ay + 1] == 0 or ((ax==zx)and(ay+1==zy))):
                d.append("UP")
            if ay - 1 > -1 and (board[ax, ay - 1] == 0 or ((ax==zx)and(ay-1==zy))):
                d.append("DOWN")
        if (fy-ay==1 and fx-ax==0) or (fy-ay==-1 and fx-ax==0):
            if ax + 1 < self.size and (board[ax + 1, ay] == 0 or ((ax+1==zx)and(ay==zy))):
                d.append("RIGHT")
            if ax - 1 > -1 and (board[ax - 1, ay] == 0 or ((ax-1==zx)and(ay==zy))):
                d.append("LEFT")
        if len(d)!=0:
            return random.choice(d)
        else: 
            return "ERROR"

    #ボードを分割して敵がいないところに行く
    def __escape(self, board, player, enemies):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        d = []

        tx = 5
        ty = 5

        #エリアごとに0と1以外の数を数える。左下0、右下1、左上2、右上3。
        area = [0, 0, 0, 0]
        for i in range(0,11):
            for j in range(0,11):
                if board[i,j] > 1:
                    if i < 5 and j < 6:
                        area[0] += 1
                    elif j < 6:
                        area[1] += 1
                    elif i < 5:
                        area[2] += 1
                    else:
                        area[3] += 1
        print(area)
        #目的地決定
        if area[0] <= area[1] and area[0] <= area[2] and area[0] <= area[3]:
            tx = 2
            ty = 2
        elif area[1] <= area[0] and area[1] <= area[2] and area[1] <= area[3]:
            tx = 8
            ty = 2
        elif area[2] <= area[0] and area[2] <= area[1] and area[2] <= area[3]:
            tx = 2
            ty = 8
        elif area[3] <= area[0] and area[3] <= area[1] and area[3] <= area[2]:
            tx = 8
            ty = 8
        print(tx,ty)

        d = self.__move_check(board,player,enemies)
        
        if tx-ax>0 and ((board[ax + 1, ay] <2 )):
            if "RIGHT" in d:
        	    return "RIGHT"
        elif tx-ax<0 and ((board[ax - 1, ay] <2 )):
            if "LEFT" in d:
        	    return "LEFT"
        elif ty-ay>0 and ((board[ax , ay + 1] <2 )):
            if "UP" in d:
        	    return "UP"
        elif ty-ay<0 and ((board[ax , ay - 1] <2 )):
            if "DOWN" in d:
        	    return "DOWN"
        
        if len(d) == 0:
            return "UP"
        else: return random.choice(d)
