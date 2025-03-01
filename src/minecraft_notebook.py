import fnmatch
from typing import List
import minecraft
import time
import random
import re
from enum import Enum
from dataclasses import dataclass

ignore_block_name_pattern = re.compile(r'^(?:air|deepslate|stone|netherrack|water|flowing_water|lava|flowing_lava|fire|dirt|baslate|tuff|granite|andesite|gravel|blackstone|cobblestone|cobbled_deepslate|grass_block|farmland|grass_path|podzol|mycelium|mud|bedrock)$')
player_mention, azimuth_dict, opposite_direction_dict = "@yutaf ", {-90: "E", 0: "S", 90: "W", -180: "N"}, {"forward": "back", "back": "forward", "up": "down", "down": "up", "left": "right", "right": "left"}

@dataclass
class WorldType:
    name: str
    collection_location: List[int]
    teleport_step_length: int

class WorldEnum(Enum):
    OVER_WARLD = WorldType(name="over_warld", collection_location=[-156, 76, 1263], teleport_step_length= 500)
    NETHER = WorldType(name="nether", collection_location=[-11, 88, 160], teleport_step_length= 25)
    THE_END = WorldType(name="the_end", collection_location=[0, 0, 0], teleport_step_length= 25)

current_warld_enum = WorldEnum.OVER_WARLD

def switch_world_type() -> WorldEnum:  # Worldの種類を変更する
    global current_warld_enum
    enum_members = list(WorldEnum)
    current_index = enum_members.index(current_warld_enum)
    next_index = (current_index + 1) % len(enum_members)
    current_warld_enum = enum_members[next_index]
    agent.say(f"switched : {current_warld_enum.value.name}")
    return current_warld_enum

def show_agent_item_list():
    """エージェントのアイテム一覧を表示"""
    for i in range(1, 28):
        item = agent.get_item(i)
        agent.say(f"{i} : {item.id} {item.stack_size}/{item.max_stack_size}")

def show_agemt_location():
    """エージェントの場所と周囲の状況を表示する"""
    agent.say(f"World : {current_warld_enum.value.name}")
    agent.say(f"Position : {agent.position}")
    agent.say(f"Rotation : {azimuth_dict[agent.rotation]}")
    for direction in ["forward", "back", "left", "right", "up", "down"]:
        agent.say(f"- {direction} : {agent.inspect(direction).id}")

def safe_teleport(position: List):
    """多段階で移動する安全なテレポート"""
    step_length, start_x, start_z = current_warld_enum.value.teleport_step_length, agent.position.x, agent.position.z
    distance_x, distance_z = position[0] - start_x, position[2] - start_z
    move_sign_x, move_sign_z = 1 if distance_x > 0 else -1, 1 if distance_z > 0 else -1
    for step in range(1, abs(int(distance_x/step_length))+1):
        agent.teleport([start_x + step*step_length*move_sign_x, agent.position.y, agent.position.z])
        agent.say(f"teleport_x{step} - {agent.position}")
    for step in range(1, abs(int(distance_z/step_length))+1):
        agent.teleport([agent.position.x, agent.position.y, start_z + step*step_length*move_sign_z])
        agent.say(f"teleport_z{step} - {agent.position}")
    agent.teleport(position)
    agent.say(f"safe_teleport: finish - {agent.position}")

def agent_turn(direction: str, count: int = 1):
    for i in range(count):
        agent.turn(direction)

def agent_move(direction: str, count: int = 1):
    for i in range(count):
        agent.move(direction)

def agent_item_delivery() -> None:
    """エージェントのアイテムを回収場所にドロップする"""
    befor_position = agent.position
    safe_teleport(current_warld_enum.value.collection_location)
    time.sleep(0.5)
    for slot in range(1, 28):
        direction = random.choice(["forward", "back", "left", "right"])
        agent.say(f"- drop : {agent.get_item(slot).id}")
        agent.drop(direction, 64, slot)
        time.sleep(0.3)
    safe_teleport([befor_position.x, befor_position.y, befor_position.z])
    agent.say(f"return : {befor_position}")

def check_and_clear_agent_inventory() -> None:
    if not agent.get_item(27).id == "air":
        agent_item_delivery()

def set_agent_azimuth(azimuth: int) -> bool:
    """エージェントの向く方角を変える"""
    for i in range(4):
        if agent.rotation == azimuth:
            return True
        agent.turn("right")
    return False

def agent_turn_away_from_player() -> None:
    """エージェントがプレイヤーに背を向ける動作を実行します。"""
    agent_pos, player_pos = agent.position, player.position
    azimuth = 90 if abs(agent_pos.x - player_pos.x) > abs(agent_pos.z - player_pos.z) else (-180 if agent_pos.z < player_pos.z else 0)
    azimuth *= -1 if agent_pos.x > player_pos.x else 1
    set_agent_azimuth(azimuth)

def agent_teleport_player():
    """エージェントがプレイヤーの前にテレポートする"""
    agent.teleport(["^0", "^0", "^1"])
    agent_turn_away_from_player()

def agent_teleport(x, y, z):
    """エージェントを指定した座標にテレポートさせる"""
    safe_teleport([x, y, z])

def is_block_list_match_direction(direction: str, block_name_pattern: re.Pattern) -> bool:
    """指定された方向において、ブロックのリストが所定のパターンにマッチするかを判定し、結果をブール値（True/False）で返却します。"""
    return bool(block_name_pattern.match(agent.inspect(direction).id))

def get_agent_storage_socket_index(items: List[str]) -> int:
    """指定したアイテムがエージェントストレージのどのソケットに格納されているか確認し、ソケット番号を返却します。"""
    for item_name in items:
        for socket_index in range(1, 28):
            check_item = agent.get_item(socket_index)
            if fnmatch.fnmatch(check_item.id, item_name):
                return socket_index
    return -1

def agent_put_item(direction: str, item_names: List[str]) -> bool:
    """エージェントが指定したアイテムを設置する"""
    socket_index = get_agent_storage_socket_index(item_names)
    if socket_index < 1:
        agent.say(f"{item_names}を持っていません")
        return False
    agent.place(direction, socket_index)
    return True

def generate_flint():
    """火打石を量産する"""
    running = True
    while running:
        if agent_put_item("forward", ["gravel"]) is False:
            running = False
        agent.destroy("forward")
        agent.collect()
    agent.say("generate_flint : finish")

def is_mining_position() -> bool:
    """指定された位置情報がマイニング対象のポジションであるかどうかを判定し、結果をブール値（True/False）で返却します。"""
    return int(agent.position.y) % 8 == 0 and int(agent.position.x) % 4 == 0 or int(agent.position.y) % 4 == 0 and (int(agent.position.x) + 2) % 4 == 0

def explore_and_mine_resources(block_name_pattern: re.Pattern, mehtod: bool = True):
    """プレイヤーが探索しながら資源を検出し、自動で採掘する処理を実行する関数。"""
    directions = ["up", "left", "right", "back", "forward", "down"]
    for direction in directions:
        if is_block_list_match_direction(direction, block_name_pattern) == mehtod:
            agent.say(f" -find : {agent.inspect(direction).id} at {agent.position}")
            agent.destroy(direction)
            agent.collect()
            agent.move(direction)
            explore_and_mine_resources(block_name_pattern, mehtod)
            agent.move(opposite_direction_dict[direction])
            agent.say(f" -lose : {agent.position}")
            
def mining(depth: int, line_number: str = "none") -> None:
    """資源を収集しながら掘り進める"""
    start_position = agent.position
    for step in range(1, depth):
        agent.say(f"Mining : {line_number} - {step}/{depth}")
        if agent.detect("forward"):
            agent.destroy("forward")
            explore_and_mine_resources(ignore_block_name_pattern, False)
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
        agent.say(is_mining_position())
        if is_mining_position() == True:
            if agent.detect("right") == True:
                agent.turn("right")
                mining(500, f"{step}R")
                agent_item_delivery()
                time.sleep(1)
                agent.turn("left")
            if agent.detect("left") == True:
                agent.turn("left")
                mining(500, f"{step}L")
                agent_item_delivery()
                time.sleep(1)
                agent.turn("right")

@on_event("PlayerMessage")
def process_chat_command(message, sender, receiver, message_type):
    # Play a sound when someone said something

    if sender == "yutaf" and message_type == "chat":
        chunked_messages = message.split()
        command = chunked_messages[0]

        if command == "trial":  # ここに実行する実験的な処理を記述する
            switch_world_type()
            agent.say("troal fin")
        elif command == "switch":
            switch_world_type()
        elif command == "come":  # エージェントを呼び出す
            agent_teleport_player()
        elif command == "warp":
            agent_teleport(int(chunked_messages[1]), int(chunked_messages[2]), int(chunked_messages[3]))
        elif command == "branch_mining":
            branch_mining()
        elif command == "mining":
            mining(int(chunked_messages[1]), "manual")
        elif command == "turn":
            agent_turn(chunked_messages[1], 1)
        elif command == "move":
            agent_move(chunked_messages[1], int(chunked_messages[2]))
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
        elif command == "flint":
            generate_flint()

agent.say(player_mention + "run script")