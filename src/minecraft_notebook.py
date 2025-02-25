import fnmatch
from typing import List
import minecraft
import time
import random
import re

# アイテムの回収場所の座標座標
item_collection_location = [-156, 73, 1262]
nether_item_collection_location = [-11, 88, 160]
ignore_block_name_pattern = re.compile(r'^(?:air|deepslate|stone|netherrack|kwater|lava|flowing_lava|dirt|baslate|tuff|granite|andesite|blackstone|cobblestone|cobbled_deepslate|grass_block|farmland|grass_path|podzol|mycelium|mud|bedrock)$')

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
    for collection_position in [item_collection_location, nether_item_collection_location, player.position]:
        agent.teleport(collection_position)
        time.sleep(0.5)
        if agent.inspect("down").id == "hopper":
            agent.say(f"teleport : {collection_position}")
            break
    time.sleep(1)
    for slot in range(1, 28):
        direction = random.choice(["forward", "back", "left", "right"])
        agent.say(f"- drop : {agent.get_item(slot).id}")
        agent.drop(direction, 64, slot)
        time.sleep(0.3)
    time.sleep(1)
    agent.teleport(befor_position)
    agent.say(f"return : {befor_position}")

def check_and_clear_agent_inventory() -> None:
    if not agent.get_item(27).id == "air":
        agent_item_delivery()


def set_agent_azimuth(azimuth: int):
    """エージェントの向く方角を変える"""
    for i in range(4):
        if agent.rotation == azimuth:
            break
        agent.turn("right")

def agent_turn_away_from_player() -> None:
    """エージェントがプレイヤーに背を向ける動作を実行します。"""
    agent_position = agent.position
    player_positoon = player.position
    azimuth = None
    if abs(abs(agent_position.x) - abs(player_positoon.x)) > abs(abs(agent_position.z) - abs(player_positoon.z)):
        if agent_position.x < player_positoon.x:
            azimuth = 90
        else:
            azimuth = -90
    else:
        if agent_position.z < player_positoon.z:
            azimuth = -180
        else:
            azimuth = 0
    
    set_agent_azimuth(azimuth)

def agent_teleport_player():
    """エージェントがプレイヤーの前にテレポートする"""
    agent.teleport(["^0", "^0", "^1"])
    agent_turn_away_from_player()

def agent_teleport(x, y, z):
    """エージェントを指定した座標にテレポートさせる"""
    agent.teleport([x, y, z])

def get_opposite_direction(direction: str) -> str:
    """指定された方向を反対方向に変換して返す関数。例:  "up" → "down" """
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

def is_block_list_match_direction(direction: str, block_name_pattern: re.Pattern) -> bool:
    """指定された方向において、ブロックのリストが所定のパターンにマッチするかを判定し、結果をブール値（True/False）で返却します。"""
    if block_name_pattern.match(agent.inspect(direction).id) is not None:
        return True
    else:
        return False

def get_agent_storage_socket_index(items: List[str]) -> int:
    """指定したアイテムがエージェントストレージのどのソケットに格納されているか確認し、ソケット番号を返却します。"""
    for item_name in items:
        for socket_index in range(1, 28):
            check_item = agent.get_item(socket_index)
            if fnmatch.fnmatch(check_item.id, item_name):
                return socket_index
    return -1

def agent_put_item(direction: str, item_names: List[str]) -> None:
    """エージェントが指定したアイテムを設置する"""
    socket_index = get_agent_storage_socket_index(item_names)
    if socket_index < 1:
        agent.say(f"{item_names}を持っていません")
        return None
    agent.place(direction, socket_index)

def is_mining_position() -> bool:
    """指定された位置情報がマイニング対象のポジションであるかどうかを判定し、結果をブール値（True/False）で返却します。"""
    position_x = int(agent.position.x)
    position_y = int(agent.position.y)

    if position_y % 8 == 0:
        if position_x % 4 == 0:
            return True
    elif position_y % 4 == 0:
        if (position_x + 2) % 4 == 0:
            return True
    return False

def explore_and_mine_resources(block_name_pattern: re.Pattern, mehtod: bool = True):
    """プレイヤーが探索しながら資源を検出し、自動で採掘する処理を実行する関数。"""
    directions = ["back", "up", "down", "left", "right", "forward"]
    for direction in directions:
        if is_block_list_match_direction(direction, block_name_pattern) == mehtod:
            agent.say(f" -Find : {agent.inspect(direction).id} at {agent.position}")
            agent.destroy(direction)
            agent.collect()
            agent.move(direction)

            explore_and_mine_resources(block_name_pattern, mehtod)

            agent.move(get_opposite_direction(direction))
            
def mining(depth: int, line_number: str = "none") -> None:
    """資源を収集しながら掘り進める"""
    start_position = agent.position
    for step in range(1, depth):
        agent.say(f"Mining : {line_number} - {step}/{depth}")
        explore_and_mine_resources(ignore_block_name_pattern, False)
        if agent.detect("forward"):
            agent.destroy("forward")
        agent.move("forward")
    agent.say("Return...")
    agent.teleport(start_position)
    agent.say("Mining : finish")

def branch_mining() -> bool:
    """ブランチマイニングを実行する"""
    length = 1000
    set_agent_azimuth(-90)  # 掘削方向の西側を向く
    if not agent.position.y % 4 == 0:
        agent.say("高さが間違っています")
        return False
    for step in range(1, length):
        if agent.detect("forward"):
            agent.destroy("forward")
        agent.move("forward")
        agent.say(f"Branch_mining : {step}/{length} {agent.position}")
        if is_mining_position() == True:
            if agent.detect("right") == True:
                agent.turn("right")
                mining(500, f"{step}R")
                agent_item_delivery()
                set_agent_azimuth(-90)
            if agent.detect("left") == True:
                agent.turn("left")
                mining(500, f"{step}L")
                agent_item_delivery()
                set_agent_azimuth(-90)

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
        elif command == "mining":
            mining(int(chunked_messages[1]), "manual")
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
