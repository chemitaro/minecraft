import fnmatch
from typing import List
import minecraft
import time

# アイテムの回収場所の座標座標
item_collection_location = [-156, 71, 1262]
# 有益な地下資源の名称
underground_resource_list = ["*_ore", "ancient_debris"]
# 液体ブロック
liquid_block_list = ["water", "lava"]
# 普通のブロックの名称
normal_block_list = ["cobblestone", "cobbled_deepslate", "granite", "andesite", "dirt", "tuff", "deepslate", "blackstone", "stone"]


def str_azimuth(azimuth: int) -> str:
    if azimuth == -90:
        return "E"
    elif azimuth == 0:
        return "S"
    elif azimuth == 90:
        return "W"
    elif azimuth == -180:
        return "N"
    else:
        return "unknown_azimuth"


def show_agent_item_list():
    """エージェントのアイテム一覧を表示"""
    for i in range(1, 28):
        item = agent.get_item(i)
        agent.say(f"{i} : {item.id} {item.stack_size}/{item.max_stack_size}")

def show_agemt_location():
    """エージェントの場所と周囲の状況を表示する"""
    agent.say(f"Position : {agent.position}")
    agent.say(f"Rotation : {str_azimuth(agent.rotation)}")
    for direction in ["forward", "back", "left", "right", "up", "down"]:
        agent.say(f"- {direction} : {agent.inspect(direction).id}")


def agent_item_delivery() -> None:
    """エージェントのアイテムを回収場所にドロップする"""
    befor_position = agent.position
    time.sleep(1)
    agent.teleport(item_collection_location)
    time.sleep(1)
    for slot in range(1, 28):
        agent.drop("up", 64, slot)
    time.sleep(1)
    agent.teleport(befor_position)


def check_and_clear_agent_inventory() -> None:
    if not agent.get_item(27).id == "air":
        agent_item_delivery()


def set_agent_azimuth(azimuth: int):
    """
    エージェントの向く方角を変える
    """
    for i in range(4):
        if agent.rotation == azimuth:
            break
        agent.turn("right")


def agent_turn_away_from_player() -> None:
    """
    エージェントがプレイヤーに背を向ける動作を実行します。
    """
    agent_position = agent.position
    player_positoon = player.position
    azimuth = None

    # x軸かz軸でどちらが近いか判断する
    if abs(abs(agent_position.x) - abs(player_positoon.x)) > abs(abs(agent_position.z) - abs(player_positoon.z)):
        # x軸の差が大きい場合
        if agent_position.x < player_positoon.x:
            # 西向き
            azimuth = 90
        else:
            # 東向き
            azimuth = -90
    else:
        # z軸の差が大きい場合
        if agent_position.z < player_positoon.z:
            # 北向き
            azimuth = -180
        else:
            # 南向き
            azimuth = 0
    
    set_agent_azimuth(azimuth)


def agent_teleport_player():
    """
    エージェントがプレイヤーの前にテレポートする
    """
    agent.teleport(["^0", "^0", "^1"])
    agent_turn_away_from_player()


def agent_teleport(x, y, z):
    """
    エージェントを指定した座標にテレポートさせる
    """
    agent.teleport([x, y, z])


def get_opposite_direction(direction: str) -> str:
    """
    指定された方向を反対方向に変換して返す関数。

    例:
      "up" → "down"
    """
    if direction == "forward":
        return "back"
    elif direction == "back":
        return "forward"
    elif direction == "up":
        return "down"
    elif direction == "down":
        return "up"
    elif direction == "left":
        return "right"
    elif direction == "right":
        return "left"
    else:
        agent.say(f"入力の方向が正しくありません: {direction}")
        return ""


def is_block_list_match_direction(direction: str, block_list: list) -> bool:
    """
    指定された方向において、ブロックのリストが所定のパターンにマッチするかを判定し、
    結果をブール値（True/False）で返却します。
    """
    # ここに判定ロジックを実装
    for block in block_list:
        target = agent.inspect(direction)
        if fnmatch.fnmatch(target.id, block):
            return True
    return False


def get_agent_storage_socket_index(items: List[str]) -> int:
    """
    指定したアイテムがエージェントストレージのどのソケットに格納されているか確認し、
    ソケット番号を返却します。
    """

    for item_name in items:
        for socket_index in range(1, 28):
            check_item = agent.get_item(socket_index)
            if fnmatch.fnmatch(check_item.id, item_name):
                return socket_index
    return -1
 

def agent_put_item(direction: str, item_names: List[str]) -> None:
    """
    エージェントが指定したアイテムを設置する
    """
    socket_index = get_agent_storage_socket_index(item_names)
    if socket_index < 1:
        agent.say(f"{item_names}を持っていません")
        return None
    agent.place(direction, socket_index)


def is_mining_position() -> bool:
    """
    指定された位置情報がマイニング対象のポジションであるかどうかを判定し、
    結果をブール値（True/False）で返却します。
    """
    position_x = agent.position.x
    position_y = agent.position.y

    if position_y % 8 == 0:
        if position_x % 4 == 0:
            return True

    elif position_y % 4 == 0:
        if  position_x % 2 == 0:
            return True

    return False


def explore_and_mine_resources(block_list: List[str]):
    """
    プレイヤーが探索しながら資源を検出し、自動で採掘する処理を実行する関数。
    """
    # 採掘処理の実装をここに記述
    directions = ["up", "left", "down", "right", "back", "forward"]
    for direction in directions:
        if is_block_list_match_direction(direction, block_list):
            agent.say(f"find: {agent.inspect(direction).id} at {agent.position}")
            agent.destroy(direction)
            agent.collect()
            agent.move(direction)

            explore_and_mine_resources(block_list)

            agent.move(get_opposite_direction(direction))
            
def mining(depth: int, line_number: int = 0) -> None:
    """
    資源を収集しながら掘り進める
    """
    for step in range(depth):
        agent.say(f"mining : {line_number} - {step}/{depth}")
        if agent.detect("forward"):
            agent.destroy("forward")
            agent.collect()

        explore_and_mine_resources(underground_resource_list)
        agent.move("forward")
    agent.say("return...")
    for step in range(depth):
        agent.move("back")
        agent.say(f"Return : {step}/{depth}")
    agent_item_delivery()
    agent.say("mining : finish")


def branch_mining() -> bool:
    """
    ブランチマイニングを実行する
    """
    length = 1000
    # 掘削方向の西側を向く
    set_agent_azimuth(-90)
    if not agent.position.y % 4 == 0:
        agent.say("高さが間違っています")
        return False

    for step in range(length):
        agent.say(f"branch_mining : {step}/{length} {agent.position}")
        if agent.detect("forward"):
            agent.destroy("forward")
            agent.collect()
        agent.move("forward")

        if is_mining_position() == True:
            if agent.detect("right") == True:
                agent.turn("right")
                mining(500, f"{step}R")
                agent.turn("left")
            
            if agent.detect("left") == True:
                agent.turn("left")
                mining(500, f"{step}L")
                agent.turn("right")


@on_event("PlayerMessage")
def process_chat_command(message, sender, receiver, message_type):
    # Play a sound when someone said something

    if sender == "yutaf" and message_type == "chat":
        # block = agent.inspect("forward")
        # agent.say(block.id)
        chunked_messages = message.split()
        command = chunked_messages[0]

        if command == "trial":
            # ここに実行する実験的な処理を記述する
            agent.say("troal fin")
        elif command == "come":
            # エージェントを自分の前に呼び出す
            agent_teleport_player()
        elif command == "warp":
            agent_teleport(chunked_messages[1], chunked_messages[2], chunked_messages[3])
            show_agemt_location()
        elif command == "branch_mining":
            branch_mining()
        elif command == "item_list":
            show_agent_item_list()
        elif command == "what_block":
            agent.say(agent.inspect("forward"))
        elif command == "what_item":
            agent.say(agent.get_item(1))
        elif command == "delivery":
            agent_item_delivery()
        elif command == "where":
            show_agemt_location()
