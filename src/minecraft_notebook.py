import fnmatch
from typing import List

# 有益な地下資源の名称
underground_resource_list = ["*_ore", "ancient_debris"]

# 液体ブロック
liquid_block_list = ["water", "lava"]

# 普通のブロックの名称
normal_block_list = ["cobblestone", "granite", "andesite", "dirt", "deepslate", "blackstone", "stone"]


def show_agent_item_list():
    for i in range(1, 28):
        item = agent.get_item(i)
        agent.say(f"{i} : {item.id} {item.stack_size}/{item.max_stack_size}")


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
    agent.say(agent_position)
    agent.say(player_positoon)
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
    agent.say(azimuth)
    
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


def is_block_list_match_direction(direction: str, block_list: list) -> bool:
    """
    指定された方向において、ブロックのリストが所定のパターンにマッチするかを判定し、
    結果をブール値（True/False）で返却します。

    Parameters:
        direction (str): チェック対象の方向（例: 'north', 'south', 'east', 'west'）。
        block_list (list): 判定対象となるブロック名称のリスト。

    Returns:
        bool: ブロックリストが指定方向のパターンにマッチする場合は True、そうでない場合は False。
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
    
    Parameters:
        items (str): 検索対象のアイテム名称。
    
    Returns:
        int: アイテムが格納されているソケット番号。該当するソケットがない場合は、例外を発生させるか
             特定の値（例: -1）を返却する設計とします。
    """

    for item_name in items:
        for socket_index in range(1, 28):
            check_item = agent.get_item(socket_index)
            if fnmatch.fnmatch(check_item.id, item_name):
                return socket_index
    return -1
 

def agent_put_item(direction: str, item_names: List[str]) -> None:
    socket_index = get_agent_storage_socket_index(item_names)
    if socket_index < 1:
        agent.say(f"{item_names}を持っていません")
        return None
    agent.place(direction, socket_index)






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
        elif command == "agent_teleport":
            agent_teleport(chunked_messages[1], chunked_messages[2], chunked_messages[3])
        elif command == "item_list":
            show_agent_item_list()
        elif command == "what_block":
            agent.say(agent.inspect("forward"))
        elif command == "what_item":
            agent.say(agent.get_item(1))




