import random
import traceback
import numpy as np
import copy
import pickle

class MTS:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.choices = ["RIGHT", "LEFT", "UP", "DOWN"] 
        self.ene_id = {}
        self.depth = 1

        self.now_direction = 0
        self.direction_pts = [0, 0, 0, 0]
        self.org_data = None
        self.recently_ene = ""
        self.dict_dead = []

    def __reset(self, data):
        self.now_direction = 0
        self.direction_pts = [1000, 1000, 1000, 1000]
        self.org_data = copy.deepcopy(data)
        self.dict_dead = []
    
    def __get_one_data(self, data, player_name):
        for i in data["players"]:
            if i["name"] == player_name:
                #print(i)
                return i
        #print(player_name, " was game over")
        return {'name': player_name, 'health': 0, 'body': []}

    def __get_recently_enemy(self, ene_names):
        min_enename = ""
        min_heads = (1000, 1000)
        for e in ene_names:
            p = self.__get_one_data(self.org_data, e)
            if len(p["body"]) < 1:
                continue
            px, py = p["body"][0]
            x,y = min_heads

            if (px + py) < (x+y):
                min_enename = e
        return min_enename

    def __direction_limiter(self, player_data, v_board, direction):
        v_d = []
        
        #print("limiter playerdata = ", player_data)
        if player_data["health"] == 0 or len(player_data["body"]) < 1:
            return False

        x, y = player_data["body"][0]
        if x + 1 < self.size and v_board[x + 1, y] < 2:
            v_d.append(0) #RIGHT
        if x - 1 > -1 and v_board[x - 1, y] < 2:
            v_d.append(1) #LEFT
        if y + 1 < self.size and v_board[x, y + 1] < 2:
            v_d.append(2) #UP
        if y - 1 > -1 and v_board[x, y - 1] < 2:
            v_d.append(3) #DOWN
    
        if direction in v_d:
            return False
        else:
            return True

    def __collision_check(self, v_data):
        #new_v_data = copy.deepcopy(v_data)
        new_v_data = pickle.loads(pickle.dumps(v_data, -1))
        for i,player in enumerate(new_v_data["players"]):
            head_1 = player["body"][0]
            hx_1, hy_1 = head_1
            for j,ene_player in enumerate(new_v_data["players"]):
                if i < j:
                    head_2 = ene_player["body"][0]
                    hx_2, hy_2 = head_2
                    if hx_1 == hx_2 and hy_1 == hy_2:
                        if len(player["body"]) > len(ene_player["body"]):
                            #ene_player["health"] = 0
                            new_v_data["players"][j]["health"] = 0
                        elif len(player["body"]) < len(ene_player["body"]):
                            #player["health"] = 0
                            new_v_data["players"][i]["health"] = 0
                            self.dict_dead.append(self.now_direction)
                        else:
                            #player["health"] = 0
                            #ene_player["health"] = 0
                            new_v_data["players"][i]["health"] = 0
                            new_v_data["players"][j]["health"] = 0
        return new_v_data

    def __make_v_data(self, data, board, ene_names, my_d, direction):
        #v_data = copy.deepcopy(data)
        v_data = pickle.loads(pickle.dumps(data, -1))
        v_board = copy.deepcopy(board)

        directions = []
        directions.append(my_d)
        for d in direction:
            directions.append(d)
        
        no_tails = []
        #player_names = []
        #player_names.append(self.name)
        #for ene_name in ene_names:
        #    player_names.append(ene_name)
        '''
        player_names.append(self.__get_one_data(v_data, self.name))
        for ene_name in ene_names:
            player_names.append(self.__get_one_data(v_data, ene_name))
        '''
        ene_count = 0
        for i,player in enumerate(v_data["players"]):
            #print("player", player)
            head = player["body"][0]
            hx, hy = head
                
            #進行
            food_flag = False
            if player["name"] == self.name:
                d = directions[0]
            else:
                d = directions[self.ene_id[player["name"]]+1]
                ene_count = ene_count + 1

            if d == 0:
                #player["body"].insert(0, (hx + 1, hy))
                v_data["players"][i]["body"].insert(0, (hx + 1, hy))
                if hx + 1 < self.size and v_board[hx + 1, hy] == 1:#進んだ先に飯があったら
                    food_flag = True
            elif d == 1:
                #player["body"].insert(0, (hx - 1, hy))
                v_data["players"][i]["body"].insert(0, (hx - 1, hy))
                if hx - 1 < self.size and v_board[hx - 1, hy] == 1:
                    food_flag = True
            elif d == 2:
                #player["body"].insert(0, (hx, hy + 1))
                v_data["players"][i]["body"].insert(0, (hx, hy + 1))
                if hy + 1 < self.size and v_board[hx, hy + 1] == 1:
                    food_flag = True
            elif d == 3:
                player["body"].insert(0, (hx, hy - 1))
                v_data["players"][i]["body"].insert(0, (hx, hy - 1))
                if hy - 1 < self.size and v_board[hx, hy - 1] == 1:
                    food_flag = True

            #尾の処理
            if food_flag == False:
                no_tails.append(player["body"][-1])
                player["body"].pop()

        v_data = self.__collision_check(v_data)
    
        #ボードの更新
        for i,p in enumerate(v_data["players"]):#新しい位置を更新
            for b in p["body"]:
                bx,by = b
                if p["health"] == 0:
                    v_board[bx, by] = 0
                else:
                    if p["name"] == self.name:
                        v_board[bx, by] = 2
                    else:
                        #print("v_board[bx, by]", bx, ":", by)
                        v_board[bx, by] = 3
                
        for ox,oy in no_tails:
            v_board[ox, oy] = 0
        
        return v_data, v_board

    def __get_food_posi(self, x, y):
        fx = -1
        fy = -1

        for i,j in self.org_data["food"]:
            #print("food posi = ", i, ":", j)
            mindis = 100
            distance=abs(i-x)+abs(j-y)
            if mindis>distance :
                mindis=distance
                fx=i
                fy=j
        
        return fx, fy

    def __score_calculate(self, v_data):
        #餌の近さ　＋　長さ＊HP
        pts = []
        my_id = 0
        dead_flag = False

        for i,p in enumerate(v_data["players"]):
            hx, hy = p["body"][0]
            fx, fy = self.__get_food_posi(hx, hy)
            
            f_distance = -1
            f_distance = abs(hx-fx)+abs(hy-fy)
            pt = f_distance#少ないほど良い
            if p["health"] == 0 and p["name"] == self.name:#自分が死んでたら
                #print("I'll be dead end...")
                pt = 100000
                dead_flag=True
            elif p["health"] == 0 and p["name"] != self.name:#敵が死んでたら
                #print("Kill You!")
                pt = pt/2
            if f_distance == 0 and dead_flag != True:
                pt = pt/2
                
            if p["name"] == self.name:
                my_id = i
                #pass
                #print("hx:hy = ", hx, ":", hy,"  fx:fy = ", fx, ":", fy, " f_distance = ", f_distance, "pt ", pt)

            pts.append(pt)

        #self.direction_pts[self.now_direction] = int(self.direction_pts[self.now_direction]) + pts[0]
        #print("pts[0] ", pts[0])
        if self.direction_pts[self.now_direction] > pts[my_id] or dead_flag:
            self.direction_pts[self.now_direction] = pts[my_id]

    def __inverse_lookup(self, d, x):
        for k,v in d.items():
            if x == v:
                return k

    def __v_move(self, player, ene_names, data, board, turn):
        direction = np.zeros(len(ene_names), dtype=int)
        turn_flag = True
        retry_flag = False
        this_turn = copy.deepcopy(turn)

        d_count = 0
        old_target_ene_d = -1
        for my_d in range(4):
            d_count = 0
            for p in range(len(direction)):
                direction[p] = 0
            
            if this_turn == self.depth:
                self.now_direction = my_d
            while turn_flag:
                #print(my_d, direction)
                   
                if self.__direction_limiter(player, board, my_d):
                    if this_turn == 0:
                        f_head = player["body"][0]
                        #print("future positon ", f_head ," I can't go ", self.choices[my_d])
                    else:
                        #print("I can't go ", self.choices[my_d])
                        pass
                    retry_flag = True
                else:
                    for i, ene_name in enumerate(ene_names):
                        ene_data =  self.__get_one_data(data, ene_name)                        
                        if self.__direction_limiter(ene_data, board, direction[self.ene_id[ene_name]]):
                            #print("Enemy ", ene_name," can't go ", self.choices[direction[self.ene_id[ene_name]]])
                            retry_flag = True
                
                if not retry_flag:
                    if direction[self.ene_id[self.recently_ene]] != old_target_ene_d:#==============================
                    #if True:
                        old_target_ene_d = direction[self.ene_id[self.recently_ene]]

                        v_data, v_board = self.__make_v_data(data, board, ene_names, my_d, direction)
                        f_player = [pp for pp in v_data["players"] if pp["name"] == self.name][0]
                        if this_turn == 0:
                            #print("head posi =", f_player["body"][0])
                            self.__score_calculate(v_data)
                        else:
                            self.__v_move(f_player, ene_names, v_data, v_board, this_turn -1)
                #==============================================================================================
                retry_flag = False

                for d in direction:
                    if d == 3:
                        d_count =  d_count + 1
                if d_count == len(direction):
                    turn_flag = False
                    for p in range(len(direction)):
                        direction[p] = 0
                else:#出なければカウントアップ
                    d_count = 0
                    for p in range(len(direction)):
                        ii = (len(direction)-1) - p
                        #ii = p
                        if ii == (len(direction)-1):
                            direction[ii] = direction[ii] + 1
                        if direction[ii] > 3 and ii > 0:
                            direction[ii] = 0
                            direction[ii - 1] = direction[ii - 1] + 1
            turn_flag = True

    def monte_direction_indicator(self, size, player, ene_names, data, board):

        self.size = size
        #my_ene_names = []
        #my_ene_names = ene_names.keys()
        self.ene_id = {}
        self.__reset(data)
        for i, name in enumerate(ene_names):
            self.ene_id[name] = i
        #print(self.ene_id)
        self.recently_ene = self.__get_recently_enemy(ene_names)
        #print("recently_ene = ", self.recently_ene)
        self.__v_move(player, ene_names, data, board, self.depth)
        
        #ここで選択肢を決める
        result = -1
        pt_tmp = 1000
        for i,c in enumerate(self.direction_pts):
            if pt_tmp > c and i not in self.dict_dead:
                pt_tmp = c
                result = i
        
        #hx, hy = player["body"][0]
        #fx, fy = self.__get_food_posi(hx, hy)
        #print("fx:fy = ", fx, ":", fy)
        print("self.direction_pts = ", self.direction_pts)
        #print("finish mcts")
        if result == -1:
            if pt_tmp == 1000:
                print("Dead end. Good bye.")
            return "RAND"
        else:
            return self.choices[result]