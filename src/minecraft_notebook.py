agent.say(player.position)


def agent_teleport_player():
    agent.teleport(["^0", "^0", "^1"])

def set_agent_azimuth(azimuth: int):
    for i in range(4):
        if agent.rotation == azimuth:
            break
        agent.turn("right")

set_agent_azimuth(90)




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



