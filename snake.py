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

    # 近くにfoodがある場合は取りに行く。
    # 基本は移動できるところをランダムで
    def move(self, data):
        board = self.__get_board(data)
        player = [p for p in data["players"] if p["name"] == self.name][0]

        #自分(a)以外は餌を優先的に取りに行くモードでプレイ
        if player["name"] != "a":
            tmp = self.__enemy_move(data,player)
            return tmp

        print("food",data["food"])
        #enemys:敵のplayersデータ。敵が複数いても管理できるようにした
        enemys = self.__get_ene_data(data)
        ene_num = len(enemys)

        d = []
        food_closest =True
        
        #敵の数が1体の時は__1vs1で取得
        if ene_num == 1:
            tmp = self.__1vs1(data,board,player,enemys[0])
            return tmp

        #自分の体の最初と最後の座標を取得
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]
        #自分の体の最後の座標を一時的に0にすることで移動可能マスとして扱う
        if data["turn"] > 1: 
            board[zx,zy] = 0
        
        #自分の頭から一番近い餌の座標を取得
        fx,fy,fmin = self.__get_food_mindis(data,player)
        #print(fx,fy,fmin)

        #敵の頭から一番近い餌の座標を取得
        ene_food_mindis = [[0 for i in range(3)] for j in range(ene_num)]
        for n in range(ene_num):
            ene_fx,ene_fy,ene_fmin = self.__get_food_mindis(data,enemys[n])
            ene_food_mindis[n][0] = ene_fx
            ene_food_mindis[n][1] = ene_fy
            ene_food_mindis[n][2] = ene_fmin
            #敵の一番近い餌が自分と同じとき、最短距離を比較する
            if fx==ene_fx and fy==ene_fy:
                if fmin > ene_fmin:
                    food_closest = False #一番近くない時はFalse
                elif fmin == ene_fmin:
                    #距離が同じときは体の長さで判定
                    food_closest = (len(player["body"])>len(enemys[n]["body"]))

        #print(ene_food_mindis)        


        #移動可能な場所を選択肢として追加
        if ax + 1 < self.size and board[ax + 1, ay] == 0:
            d.append("RIGHT")
        if ax - 1 > -1 and board[ax - 1, ay] == 0:
            d.append("LEFT")
        if ay + 1 < self.size and board[ax, ay + 1] == 0:
            d.append("UP")
        if ay - 1 > -1 and board[ax, ay - 1] == 0:
            d.append("DOWN")

        if ene_num == 3: 
            #if abs(fx-ax)<3 and abs(fy-ay)<3:     #foodまでの距離が縦横2マス以内なら取りに行く
            if food_closest:
                print("一番近い！！")
                if fx-ax>0 and (board[ax + 1, ay] <2 ):
                    board[zx,zy] = board[ax,ay]
                    return "RIGHT"
                elif fx-ax<0 and (board[ax - 1, ay] <2 ):
                    board[zx,zy] = board[ax,ay]
                    return "LEFT"
                elif fy-ay>0 and (board[ax , ay + 1] <2 ):
                    board[zx,zy] = board[ax,ay]
                    return "UP"
                elif fy-ay<0 and (board[ax , ay - 1] <2 ):
                    board[zx,zy] = board[ax,ay]
                    return "DOWN"
            if len(d) == 0:
                board[zx,zy] = board[ax,ay]
                return "UP"
            else:
                board[zx,zy] = board[ax,ay]
                return random.choice(d)

        elif ene_num == 2:
            if fx-ax>0 and (board[ax + 1, ay] <2 ):
                board[zx,zy] = board[ax,ay]
                return "RIGHT"
            elif fx-ax<0 and (board[ax - 1, ay] <2 ):
                board[zx,zy] = board[ax,ay]
                return "LEFT"
            elif fy-ay>0 and (board[ax , ay + 1] <2 ):
                board[zx,zy] = board[ax,ay]
                return "UP"
            elif fy-ay<0 and (board[ax , ay - 1] <2 ):
                board[zx,zy] = board[ax,ay]
                return "DOWN" 
            elif len(d) == 0:
                board[zx,zy] = board[ax,ay]
                return "UP"
            else:
                board[zx,zy] = board[ax,ay]
                return random.choice(d)
        
        else: 
            board[zx,zy] = board[ax,ay]
            return random.choice(d)


    def __1vs1(self,data,board,player,enemys):
        #自分の体の最初と最後の座標を取得
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]
        if data["turn"] > 1: 
            board[zx,zy] = 0
        
        d = []
        
        #自分の頭から一番近い餌の座標を取得
        fx,fy,fmin = self.__get_food_mindis(data,player)

        #敵の頭から一番近い餌の座標を取得
        ene_fx,ene_fy,ene_fmin = self.__get_food_mindis(data,enemys)

        #移動可能な場所を選択肢として追加
        if ax + 1 < self.size and board[ax + 1, ay] == 0:
            d.append("RIGHT")
        if ax - 1 > -1 and board[ax - 1, ay] == 0:
            d.append("LEFT")
        if ay + 1 < self.size and board[ax, ay + 1] == 0:
            d.append("UP")
        if ay - 1 > -1 and board[ax, ay - 1] == 0:
            d.append("DOWN")
        
        #囲いを作る戦法
        if ((len(player["body"])== 7) or(len(player["body"])==8)):
            tmp = self.__enclosure(board,player,fx,fy)
            return tmp

        if fx-ax>0 and (board[ax + 1, ay] <2 ):
        	return "RIGHT"
        elif fx-ax<0 and (board[ax - 1, ay] <2 ):
        	return "LEFT"
        elif fy-ay>0 and (board[ax , ay + 1] <2 ):
        	return "UP"
        elif fy-ay<0 and (board[ax , ay - 1] <2 ):
        	return "DOWN"
        elif len(d) == 0:
            return "UP"
        else: return random.choice(d)

    def __get_ene_data(self,data):
        ene_datas = []
        for i in data["players"]:
            if i["name"]!=self.name:
                enemy = [p for p in data["players"] if p["name"] == i["name"]][0]
                ene_datas.append(enemy)
        return ene_datas

    def __get_food_mindis(self,data,player):
        ax, ay = player["body"][0]
        #print(ax,ay)
        fx=fy=6
        food_mindis=20
        for i,j in data["food"]:
        	distance=abs(i-ax)+abs(j-ay)
        	if food_mindis>distance:
        		food_mindis=distance
        		fx=i
        		fy=j
        return fx,fy,food_mindis

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
            return "UP"

    def __enemy_move(self,data,player):
        board = self.__get_board(data)
        head = player["body"][0]

        x, y = head
        d = []

        fx=fy=6
        
        mindis=20
        for i,j in data["food"]:
        	distance=abs(i-x)+abs(j-y)
        	if mindis>distance:
        		mindis=distance
        		fx=i
        		fy=j
        

        if x + 1 < self.size and board[x + 1, y] == 0:
            d.append("RIGHT")
        if x - 1 > -1 and board[x - 1, y] == 0:
            d.append("LEFT")
        if y + 1 < self.size and board[x, y + 1] == 0:
            d.append("UP")
        if y - 1 > -1 and board[x, y - 1] == 0:
            d.append("DOWN")

        if fx-x>0 and (board[x + 1, y] <2 ):
        	return "RIGHT"
        elif fx-x<0 and (board[x - 1, y] <2 ):
        	return "LEFT"
        elif fy-y>0 and (board[x , y + 1] <2 ):
        	return "UP"
        elif fy-y<0 and (board[x , y - 1] <2 ):
        	return "DOWN"
        elif len(d) == 0:
            return "UP"
        else: return random.choice(d)
