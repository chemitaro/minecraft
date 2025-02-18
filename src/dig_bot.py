def on_on_chat():
    for コマンド名 in ["come",
        "branch_mining",
        "dig_fast",
        "dig_route",
        "where",
        "item_list",
        "store",
        "warp"]:
        player.say(コマンド名)
player.on_chat("help", on_on_chat)

def do指定座標にワープ(ワープ座標: Position):
    agent.teleport(ワープ座標, WEST)
def doエージェントの場所を表示():
    player.say("座標" + " : " + ("" + str(agent.get_position())))
    player.say("方角" + " : " + ("" + str(get方角を文字に変換(agent.get_orientation()))))
    player.say("周囲のブロック")
    player.say(" - " + "前" + " : " + blocks.name_of_block(agent.inspect(AgentInspection.BLOCK, FORWARD)))
    player.say(" - " + "後" + " : " + blocks.name_of_block(agent.inspect(AgentInspection.BLOCK, BACK)))
    player.say(" - " + "左" + " : " + blocks.name_of_block(agent.inspect(AgentInspection.BLOCK, LEFT)))
    player.say(" - " + "右" + " : " + blocks.name_of_block(agent.inspect(AgentInspection.BLOCK, RIGHT)))
    player.say(" - " + "上" + " : " + blocks.name_of_block(agent.inspect(AgentInspection.BLOCK, UP)))
    player.say(" - " + "下" + " : " + blocks.name_of_block(agent.inspect(AgentInspection.BLOCK, FORWARD)))

def on_on_chat2(掘削回数):
    do通路を掘る(掘削回数)
player.on_chat("dig_route", on_on_chat2)

def doエージェントのアイテムリストを表示():
    for カウンター in range(28):
        if カウンター < 1:
            continue
        player.say("" + str(カウンター) + " : " + blocks.name_of_block(agent.get_item_detail(カウンター)) + " : " + ("" + str(agent.get_item_count(カウンター))))
def do資源探索_左():
    for 資源ブロックnum in 資源ブロックコレクション:
        if agent.inspect(AgentInspection.BLOCK, LEFT) == 資源ブロックnum:
            player.say("" + str(agent.get_position()) + " : " + blocks.name_of_block(資源ブロックnum))
            doアイテムスペース確保()
            agent.destroy(LEFT)
            agent.collect_all()
            agent.move(LEFT, 1)
            do資源探索()
            agent.move(RIGHT, 1)
def do資源探索_下():
    for 資源ブロックnum2 in 資源ブロックコレクション:
        if agent.inspect(AgentInspection.BLOCK, DOWN) == 資源ブロックnum2:
            player.say("" + str(agent.get_position()) + " : " + blocks.name_of_block(資源ブロックnum2))
            doアイテムスペース確保()
            agent.destroy(DOWN)
            agent.collect_all()
            agent.move(DOWN, 1)
            do資源探索()
            agent.move(UP, 1)
def get採掘場所かどうか():
    if agent.get_position().get_value(Axis.Y) % 8 == 0:
        if agent.get_position().get_value(Axis.X) % 4 == 0:
            return 1
        return 0
    elif agent.get_position().get_value(Axis.Y) % 8 == 4 or agent.get_position().get_value(Axis.Y) % 8 == -4:
        if agent.get_position().get_value(Axis.X) % 4 == 2 or agent.get_position().get_value(Axis.X) % 4 == -2:
            return 1
        return 0
    else:
        return 0
def doエージェントの向きを指定する(向き: number):
    for index in range(4):
        if agent.get_orientation() == 向き:
            break
        agent.turn(RIGHT_TURN)

def on_on_chat3():
    agent.turn(RIGHT_TURN)
player.on_chat("turn_right", on_on_chat3)

def get方角を文字に変換(確認したい方角の数値: number):
    if 確認したい方角の数値 == -90:
        return "東"
    elif 確認したい方角の数値 == 0:
        return "南"
    elif 確認したい方角の数値 == 90:
        return "西"
    elif 確認したい方角の数値 == -180:
        return "北"
    else:
        return "不明な方角"
def get反対の方向(変換前の方向: number):
    if 変換前の方向 == FORWARD:
        return BACK
    elif 変換前の方向 == BACK:
        return FORWARD
    elif 変換前の方向 == LEFT:
        return RIGHT
    elif 変換前の方向 == RIGHT:
        return LEFT
    elif 変換前の方向 == UP:
        return DOWN
    elif 変換前の方向 == DOWN:
        return UP
    else:
        return 0
def do資源探索_上():
    for 資源ブロックnum3 in 資源ブロックコレクション:
        if agent.inspect(AgentInspection.BLOCK, UP) == 資源ブロックnum3:
            player.say("" + str(agent.get_position()) + " : " + blocks.name_of_block(資源ブロックnum3))
            doアイテムスペース確保()
            agent.destroy(UP)
            agent.collect_all()
            agent.move(UP, 1)
            do資源探索()
            agent.move(DOWN, 1)

def on_on_chat4():
    doブランチマイニング()
player.on_chat("branch_mining", on_on_chat4)

def on_on_chat5(ワープ座標x2):
    agent.move(UP, ワープ座標x2)
player.on_chat("up", on_on_chat5)

def on_on_chat6():
    agent.turn(LEFT_TURN)
player.on_chat("turn_left", on_on_chat6)

def on_on_chat7(掘削回数5):
    do高速に高さ2の穴を掘り進める(掘削回数5)
player.on_chat("dig_fast", on_on_chat7)

def doブランチマイニング():
    global ブランチマイニングのステップ数
    doエージェントの向きを指定する(-90)
    if agent.get_position().get_value(Axis.Y) % 4 == 0:
        pass
    else:
        player.say("高さが間違っています")
        return 0
    ブランチマイニングのステップ数 = 0
    for index2 in range(999):
        ブランチマイニングのステップ数 += 1
        player.say("Branch_mining" + " : " + ("" + str(ブランチマイニングのステップ数)) + "/" + "999" + ", " + ("" + str(agent.get_position())))
        if get採掘場所かどうか() == 1:
            if getエージェントの指定した方向が空いているかどうか(RIGHT) == 0:
                agent.turn(RIGHT_TURN)
                doマイニング(500)
                doアイテム納品()
                doエージェントの向きを指定する(-90)
            if getエージェントの指定した方向が空いているかどうか(LEFT) == 0:
                agent.turn(LEFT_TURN)
                doマイニング(500)
                doアイテム納品()
                doエージェントの向きを指定する(-90)
        if agent.inspect(AgentInspection.BLOCK, FORWARD) == AIR:
            pass
        else:
            agent.destroy(FORWARD)
        agent.move(FORWARD, 1)
    player.say("Branch_mining: finish")
    return 1
def do資源探索_右():
    for 資源ブロックnum4 in 資源ブロックコレクション:
        if agent.inspect(AgentInspection.BLOCK, RIGHT) == 資源ブロックnum4:
            player.say("" + str(agent.get_position()) + " : " + blocks.name_of_block(資源ブロックnum4))
            agent.destroy(RIGHT)
            agent.collect_all()
            agent.move(RIGHT, 1)
            do資源探索()
            agent.move(LEFT, 1)
def doアイテム納品():
    global 帰還方角, 帰還座標
    loops.pause(1000)
    帰還方角 = agent.get_orientation()
    帰還座標 = agent.get_position()
    agent.teleport(アイテム保管座標, WEST)
    loops.pause(1000)
    agent.drop_all(UP)
    agent.teleport(帰還座標, WEST)
    loops.pause(1000)
    doエージェントの向きを指定する(帰還方角)

def on_on_chat8(ワープ座標x, ワープ座標y, ワープ座標z):
    do指定座標にワープ(world(ワープ座標x, ワープ座標y, ワープ座標z))
player.on_chat("warp", on_on_chat8)

def on_on_chat9():
    doエージェントのアイテムリストを表示()
player.on_chat("item_list", on_on_chat9)

def get該当するアイテムのスロット番号(item_list: List[any]):
    for カウンター2 in range(29):
        for 値 in item_list:
            if agent.get_item_detail(カウンター2) == 値:
                return カウンター2
    return 999
def do通路を掘る(掘削回数2: number):
    global 松明カウント
    agent.set_assist(DESTROY_OBSTACLES, True)
    松明カウント = 0
    for index3 in range(掘削回数2):
        agent.collect_all()
        do足場作り()
        do水止め([LEFT, RIGHT, DOWN, UP, FORWARD, BACK])
        if agent.inspect(AgentInspection.BLOCK, BACK) == AIR:
            pass
        else:
            agent.destroy(BACK)
        agent.move(UP, 1)
        do水止め([LEFT, RIGHT, UP, FORWARD])
        if agent.inspect(AgentInspection.BLOCK, FORWARD) == AIR:
            pass
        else:
            agent.destroy(FORWARD)
        agent.move(FORWARD, 1)
        do水止め([LEFT, RIGHT, UP, DOWN, FORWARD])
        if agent.inspect(AgentInspection.BLOCK, DOWN) == AIR:
            pass
        else:
            agent.destroy(DOWN)
        agent.move(DOWN, 1)
        松明カウント += 1
        if 松明カウント >= 松明の間隔設定:
            agent.move(BACK, 松明の間隔設定 - 1)
            agent.set_slot(get該当するアイテムのスロット番号([TORCH]))
            agent.place(BACK)
            agent.move(FORWARD, 松明の間隔設定 - 1)
            松明カウント = 0
def do資源探索_後():
    if agent.inspect(AgentInspection.BLOCK, BACK) == AIR:
        pass
    else:
        for 資源ブロックnum5 in 資源ブロックコレクション:
            if agent.inspect(AgentInspection.BLOCK, BACK) == 資源ブロックnum5:
                player.say("" + str(agent.get_position()) + " : " + blocks.name_of_block(資源ブロックnum5))
                doアイテムスペース確保()
                agent.destroy(BACK)
                agent.collect_all()
                agent.move(BACK, 1)
                do資源探索()
                agent.move(FORWARD, 1)
def do足場作り():
    if agent.inspect(AgentInspection.BLOCK, DOWN) == AIR:
        汎用ブロックを有効()
        agent.place(DOWN)
# 方向が空いていれば1
# 空いていなければ0を返す
def getエージェントの指定した方向が空いているかどうか(空いているかどうか確認する方向: number):
    for 移動できるブロック in [WATER, 9, LAVA, 11, 750, AIR]:
        if agent.inspect(AgentInspection.BLOCK, 空いているかどうか確認する方向) == 移動できるブロック:
            return 1
    return 0

def on_on_chat10():
    agent.drop_all(UP)
player.on_chat("drop", on_on_chat10)

def 汎用ブロックを有効():
    agent.set_slot(get該当するアイテムのスロット番号(汎用ブロックコレクション))

def on_on_chat11():
    doエージェントの場所を表示()
player.on_chat("where", on_on_chat11)

def on_on_chat12():
    player.say(agent.inspect(AgentInspection.BLOCK, FORWARD))
player.on_chat("name", on_on_chat12)

def getプレイヤーの向いている方向():
    if -135 <= player.get_orientation() and player.get_orientation() < -45:
        return -90
    elif -45 <= player.get_orientation() and player.get_orientation() < 45:
        return 0
    elif 45 <= player.get_orientation() and player.get_orientation() < 135:
        return 90
    else:
        return -180
def doアイテムスペース確保():
    if 0 < agent.get_item_count(27):
        doアイテム納品()
def do資源探索_前():
    if agent.inspect(AgentInspection.BLOCK, FORWARD) == AIR:
        pass
    else:
        for 資源ブロックnum6 in 資源ブロックコレクション:
            if agent.inspect(AgentInspection.BLOCK, FORWARD) == 資源ブロックnum6:
                player.say("" + str(agent.get_position()) + " : " + blocks.name_of_block(資源ブロックnum6))
                doアイテムスペース確保()
                agent.destroy(FORWARD)
                agent.collect_all()
                agent.move(FORWARD, 1)
                do資源探索()
                agent.move(BACK, 1)
def do資源探索():
    do資源探索_後()
    do資源探索_右()
    do資源探索_上()
    do資源探索_左()
    do資源探索_下()
    do資源探索_前()

def on_on_chat13():
    player.say(":)")
player.on_chat("jump", on_on_chat13)

def do水止め(angle_list: List[number]):
    for 方向 in angle_list:
        for 値2 in 液体ブロックコレクション:
            if agent.inspect(AgentInspection.BLOCK, 方向) == 値2:
                汎用ブロックを有効()
                agent.place(方向)

def on_on_chat14():
    doアイテム納品()
player.on_chat("store", on_on_chat14)

def doマイニング(掘削回数3: number):
    global 掘削済み回数
    agent.set_assist(DESTROY_OBSTACLES, True)
    掘削済み回数 = 0
    for index4 in range(掘削回数3):
        if agent.inspect(AgentInspection.BLOCK, FORWARD) == AIR:
            pass
        else:
            agent.destroy(FORWARD)
        do資源探索()
        agent.move(FORWARD, 1)
        掘削済み回数 += 1
        player.say("mining" + " : " + ("" + str(ブランチマイニングのステップ数)) + "-" + ("" + str(掘削済み回数)))
    player.say("mining : finish")
    agent.move(BACK, 掘削回数3)
    player.say("returt : finish")
def do高速に高さ2の穴を掘り進める(掘削回数6: number):
    agent.set_assist(DESTROY_OBSTACLES, True)
    for index5 in range(掘削回数6):
        if agent.inspect(AgentInspection.BLOCK, FORWARD) == AIR:
            pass
        else:
            agent.destroy(FORWARD)
        if agent.inspect(AgentInspection.BLOCK, UP) == AIR:
            pass
        else:
            agent.destroy(UP)
        agent.collect_all()
        agent.move(FORWARD, 1)

def on_on_chat15():
    agent.teleport_to_player()
    doエージェントの向きを指定する(getプレイヤーの向いている方向())
player.on_chat("come", on_on_chat15)

掘削済み回数 = 0
松明カウント = 0
帰還座標: Position = None
帰還方角 = 0
ブランチマイニングのステップ数 = 0
資源ブロックコレクション: List[number] = []
液体ブロックコレクション: List[number] = []
汎用ブロックコレクション: List[number] = []
松明の間隔設定 = 0
アイテム保管座標: Position = None
アイテム保管座標 = world(-156, 72, 1262)
松明の間隔設定 = 27
汎用ブロックコレクション = [DIRT,
    STONE,
    GRANITE,
    DIORITE,
    ANDESITE,
    DIRT,
    COARSE_DIRT,
    COBBLESTONE,
    SANDSTONE,
    RED_SANDSTONE]
液体ブロックコレクション = [WATER, 9, LAVA, 11, 750]
資源ブロックコレクション = [IRON_ORE,
    COAL_ORE,
    LAPIS_ORE,
    GOLD_ORE,
    REDSTONE_ORE,
    DIAMOND_ORE,
    EMERALD_ORE]
