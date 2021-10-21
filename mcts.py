import random
import numpy as np

class MCTS():
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.board = None
        self.check_v_board = None #使わないかも
        self.player_datas = None

        self.org_data = None

        self.now_direction = 0
        self.direction_pts = [0, 0, 0, 0]

        self.depth = 1

    def __reset(self):
        self.now_direction = 0
        self.direction_pts = [0, 0, 0, 0]

    def __get_ene_data(self, data):
        ene_datas = []
        for i in data["players"]:
            if i["name"] != self.name:
                ene_datas.append(i)
        
        return ene_datas

    
    def __direction_limiter(self, player_data, v_board, direction):
        #print(v_board)
        v_d = []
        #print("__direction_limiter player_data[0] = ", player_data)
        #print("__direction_limiter player_data['body'][0] = ", player_data["body"])
        x, y = player_data["body"][0]
        if x + 1 < self.size and v_board[x + 1, y] < 2:
            v_d.append(0) #RIGHT
        if x - 1 > -1 and v_board[x - 1, y] < 2:
            v_d.append(1) #LEFT
        if y + 1 < self.size and v_board[x, y + 1] < 2:
            v_d.append(2) #UP
        if y - 1 > -1 and v_board[x, y - 1] < 2:
            v_d.append(3) #DOWN

        #print("__direction_limiter direction = ", direction, " v_d = ", v_d)
        if direction in v_d:
            return False
        else:
            #print("")
            #print("x:", x, " y:", y, "v_board[x,y]=", v_board[x,y], " body:", player_data['body'])
            #print("RIGHT:", v_board[x + 1, y], " LEFT:", v_board[x - 1, y], " UP:", v_board[x, y + 1], " DOWN:", v_board[x, y - 1])
            #print("__direction_limiter", direction, " v_d = ", v_d)
            return True
    '''
    def __direction_limiter(self, player_data, v_board, direction):
        x, y = player_data["body"][0]
        if direction == 0:
            if x + 1 < self.size and v_board[x + 1, y] < 2:
                return False #RIGHT
        elif direction == 1:
            if x - 1 > -1 and v_board[x - 1, y] < 2:
                return False #LEFT
        elif direction == 2:
            if y + 1 < self.size and v_board[x, y + 1] < 2:
                return False #UP
        elif direction == 3:
            if y - 1 > -1 and v_board[x, y - 1] < 2:
                return False #DOWN

        return True
    '''

    def __get_food_posi(self, x, y):
        fx = -1
        fy = -1

        for i,j in self.org_data["food"]:
            mindis = 20
            distance=abs(i-x)+abs(j-y)
            if mindis>distance :
                mindis=distance
                fx=i
                fy=j
        
        return fx, fy

    def __score_calculate(self, v_player_datas):
        #餌の近さ　＋　長さ＊HP
        pts = []
        #rank_pt = 3

        for i,p in enumerate(v_player_datas):
            hx, hy = p["body"][0]
            fx, fy = self.__get_food_posi(hx, hy)
            pt = p["health"] *  len(p["body"])#基礎pt
            if p["health"] == 0 and i == 0:#自分が死んでたら
                pt = 0
            elif p["health"] == 0 and i > 0:#敵が死んでたら
                pt = pt*2
            
            f_distance=abs(hx-fx)+abs(hy-fy)
            if not f_distance == 0:
                pt = pt / (2*f_distance)
            
            pts.append(pt)
        
        '''
        for i in pts:
            if pts[0] < i:
                rank_pt = rank_pt - 1
        '''
        
        #print("__score_calculate direction_pts[self.now_direction] = ", self.direction_pts[self.now_direction], "rank_pt = ", rank_pt)
        #self.direction_pts[self.now_direction] = int(self.direction_pts[self.now_direction]) + rank_pt
        self.direction_pts[self.now_direction] = int(self.direction_pts[self.now_direction]) + pts[0]

    def __collision_check(self, v_player_datas):
        bodys_no_heads = []
        heads = []
        
        for i in v_player_datas:
            for j,b in enumerate(i["body"]):
                if j > 0:
                    bodys_no_heads.append(b)
                else:
                    heads.append(b)

        for i in v_player_datas:#他人の体に触れたら
            if i["body"][0] in bodys_no_heads:
                i["health"] = 0
        
        for i, my_h in enumerate(v_player_datas):#他人の頭に触れたら
            for j,ene_h in enumerate(heads):
                if i != j and my_h == ene_h:
                    if len(v_player_datas[i]["body"]) > len(v_player_datas[j]["body"]):
                        v_player_datas[j]["health"] = 0
                    else:
                        v_player_datas[i]["health"] = 0
        
        return v_player_datas
        
    def __make_v_board(self, v_player_datas, v_board):#仮想ボートの更新、衝突に殺すか否か
        new_v_board = v_board
        new_v_player_datas = []
        food_flag = 0

        v_player_datas = self.__collision_check(v_player_datas)

        for p in v_player_datas:
            s_len = len(p["body"])
            hx, hy = p["body"][0]
            nx, ny = p["body"][1]
            tx, ty = p["body"][s_len - 1]

            if new_v_board[hx, hy] == 1:#そこに飯があった
                food_flag = 1
            new_v_board[hx, hy] = new_v_board[nx, ny]
            new_v_board[tx, ty] = 0

            if food_flag != 1:#飯を食い損ねたら伸びないので尻尾を消去
                p["body"].pop()
            else:
                p["health"] = 100
                #ここで新しい飯の位置を考慮すべきだが、不確定要素すぎるので無視
            new_v_player_datas.append(p)
        
        return new_v_player_datas, new_v_board



    def __v_move(self, v_player_datas, v_board, turn):
        #my_v_player_datas = v_player_datas
        #my_v_board = v_board
        direction = np.zeros(len(v_player_datas), dtype=int)
        d_count = 0
        turn_flag = True
        retry_flag = False

        #全探索
        while turn_flag:
            my_v_player_datas = v_player_datas
            my_v_board = v_board
            if turn == self.depth:
                self.now_direction = direction[0]

            retry_flag = False
            for i,p in enumerate(my_v_player_datas):
                if(self.__direction_limiter(p, my_v_board, direction[i])):#探索不能な場合のリミッター
                #print("can't go player", i, " direction:", direction[i])
                    retry_flag = True
            
            if not retry_flag:
                #print("searching", turn, direction)
                for i,p in enumerate(my_v_player_datas):
                    head = my_v_player_datas[i]["body"][0]
                    hx, hy = head
                    #if(self.__direction_limiter(p, my_v_board, d))#リミッターの位置を要改良
                    #    continue
                    #else:# 0:右 1:左 2:上 3:下
                    d = direction[i]
                    if d == 0:
                        my_v_player_datas[i]["body"].insert(0, (hx + 1, hy))
                    elif d == 1:
                        my_v_player_datas[i]["body"].insert(0, (hx - 1, hy))
                    elif d == 2:
                        my_v_player_datas[i]["body"].insert(0, (hx, hy + 1))
                    elif d == 3:
                        my_v_player_datas[i]["body"].insert(0, (hx, hy - 1))
                    #self.v_player_datas["body"].pop()
                
                #このタイミングで餌を食べて成長したか、衝突したか、HP管理を行う
                my_v_player_datas, my_v_board  = self.__make_v_board(my_v_player_datas, my_v_board)
                if turn > 0:
                    #print("go next turn")
                    self.__v_move(my_v_player_datas, my_v_board, turn - 1)
                else:
                    #print("calculate score")
                    self.__score_calculate(my_v_player_datas)#その手を打った時に勝っているのかの点数づけも行う

            #そのターンでの全事象を試したか確認
            for d in direction:
                if d == 3:
                    d_count =  d_count + 1
            if d_count == len(my_v_player_datas):
                turn_flag = False
                for p in range(len(my_v_player_datas)):
                    direction[p] = 0
            else:#出なければカウントアップ
                d_count = 0
                for p in range(len(my_v_player_datas)):
                    i = (len(my_v_player_datas)-1) - p
                    if i == (len(my_v_player_datas)-1):
                        direction[i] = direction[i] + 1
                    if direction[i] > 3:
                        direction[i] = 0
                        direction[i - 1] = direction[i - 1] + 1

            my_v_player_datas = v_player_datas#再初期化


    def monte_direction_indicator(self, my_datas, data, board):
        self.__reset()
        self.size =  data["size"]
        self.org_data = data

        self.board = board
        self.player_datas = []
        self.player_datas.append(my_datas)
        ene_datas = self.__get_ene_data(data)
        for p in ene_datas:
            self.player_datas.append(p)

        #初期化
        v_board = self.board 
        v_player_datas = self.player_datas
        
        direction_choices = ["RIGHT", "LEFT", "UP", "DOWN"]# 0:右 1:左 2:上 3:下

        
        #全探索
        self.__v_move(v_player_datas, v_board, self.depth)

        #ここで選択肢を決める
        result = -1
        pt_tmp = 0
        for i,c in enumerate(self.direction_pts):
            if pt_tmp < c:
                pt_tmp = c
                result = i
        
        #print("self.direction_pts = ", self.direction_pts)
        #print("finish mcts")
        if result == -1:
            return "RAND"
        else:
            return direction_choices[result]