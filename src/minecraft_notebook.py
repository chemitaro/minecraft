import fnmatch
import random
import re
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

ignore_block_name_pattern = re.compile(
    r"^(?:air|deepslate|stone|netherrack|water|flowing_water|bubble_column|lava|flowing_lava|fire|dirt|diorite|baslate|tuff|granite|andesite|gravel|blackstone|grass_block|farmland|grass_path|podzol|mycelium|mud|clay|short_grass|tall_grass|seagrass|oak_leaves|spruce_leaves|birch_leaves|jungle_leaves|acacia_leaves|dark_oak_leaves|mangrove_leaves|cherry_leaves|pale_oak_leaves|azalea_leaves|azalea_leaves_flowered|bedrock)$"
)
normal_block_name_pattern = re.compile(
    r"^(?:cobblestone|cobbled_deepslate|deepslate|stone|netherrack|dirt|baslate|tuff|granite|andesite|blackstone)$"
)
liquid_block_name_pattern = re.compile(r"^(?:water|flowing_water|bubble_column|lava|flowing_lava)$")
leave_block_name_pattern = re.compile(
    r"^(?:oak_leaves|spruce_leaves|birch_leaves|jungle_leaves|acacia_leaves|dark_oak_leaves|mangrove_leaves|cherry_leaves|pale_oak_leaves|azalea_leaves|azalea_leaves_flowered)$"
)
notify_block_name_pattern = re.compile(
    r"^(?:end_portal_frame|vault|trial_spawner|mob_spawner|suspicious_sand|suspicious_gravel|sculk|sculk_vein|sculk_sensor|sculk_catalyst|sculk_shrieker|oak_planks|spruce_planks|birch_planks|jungle_planks|acacia_planks|dark_oak_planks|mangrove_planks|cherry_planks|pale_oak_planks|bamboo_planks|crimson_planks|warped_planks|oak_fence|spruce_fence|birch_fence|jungle_fence|acacia_fence|dark_oak_fence|mangrove_fence|cherry_fence|pale_oak_fence|bamboo_fence|crimson_fence|warped_fence|chiseled_stone_bricks|stone_bricks|mossy_stone_bricks|infested_stone|infested_cobblestone|infested_stone_bricks|infested_mossy_stone_bricks|infested_cracked_stone_bricks|infested_chiseled_stone_bricks|infested_deepslate|lodestone|polished_deepslate|deepslate_bricks|deepslate_tiles|chiseled_deepslate|cracked_deepslate_bricks|cracked_deepslate_tiles|cobbled_deepslate_double_slab|cobbled_deepslate_slab|cobbled_deepslate_stairs|polished_deepslate_double_slab|polished_deepslate_slab|polished_deepslate_stairs|deepslate_brick_double_slab|deepslate_brick_slab|deepslate_brick_stairs|deepslate_tile_double_slab|deepslate_tile_slab|deepslate_tile_stairs|reinforced_deepslate|stone_bricks|tuff_bricks|chiseled_tuff|chiseled_tuff_bricks|chiseled_sandstone|chiseled_sandstone|nether_brick|polished_blackstone_bricks|cracked_polished_blackstone_bricks|chiseled_polished_blackstone|gold_block|quartz_block|gilded_blackstone|polished_blackstone|purpur_block|purpur_pillar|end_bricks|copper_block|exposed_copper|weathered_copper|oxidized_copper|waxed_copper|waxed_exposed_copper|waxed_weathered_copper|waxed_oxidized_copper|cut_copper|exposed_cut_copper|weathered_cut_copper|oxidized_cut_copper|waxed_cut_copper|waxed_exposed_cut_copper|waxed_weathered_cut_copper|waxed_oxidized_cut_copper|copper_grate|exposed_copper_grate|weathered_copper_grate|oxidized_copper_grate|waxed_copper_grate|waxed_exposed_copper_grate|waxed_weathered_copper_grate|waxed_oxidized_copper_grate|prismarine)$"
)
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
orthogonal_directions_dict = {
    "forward": ["left", "right", "up", "down"],
    "back": ["left", "right", "up", "down"],
    "left": ["forward", "back", "up", "down"],
    "right": ["forward", "back", "up", "down"],
    "up": ["forward", "back", "left", "right"],
    "down": ["forward", "back", "left", "right"],
}


# 発見したnotify_blockの名前と座標
@dataclass
class NotifyBlock:
    name: str
    position: List[int]

    def __str__(self) -> str:
        return f"{self.name} : {self.position}"


notify_block_list: List[NotifyBlock] = []


@dataclass
class WorldType:
    name: str
    collection_location: List[int]
    teleport_step_length: int
    max_y: int
    min_y: int


class WorldEnum(Enum):
    OVER_WORLD = WorldType(
        name="over_world", collection_location=[-135, 73, 1243], teleport_step_length=176, max_y=320, min_y=-60
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


def convert_absolute_to_relative_coordinates(absolute_coordinates: List[int]) -> List[int]:
    """絶対座標を相対座標に変換する"""
    return [
        absolute_coordinates[0] - int(agent.position.x),
        absolute_coordinates[1] - int(agent.position.y),
        absolute_coordinates[2] - int(agent.position.z),
    ]


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
    step_length = current_world_enum.value.teleport_step_length
    goal_x = position[0]
    goal_y = position[1]
    goal_z = position[2]
    current_x = agent.position.x
    current_y = agent.position.y
    current_z = agent.position.z
    current_distance_x = goal_x - current_x
    current_distance_y = goal_y - current_y
    current_distance_z = goal_z - current_z
    move_sign_x = 1 if current_distance_x > 0 else -1
    move_sign_y = 1 if current_distance_y > 0 else -1
    move_sign_z = 1 if current_distance_z > 0 else -1

    while (
        abs(current_distance_x) > step_length
        or abs(current_distance_y) > step_length
        or abs(current_distance_z) > step_length
    ):
        if abs(current_distance_x) > step_length:
            next_x = current_x + step_length * move_sign_x
        else:
            next_x = current_x

        if abs(current_distance_y) > step_length:
            next_y = current_y + step_length * move_sign_y
        else:
            next_y = current_y

        if abs(current_distance_z) > step_length:
            next_z = current_z + step_length * move_sign_z
        else:
            next_z = current_z
        agent.say(f"teleport_to: {next_x}, {next_y}, {next_z}")
        agent.teleport([next_x, next_y, next_z])
        time.sleep(5)

        current_x = next_x
        current_y = next_y
        current_z = next_z
        current_distance_x = goal_x - current_x
        current_distance_y = goal_y - current_y
        current_distance_z = goal_z - current_z
    agent.teleport(position)
    agent.say(f"teleport: finish {agent.position}")


def agent_turn(direction: str, count: int = 1) -> None:
    for i in range(count):
        agent.turn(direction)


def agent_move(direction: str, count: int = 1, is_destroy: bool = False, is_collect: bool = False) -> None:
    for i in range(count):
        retry_count = 3
        while is_destroy and agent.detect(direction):
            agent.destroy(direction)
            retry_count -= 1
            if retry_count < 0:
                agent.say(f"destroy : {agent.inspect(direction).id} failed")
                show_agent_location()
                # 周囲のブロックを破壊する
                six_directions = ["forward", "back", "left", "right", "up", "down"]
                # 進行方向ではない方角のリストを作成
                for other_direction in orthogonal_directions_dict[direction]:
                    agent.destroy(other_direction)
                    agent_move(other_direction, count=1, is_destroy=True, is_collect=is_collect)
                    for destroy_direction in six_directions:
                        agent.say(f"destroy : {agent.inspect(destroy_direction).id}")
                        agent.destroy(destroy_direction)
                    agent_move(
                        opposite_direction_dict[other_direction], count=1, is_destroy=True, is_collect=is_collect
                    )
                # ループの最初に戻る
                continue
        if is_collect:
            agent.collect()
        agent.move(direction)


def agent_item_delivery() -> None:
    """エージェントのアイテムを回収場所にドロップする"""
    before_position = agent.position
    agent.teleport(current_world_enum.value.collection_location)
    time.sleep(0.5)
    for slot in range(1, 28):
        direction = random.choice(["forward", "back", "left", "right"])
        item = agent.get_item(slot)
        agent.say(f"- drop {slot}/{27} : {item.id} {item.stack_size}")
        agent.drop(direction, 64, slot)
        time.sleep(0.3)
    agent.teleport([before_position.x, before_position.y, before_position.z])
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


def is_block_list_match_direction(
    direction: str, block_name_pattern: Union[str, re.Pattern], data: Optional[int] = None
) -> bool:
    """指定された方向において、ブロックのリストが所定のパターンにマッチするかを判定し、結果をブール値（True/False）で返却します。
    また、dataパラメータが指定されている場合は、ブロックのdata値も一致するかを判定します。"""
    block = agent.inspect(direction)

    # ブロック名のパターンマッチングを確認
    pattern_match = False
    if isinstance(block_name_pattern, str):
        pattern_match = bool(fnmatch.fnmatch(block.id, block_name_pattern))
    elif isinstance(block_name_pattern, re.Pattern):
        pattern_match = bool(block_name_pattern.match(block.id))
    else:
        raise ValueError("block_name_pattern must be a string or a re.Pattern")

    # パターンがマッチしなければFalseを返す
    if not pattern_match:
        return False

    # dataパラメータが指定されている場合は、data値も一致するか確認
    if data is not None and block.data != data:
        return False

    # すべての条件を満たした場合はTrueを返す
    return True


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


def block_liquid(
    directions: List[str] = ["forward", "up", "left", "right", "down", "back"],
    block_name_pattern: Union[str, re.Pattern] = liquid_block_name_pattern,
    ignore_flow: bool = False,
) -> bool:
    is_block_liquid = False
    for direction in directions:
        if ignore_flow and is_block_list_match_direction(
            direction=direction, block_name_pattern=liquid_block_name_pattern, data=0
        ):
            agent_put_block(direction)
            is_block_liquid = True
        elif is_block_list_match_direction(direction=direction, block_name_pattern=block_name_pattern):
            agent_put_block(direction)
            is_block_liquid = True
    return is_block_liquid


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
    water: bool = False,
    block_names: List[Union[str, re.Pattern]] = [
        re.compile(r"^(?:cobblestone|cobbled_deepslate|)$"),
        re.compile(r"^(?:deepslate|stone|dirt|diorite|baslate|tuff|granite|andesite|blackstone)$"),
        re.compile(r"^(?:netherrack)$"),
    ],
) -> None:
    agent_move("up", height - 1, True, True)  # 開始ポジションに移動（左上）
    total_count = width * height * depth
    success_count = 0
    for dep in range(depth):
        for w in range(width):
            if u:
                agent_put_block("up")
            for h in range(height):
                success_count += 1
                agent.say(
                    f"success: {format(success_count/total_count*100, '.2f')}%, w: {w}/{width}, h: {h}/{height}, d: {dep}/{depth}"
                )
                if safe or (f and d == depth - 1):
                    agent_put_block("forward")
                if l and w == 0:
                    agent_put_block("left")
                if r and w == (width - 1):
                    agent_put_block("right")
                if b and d == 0:
                    agent_put_block("back")
                if h < height - 1:
                    agent_move("down", 1, True, True)
                    if water:
                        block_liquid(directions=["up", "left", "right", "down"])
                        block_liquid(
                            directions=["forward", "back"],
                            block_name_pattern=re.compile(r"^(?:water|lava)$"),
                            ignore_flow=True,
                        )
            if d:
                agent_put_block("down")

            if water:
                for i in range(height - 1):
                    if agent.detect("back"):
                        agent.destroy("back")
                        agent.collect()
                    agent_move(direction="up", count=1, is_destroy=True, is_collect=True)
                if agent.detect("back"):
                    agent.destroy("back")
                    agent.collect()
            else:
                agent_move("up", height - 1, True, True)

            if w < width - 1:
                agent_move("right", 1, True, True)
                if water:
                    block_liquid(directions=["up", "left", "right", "down"])
                    block_liquid(
                        directions=["forward", "back"],
                        block_name_pattern=re.compile(r"^(?:water|lava)$"),
                        ignore_flow=True,
                    )
        agent_move("left", width - 1, True, True)
        if dep < depth - 1:
            agent_move("forward", 1, True, True)
            if water:
                block_liquid(directions=["up", "left", "right", "down"])
                block_liquid(
                    directions=["forward", "back"], block_name_pattern=re.compile(r"^(?:water|lava)$"), ignore_flow=True
                )
    agent_move("down", height - 1, True, True)


# 高速に通路を掘る
def fast_dig(count: int = 1) -> None:
    for i in range(count):
        if agent.detect("forward"):
            agent.destroy("forward")
        if agent.detect("up"):
            agent.destroy("up")
        agent.collect()
        if is_block_list_match_direction("forward", liquid_block_name_pattern) or is_block_list_match_direction(
            "up", liquid_block_name_pattern
        ):
            build_space(width=1, height=2, depth=10, d=True, water=True)
        if agent.detect("down") is False:
            agent_put_block("down")
        else:
            agent.move("forward")


# def build_hole(width: int, height: int, depth: int, *, safe: bool = False) -> None:


def build_ladder(direction: str, step: int = 9999, safe: bool = False) -> bool:
    for i in range(step):
        agent.say(f"build_ladder : {i}/{step} {agent.position}")
        if (
            agent.inspect(direction).id == "bedrock"
            or agent.position.y >= current_world_enum.value.max_y
            or agent.position.y <= current_world_enum.value.min_y
        ):
            return False
        agent_move(direction=direction, is_destroy=True, is_collect=True)
        agent_put_block(direction="forward")
        if safe:
            agent_put_block(direction="left")
            agent_put_block(direction="right")
            agent_put_block(direction="back")
            agent_put_block(direction=direction)
        agent_move(direction=opposite_direction_dict[direction], is_destroy=True, is_collect=True)
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
    # 高さが８の倍数の場合
    if int(agent.position.y) % 8 == 0:
        if int(agent.position.x) % 4 == 0:
            return True
    # 高さが４の倍数の場合
    elif int(agent.position.y) % 4 == 0:
        if (int(agent.position.x) + 2) % 4 == 0:
            return True
    return False


def explore_and_mine_resources(
    block_name_pattern: Union[str, re.Pattern],
    mehtod: bool = True,
    first_directions: List[str] = ["up", "left", "back", "right", "forward", "down"],
    count: int = 0,
    notify: bool = False,
) -> bool:
    """プレイヤーが探索しながら資源を検出し、自動で採掘する処理を実行する関数。"""
    result: bool
    global notify_block_list
    for direction in first_directions:
        if is_block_list_match_direction(direction, block_name_pattern) == mehtod:
            agent.say(f" {count} find : {agent.inspect(direction).id} {agent.position}")
            if notify and is_block_list_match_direction(direction, notify_block_name_pattern):
                agent.say(f"notify : {agent.inspect(direction).id} {agent.position}")
                notify_block_list.append(NotifyBlock(agent.inspect(direction).id, agent.position))
                return False
            agent.destroy(direction)
            agent.collect()
            agent_move(direction, 1, True, True)
            if count < 700:
                result = explore_and_mine_resources(block_name_pattern, mehtod, count=count + 1, notify=notify)
                if result is False:
                    return False
            else:
                agent.say(f" {count} : limit over")
            agent_move(opposite_direction_dict[direction], 1, True, True)
            agent.say(f" {count} lose : {agent.position}")
        else:
            result = True
    return result


# # 指定した方角のブロックを検出したら、そのブロックを破壊して、そのブロックを採掘する
def detect_and_destroy_block(direction: Optional[str] = None) -> None:
    if direction is None or agent.inspect(direction).id == "air":
        explore_and_mine_resources(block_name_pattern=ignore_block_name_pattern, mehtod=False)
    else:
        explore_and_mine_resources(block_name_pattern=agent.inspect(direction).id)


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
            explore_and_mine_resources(
                block_name_pattern=ignore_block_name_pattern,
                mehtod=False,
                first_directions=["up", "left", "right", "down"],
            )
            check_and_clear_agent_inventory()


def mining(depth: int, line_number: str = "none") -> bool:
    """資源を収集しながら掘り進める"""
    start_position = [agent.position.x, agent.position.y, agent.position.z]
    explore_result = True
    for step in range(1, depth):
        agent.say(f"Mining : {line_number} - {step}/{depth}")
        for notify_block in notify_block_list:
            agent.say(f"notify_block : {str(notify_block)}")
        agent_move("forward", count=1, is_destroy=True, is_collect=True)
        explore_result = explore_and_mine_resources(
            block_name_pattern=ignore_block_name_pattern,
            mehtod=False,
            first_directions=["up", "left", "right", "down"],
            notify=True,
        )
        if explore_result is False:
            break
    agent.say("Return...")
    agent.teleport(start_position)
    agent.say("Mining : finish")
    for notify_block in notify_block_list:
        agent.say(f"notify_block : {str(notify_block)}")
    return explore_result


def branch_mining() -> bool:
    """ブランチマイニングを実行する"""
    length = 1598
    set_agent_azimuth(-90)  # 掘削方向の西側を向く
    show_agent_location()
    if not agent.position.y % 4 == 0:
        agent.say("高さが間違っています")
        return False
    for step in range(1, length):
        agent_move("forward", 1, True, True)
        if agent.detect("forward"):
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
        else:
            # 採掘済み
            agent.say(f"Already mined : {step}/{length}")
    return True


@on_event("PlayerMessage")
def process_chat_command(message: str, sender: str, receiver: str, message_type: str) -> None:
    # Play a sound when someone said something

    if sender == "yutaf" and message_type == "chat":
        chunked_messages = message.split()
        command = chunked_messages[0]
        if command == "trial":  # ここに実行する実験的な処理を記述する
            # build_space(2, 3, 50, l=True, r=True, u=True, d=True, f=True, safe=True)
            agent.say(
                is_block_list_match_direction(direction="forward", block_name_pattern=liquid_block_name_pattern, data=0)
            )
            agent.say("trial finish")
        elif command == "switch":
            switch_world_type()
        elif command == "come":  # エージェントを呼び出す
            agent_teleport_player()
        elif command == "warp":
            safe_teleport([int(chunked_messages[1]), int(chunked_messages[2]), int(chunked_messages[3])])
        elif command == "branch_mining":
            try:
                agent.teleport([int(chunked_messages[1]), int(chunked_messages[2]), int(chunked_messages[3])])
                running = True
                while running:
                    running = branch_mining()
            except Exception as e:
                agent.say(f"error : {e}")

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
        elif command == "collect":
            agent.collect()
        elif command == "use":
            agent.place(chunked_messages[1], chunked_messages[2])
        elif command == "attack":
            agent.attack("forward")
        elif command == "destroy":
            agent.destroy("forward")
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
                water=("water" in chunked_messages),
            )
        elif command == "fast_dig":
            fast_dig(int(chunked_messages[1]))
        elif command == "ladder":
            build_ladder(
                direction=chunked_messages[1], step=int(chunked_messages[2]), safe=("safe" in chunked_messages)
            )
        elif command == "chunk":
            show_chunk_range()


agent.say(player_mention + "run script")
