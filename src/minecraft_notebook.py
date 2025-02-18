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
            agent.say(get_player_direction())
            agent.say("troal fin")
        elif chunked_messages[0] == "come":
            # エージェントを自分の前に呼び出す
            agent_teleport_player()



