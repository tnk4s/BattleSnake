import random

import numpy as np

#�����p��Snake�����ɂ́Abattlesnake�Œ�`����Ă���Snake���p������K�v������
from battlesnake import Snake

# class����ύX�B���̃`�[���Ƃ��Ԃ�Ȃ��悤��

class Miya(Snake):

    def __init__(self, name):
        super().__init__(name)
        self.size = 0
        self.food_closest = False
        self.strategy = "food"
        self.s_count = 0
        self.eruzio_d = ""
        self.zahyoux=0
        self.zahyouy=0

    # �I����(�Q�[���I�[�o�[ or ����)�ɌĂ΂��
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

    # �߂���food������ꍇ�͎��ɍs���B
    # ��{�͈ړ��ł���Ƃ���������_����
    def move(self, data):
        board = self.__get_board(data)
        player = [p for p in data["players"] if p["name"] == self.name][0]
        enemies = [p for p in data["players"] if p["name"] != self.name]

        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        #�����̑̂̍Ō�̍��W���ꎞ�I��0�ɂ��邱�Ƃňړ��\�}�X�Ƃ��Ĉ���
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
        #�����̑̂̍ŏ��ƍŌ�̍��W���擾
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]
        
        #�����̓������ԋ߂��a�̍��W���擾
        food_mindis,ene_food_mindis,priority_food = self.__get_food_mindis(data,board,player,enemies)
        
        if priority_food != 100:
            fx,fy = data["food"][priority_food]
            fmin = food_mindis[priority_food]
            able_d = self.__move_check(board,player,enemies)
            print("���ɍs���ׂ��a��(",fx,fy,")�ōŒZ������",fmin,"�ł�")
            
            best_d,flag = self.__best_route(board,player,fx,fy,0,0)
            if best_d in able_d:
                print(best_d,"�ɐi�݂܂�")
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
            print("��ԋ߂��a�͂���܂���")
            return self.__escape(board,player,enemies)


    def __1vs1(self,data,board,player,enemies):
        #�����̑̂̍ŏ��ƍŌ�̍��W���擾
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        #�����̓������ԋ߂��a�̍��W���擾
        food_mindis,ene_food_mindis,priority_food = self.__get_food_mindis(data,board,player,enemies)
        
        if priority_food != 100 or self.strategy != "food":
            fx,fy = data["food"][priority_food]
            fmin = food_mindis[priority_food]
            able_d = self.__move_check(board,player,enemies)
            print("���ɍs���ׂ��a��(",fx,fy,")�ōŒZ������",fmin,"�ł�")
            best_d,flag = self.__best_route(board,player,fx,fy,0,0)
            self.__strategy_decision(board,player,enemies,fx,fy)
            if flag != "ERROR" and self.strategy != "food":
                strategy_d =  self.__strategy(board,player,enemies,fx,fy,fmin)
                if strategy_d in able_d:
                    print(strategy_d,"�ɐi�݂܂�")
                    return strategy_d
            elif best_d in able_d:
                print(best_d,"�ɐi�݂܂�")
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
            print("��ԋ߂��a�͂���܂���")
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
            #�a���p�ɂ�������3�}�X�ȏ㍷�������Ǝ��ɂ����Ȃ��悤�ɂ���
            if (fx==0 or fx==data["size"]-1) and (fy==0 or fy==data["size"]-1):
                food_mindis[i] += 2
            tmp_closest = True
            #�a�̍ŒZ�����������Ƒ��̓G�Ŕ�r����
            for j, enemy_head in enumerate(enemies_head):
                ene_ax, ene_ay = enemy_head
                tmp.append(abs(fx-ene_ax)+abs(fy-ene_ay))
                if food_mindis[i] > tmp[j] or (food_mindis[i] == tmp[j] and len(player["body"]) <= len(enemies[j]["body"])):
                    tmp_closest = False
            #�ŒZ�����̉a����������Ƃ���,1�ԋ������Z���a��I��
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
        """ ������G�̒������1�傫���ɕύX����"""
        #�����݂��ł��邩����
        if (((fx==0) and ((fy==0) or (fy==self.size-1))) or ((fx==self.size-1) and ((fy==0) or (fy==self.size-1)))) and(len(player["body"])> 6) and ((fmin < 2) or (fmin<5 and self.strategy=="kakomiko")):
            if self.strategy == "kakomiko":
                self.s_count -= 1
            else:
                self.strategy = "kakomiko"
                self.s_count = 50
        #���邶���ł��邩����
        elif ((fx==0) or (fy==0) or (fy==self.size-1) or (fx==self.size-1)) and(len(player["body"])>4) and ((fmin<2) or (fmin<4 and self.strategy=="eruzio")):
            if self.strategy == "eruzio":
                self.s_count -= 1
            else:
                self.zahyoux,self.zahyouy=player["body"][1]
                self.strategy = "eruzio"
                self.s_count = 50
        #�a�܂��Ɉ͂������邩����
        elif ((0<fx<self.size-1) and (0<fy<self.size-1)) and((len(player["body"]) == 7)or(len(player["body"]) == 8))and ((fmin<2) or (fmin<3 and self.strategy=="enclosure")):
            if self.strategy == "enclosure":
                self.s_count -= 1
            else:
                self.strategy = "enclosure"
                if my_health > ene_health:
                    self.s_count = my_health - 2
                else:
                    self.s_count = 50
        #��킪���s�ł��Ȃ��Ȃ����Ƃ�(�a���Ƃ�ꂽ�Ƃ��Ȃ�)��1�^�[���������𑱍s����悤�ɂ���
        elif self.strategy != "food" and self.s_count > 0:
            print(self.strategy,"���͎��^�[���ŏI���")
            self.s_count = 0
        elif self.s_count == 0:
            self.strategy = "food"
        print("���F",self.strategy)


    def __strategy(self,board,player,enemies,fx,fy,fmin):
        if self.strategy == "kakomiko":
            d = self.__kakomiko(board,player,fx,fy)
        elif self.strategy == "eruzio":
            d = self.__eruzio(board,player,fx,fy)
        elif self.strategy == "enclosure":
            d = self.__enclosure(board,player,fx,fy,fmin)

        if d == "ERROR":
            print("��편�s")
        return d

        
    def __kakomiko(self,board,player,fx,fy):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        if zx-ax>-1 and ((board[ax + 1, ay] ==0 ) or ((ax+1==zx)and(ay==zy))):
            return "RIGHT"
        elif zx-ax<-1 and ((board[ax - 1, ay] ==0 ) or ((ax-1==zx)and(ay==zy))):
            return "LEFT"
        elif zy-ay>-1 and ((board[ax , ay + 1] ==0 ) or ((ax==zx)and(ay+1==zy))):
            return "UP"
        elif zy-ay<-1 and ((board[ax , ay - 1] ==0 ) or ((ax==zx)and(ay-1==zy))):
            return "DOWN"
        else:
            return "ERROR"


    def __eruzio(self,board,player,fx,fy):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        #���邶�����N�����Ĉ���
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
        elif self.s_count<48:
            if (abs(self.zahyoux-ax)+abs(self.zahyouy-ay))==2:
                self.strategy = "food"
            if ((fx<4) or (self.size-4<fx)) and ((fy>2) or (self.size-1>fy)):
                if self.zahyouy-ay>0 and ((board[ax , ay + 1] <2 ) or ((ax==zx)and(ay+1==zy))):
                    return "UP"
                elif self.zahyouy-ay<0 and ((board[ax , ay - 1] <2 ) or ((ax==zx)and(ay-1==zy))):
                    return "DOWN"
                elif self.zahyoux-ax>0 and ((board[ax + 1, ay] <2 ) or ((ax+1==zx)and(ay==zy))):
                    return "RIGHT"
                elif self.zahyoux-ax<0 and ((board[ax - 1, ay] <2 ) or ((ax-1==zx)and(ay==zy))):
                    return "LEFT"
                else:
                    return "ERROR"
            else:    
                if self.zahyoux-ax>0 and ((board[ax + 1, ay] <2 ) or ((ax+1==zx)and(ay==zy))):
                    return "RIGHT"
                elif self.zahyoux-ax<0 and ((board[ax - 1, ay] <2 ) or ((ax-1==zx)and(ay==zy))):
                    return "LEFT"
                elif self.zahyouy-ay>0 and ((board[ax , ay + 1] <2 ) or ((ax==zx)and(ay+1==zy))):
                    return "UP"
                elif self.zahyouy-ay<0 and ((board[ax , ay - 1] <2 ) or ((ax==zx)and(ay-1==zy))):
                    return "DOWN"
                else:
                    return "ERROR"

    def __enclosure(self,board,player,fx,fy,fmin):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]
        d=[]
        if fmin==1:
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
        else:
            if fx-x>0 and (board[x + 1, y] <2 ):
        	    return "RIGHT"
            elif fx-x<0 and (board[x - 1, y] <2 ):
        	    return "LEFT"
            elif fy-y>0 and (board[x , y + 1] <2 ):
        	    return "UP"
            elif fy-y<0 and (board[x , y - 1] <2 ):
        	    return "DOWN"

    #�{�[�h�𕪊����ēG�����Ȃ��Ƃ���ɍs��
    def __escape(self, board, player, enemies):
        ax, ay = player["body"][0]
        zx, zy = player["body"][-1]

        d = []

        tx = 5
        ty = 5

        #�G���A���Ƃ�0��1�ȊO�̐��𐔂���B����0�A�E��1�A����2�A�E��3�B
        area = [0, 0, 0, 0]
        for i in range(0,self.size):
            for j in range(0,self.size):
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
        #�ړI�n����
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