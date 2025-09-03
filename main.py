from src.bili import MyLive


def danmu(event):
    print(event)


if __name__ == "__main__":
    instance = MyLive(room_id=100052)
    try:
        instance.on("danmu")(danmu)
        instance.start()
    except KeyboardInterrupt:
        instance.stop()
