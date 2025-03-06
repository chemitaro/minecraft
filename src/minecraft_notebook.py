import fnmatch
import random
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

ignore_block_name_pattern = re.compile(
    r"^(?:air|deepslate|stone|netherrack|water|flowing_water|bubble_column|lava|flowing_lava|fire|dirt|diorite|baslate|tuff|granite|andesite|gravel|blackstone|cobblestone|cobbled_deepslate|grass_block|farmland|grass_path|podzol|mycelium|mud|oak_leaves|spruce_leaves|birch_leaves|jungle_leaves|acacia_leaves|dark_oak_leaves|mangrove_leaves|cherry_leaves|pale_oak_leaves|azalea_leaves|azalea_leaves_flowered|short_grass|tall_grass|seagrass|bedrock)$"
)
normal_block_name_pattern = re.compile(
    r"^(?:cobblestone|cobbled_deepslate|deepslate|stone|netherrack|dirt|baslate|tuff|granite|andesite|blackstone)$"
)
liquid_block_name_pattern = re.compile(r"^(?:water|flowing_water|lava|flowing_lava)$")
player_mention = "@yutaf "
azimuth_dict = {-90: "E", 0: "S", 90: "W", -180: "N"}
opposite_direction_dict = {
    "forward": "back",
    "back": "forward",
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left",
}


@dataclass
class WorldType:
    name: str
    collection_location: List[int]
    teleport_step_length: int
    max_y: int
    min_y: int


class WorldEnum(Enum):
    OVER_WORLD = WorldType(
        name="over_world", collection_location=[-136, 76, 1250], teleport_step_length=176, max_y=320, min_y=-60
    )
    NETHER = WorldType(name="nether", collection_location=[-11, 88, 160], teleport_step_length=22, max_y=122, min_y=5)
    THE_END = WorldType(name="the_end", collection_location=[0, 0, 0], teleport_step_length=25, max_y=122, min_y=5)


current_world_enum = WorldEnum.OVER_WORLD


def switch_world_type() -> WorldEnum:  # Worldの種類を変更する
    global current_world_enum
    enum_members = list(WorldEnum)
    current_index = enum_members.index(current_world_enum)
    next_index = (current_index + 1) % len(enum_members)
    current_world_enum = enum_members[next_index]
    agent.say(f"switched : {current_world_enum.value.name}")
    return current_world_enum


def show_chunk_range() -> None:
    """現在地点のチャンクの範囲を表示する"""
    agent.say(f"Current Chunk : {int(player.position.x // 16)}, {int(player.position.z // 16)}")
    agent.say(
        f"Chunk Range : {int(player.position.x // 16 * 16)} ~ {int(player.position.x // 16 * 16 + 16)}, {int(player.position.z // 16 * 16)} ~ {int(player.position.z // 16 * 16 + 16)}"
    )


def show_agent_item_list() -> None:
    """エージェントのアイテム一覧を表示"""
    for i in range(1, 28):
        item = agent.get_item(i)
        agent.say(f"{i} : {item.id} {item.stack_size}/{item.max_stack_size}")


def show_agent_location() -> None:
    """エージェントの場所と周囲の状況を表示する"""
    agent.say(f"World : {current_world_enum.value.name}")
    agent.say(f"Position : {agent.position}")
    agent.say(f"Rotation : {azimuth_dict[agent.rotation]}")
    for direction in ["forward", "back", "left", "right", "up", "down"]:
        agent.say(f"- {direction} : {agent.inspect(direction).id}")


def safe_teleport(position: List) -> None:
    """多段階で移動する安全なテレポート"""
    step_length, start_x, start_z = current_world_enum.value.teleport_step_length, agent.position.x, agent.position.z
    distance_x, distance_z = position[0] - start_x, position[2] - start_z
    move_sign_x, move_sign_z = 1 if distance_x > 0 else -1, 1 if distance_z > 0 else -1
    for step in range(1, abs(int(distance_x / step_length)) + 1):
        agent.teleport([start_x + step * step_length * move_sign_x, agent.position.y, agent.position.z])
        agent.say(f"teleport_x{step} - {agent.position}")
    for step in range(1, abs(int(distance_z / step_length)) + 1):
        agent.teleport([agent.position.x, agent.position.y, start_z + step * step_length * move_sign_z])
        agent.say(f"teleport_z{step} - {agent.position}")
    agent.teleport(position)
    agent.say(f"safe_teleport: finish - {agent.position}")


def agent_turn(direction: str, count: int = 1) -> None:
    for i in range(count):
        agent.turn(direction)


def agent_move(direction: str, count: int = 1, is_destroy: bool = False) -> None:
    for i in range(count):
        while is_destroy and agent.detect(direction):
            agent.destroy(direction)
        agent.move(direction)


def agent_item_delivery() -> None:
    """エージェントのアイテムを回収場所にドロップする"""
    before_position = agent.position
    safe_teleport(current_world_enum.value.collection_location)
    time.sleep(0.5)
    for slot in range(1, 28):
        direction = random.choice(["forward", "back", "left", "right"])
        agent.say(f"- drop : {agent.get_item(slot).id}")
        agent.drop(direction, 64, slot)
        time.sleep(0.3)
    safe_teleport([before_position.x, before_position.y, before_position.z])
    agent.say(f"return : {before_position}")


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


def agent_teleport_player() -> None:
    """エージェントがプレイヤーの前にテレポートする"""
    agent.teleport(["~0", "~0", "~0"])


def is_block_list_match_direction(direction: str, block_name_pattern: Union[str, re.Pattern]) -> bool:
    """指定された方向において、ブロックのリストが所定のパターンにマッチするかを判定し、結果をブール値（True/False）で返却します。"""
    if isinstance(block_name_pattern, str):
        return bool(fnmatch.fnmatch(agent.inspect(direction).id, block_name_pattern))
    elif isinstance(block_name_pattern, re.Pattern):
        return bool(block_name_pattern.match(agent.inspect(direction).id))
    else:
        raise ValueError("block_name_pattern must be a string or a re.Pattern")


def get_agent_storage_socket_index(items: List[Union[str, re.Pattern]]) -> int:
    """指定したアイテムがエージェントストレージのどのソケットに格納されているか確認し、ソケット番号を返却します。"""
    for item_name in items:
        for socket_index in range(1, 28):
            check_item = agent.get_item(socket_index)
            if (
                isinstance(item_name, str)
                and fnmatch.fnmatch(check_item.id, item_name)
                or isinstance(item_name, re.Pattern)
                and bool(item_name.match(check_item.id))
            ):
                return socket_index
    return -1


def agent_use_item(direction: str, item_names: List[Union[str, re.Pattern]]) -> bool:
    """エージェントが指定したアイテムを設置する"""
    socket_index = get_agent_storage_socket_index(item_names)
    if socket_index < 1:
        agent.say(f"{item_names}を持っていません")
        return False
    agent.place(direction, socket_index)
    return True


def agent_put_block(
    direction: str,
    block_names: List[Union[str, re.Pattern]] = [
        re.compile(r"^(?:cobblestone|cobbled_deepslate|)$"),
        re.compile(r"^(?:deepslate|stone|dirt|baslate|tuff|granite|andesite|blackstone)$"),
        re.compile(r"^(?:netherrack)$"),
    ],
) -> bool:
    if agent.detect(direction):
        return False
    return agent_use_item(direction, block_names)


def build_space(
    width: int,
    height: int,
    depth: int,
    *,
    f: bool = False,
    b: bool = False,
    l: bool = False,
    r: bool = False,
    u: bool = False,
    d: bool = False,
    safe: bool = False,
    block_names: List[Union[str, re.Pattern]] = [
        re.compile(r"^(?:cobblestone|cobbled_deepslate|)$"),
        re.compile(r"^(?:deepslate|stone|dirt|diorite|baslate|tuff|granite|andesite|blackstone)$"),
        re.compile(r"^(?:netherrack)$"),
    ],
) -> None:
    agent_move("up", height - 1, True)  # 開始ポジションに移動（左上）
    for dep in range(depth):
        for w in range(width):
            if u:
                agent_put_block("up")
            for h in range(height):
                if safe or (f and d == depth - 1):
                    agent_put_block("forward")
                if l and w == 0:
                    agent_put_block("left")
                if r and w == (width - 1):
                    agent_put_block("right")
                if b and d == 0:
                    agent_put_block("back")
                if h < height - 1:
                    agent_move("down", 1, True)
                    agent.collect()
            if d:
                agent_put_block("down")
            agent_move("up", height - 1, True)
            if w < width - 1:
                agent_move("right", 1, True)
                agent.collect()
        agent_move("left", width - 1, True)
        if dep < depth - 1:
            agent_move("forward", 1, True)
            agent.collect()
    agent_move("down", height - 1, True)


def build_ladder(direction: str, step: int = 9999, safe: bool = False) -> bool:
    for i in range(step):
        if (
            agent.inspect(direction).id == "bedrock"
            or agent.position.y >= current_world_enum.value.max_y
            or agent.position.y <= current_world_enum.value.min_y
        ):
            return False
        agent_move(direction=direction, is_destroy=True)
        agent.collect()
        agent_put_block(direction="forward")
        if safe:
            agent_put_block(direction="left")
            agent_put_block(direction="right")
            agent_put_block(direction="back")
            agent_put_block(direction=opposite_direction_dict[direction])
        agent_move(direction=opposite_direction_dict[direction], is_destroy=True)
        agent_use_item(direction="forward", item_names=["ladder"])
        agent_move(direction=direction)
    agent_use_item(direction="forward", item_names=["ladder"])
    return True


def generate_flint() -> None:
    """火打石を量産する"""
    running = True
    while running:
        if agent_use_item("forward", ["gravel"]) is False:
            running = False
        agent.destroy("forward")
        agent.collect()
    agent.say("generate_flint : finish")


def is_mining_position() -> bool:
    """指定された位置情報がマイニング対象のポジションであるかどうかを判定し、結果をブール値（True/False）で返却します。"""
    return (
        int(agent.position.y) % 8 == 0
        and int(agent.position.x) % 4 == 0
        or int(agent.position.y) % 4 == 0
        and (int(agent.position.x) + 2) % 4 == 0
    )


def explore_and_mine_resources(
    block_name_pattern: Union[str, re.Pattern],
    mehtod: bool = True,
    first_directions: List[str] = ["up", "left", "right", "back", "forward", "down"],
) -> None:
    """プレイヤーが探索しながら資源を検出し、自動で採掘する処理を実行する関数。"""
    for direction in first_directions:
        if is_block_list_match_direction(direction, block_name_pattern) == mehtod:
            agent.say(f" -find : {agent.inspect(direction).id} at {agent.position}")
            agent.destroy(direction)
            agent.collect()
            agent.move(direction)
            explore_and_mine_resources(block_name_pattern, mehtod)
            agent.move(opposite_direction_dict[direction])
            agent.say(f" -lose : {agent.position}")


# # 指定した方角のブロックを検出したら、そのブロックを破壊して、そのブロックを採掘する
def detect_and_destroy_block(direction: Optional[str] = None) -> None:
    if direction is None or agent.inspect(direction).id == "air":
        explore_and_mine_resources(ignore_block_name_pattern, False)
    else:
        explore_and_mine_resources(agent.inspect(direction).id)


def fall_down(explore: bool = False) -> None:
    in_air = not agent.detect("down")
    while in_air:
        agent.move("down")
        if explore:
            explore_and_mine_resources(ignore_block_name_pattern, False, ["left", "right", "forward", "back"])
        in_air = not agent.detect("down")


def climb_up(explore: bool = False) -> None:
    forward_block = agent.detect("forward")
    while forward_block:
        agent_move("up", 1, True)
        if explore:
            explore_and_mine_resources(ignore_block_name_pattern, False, ["left", "right", "forward", "back"])
        forward_block = agent.detect("forward")


def walk_along_the_terrain(step: int = 1, explore: bool = False) -> None:
    for i in range(step):
        fall_down(explore)
        climb_up(explore)
        agent.move("forward")
        if explore:
            explore_and_mine_resources(ignore_block_name_pattern, False, ["up", "left", "right", "down"])
            check_and_clear_agent_inventory()


def mining(depth: int, line_number: str = "none") -> None:
    """資源を収集しながら掘り進める"""
    start_position = [agent.position.x, agent.position.y, agent.position.z]
    for step in range(1, depth):
        agent.say(f"Mining : {line_number} - {step}/{depth}")
        if agent.detect("forward"):
            agent.destroy("forward")
            agent.collect()
            explore_and_mine_resources(ignore_block_name_pattern, False, ["up", "left", "right", "down"])
        agent.move("forward")
    agent.say("Return...")
    safe_teleport(start_position)
    agent.say("Mining : finish")


def branch_mining() -> bool:
    """ブランチマイニングを実行する"""
    length = 1000
    set_agent_azimuth(-90)  # 掘削方向の西側を向く
    show_agent_location()
    if not agent.position.y % 4 == 0:
        agent.say("高さが間違っています")
        return False
    for step in range(1, length):
        if agent.detect("forward"):
            agent.destroy("forward")
            agent.collect()
        agent.move("forward")
        agent.say(f"Branch_mining : {step}/{length} {agent.position}")
        if is_mining_position():
            if agent.detect("right"):
                agent.turn("right")
                mining(500, f"{step}R")
                agent_item_delivery()
                time.sleep(1)
                agent.turn("left")
            if agent.detect("left"):
                agent.turn("left")
                mining(500, f"{step}L")
                agent_item_delivery()
                time.sleep(1)
                agent.turn("right")
    return True


@on_event("PlayerMessage")
def process_chat_command(message: str, sender: str, receiver: str, message_type: str) -> None:
    # Play a sound when someone said something

    if sender == "yutaf" and message_type == "chat":
        chunked_messages = message.split()
        command = chunked_messages[0]
        if command == "trial":  # ここに実行する実験的な処理を記述する
            # build_space(2, 3, 50, l=True, r=True, u=True, d=True, f=True, safe=True)
            detect_and_destroy_block("forward")
            agent.say("trial finish")
        elif command == "switch":
            switch_world_type()
        elif command == "come":  # エージェントを呼び出す
            agent_teleport_player()
        elif command == "warp":
            safe_teleport([int(chunked_messages[1]), int(chunked_messages[2]), int(chunked_messages[3])])
        elif command == "branch_mining":
            branch_mining()
        elif command == "mining":
            mining(int(chunked_messages[1]), "manual")
        elif command == "turn":
            agent_turn(chunked_messages[1], 1)
        elif command == "move":
            agent_move(
                direction=chunked_messages[1],
                count=int(chunked_messages[2]),
                is_destroy=("destroy" in chunked_messages),
            )
        elif command == "fall":
            fall_down()
        elif command == "climb":
            climb_up()
        elif command == "walk":
            walk_along_the_terrain(step=int(chunked_messages[1]), explore=("exp" in chunked_messages))
        elif command == "detect":
            if len(chunked_messages) > 1:
                detect_and_destroy_block(chunked_messages[1])
            else:
                detect_and_destroy_block()
        elif command == "item_list":
            show_agent_item_list()
        elif command == "what_block":
            agent.say(agent.inspect("forward"))
        elif command == "what_item":
            agent.say(agent.get_item(1))
        elif command == "delivery":
            agent_item_delivery()
        elif command == "where":
            show_agent_location()
        elif command == "flint":
            generate_flint()
        elif command == "space":
            build_space(
                int(chunked_messages[1]),
                int(chunked_messages[2]),
                int(chunked_messages[3]),
                l=("l" in chunked_messages),
                r=("r" in chunked_messages),
                u=("u" in chunked_messages),
                d=("d" in chunked_messages),
                f=("f" in chunked_messages),
                safe=("safe" in chunked_messages),
            )
        elif command == "ladder":
            build_ladder(
                direction=chunked_messages[1], step=int(chunked_messages[2]), safe=("safe" in chunked_messages)
            )
        elif command == "chunk":
            show_chunk_range()


agent.say(player_mention + "run script")
