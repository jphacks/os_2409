import requests
import json
from enum import Enum


def __edit(params):
    requests.post(
        "https://editdata-t2l7bkkhbq-dt.a.run.app",
        data=json.dumps(params),
        headers={"Content-Type": "application/json"},
    )


def __get():
    res = requests.get("https://getdata-t2l7bkkhbq-dt.a.run.app")
    return json.loads(res.content)


def set_in_room(value: bool):
    __edit({"in_room": value})


class UnchType(Enum):
    BANANA = "banana"
    KATAI = "katai"
    KOROKORO = "korokoro"
    BISHA = "bisha"

    @classmethod
    def value_of(cls, target_value):
        for e in UnchType:
            if e.value == target_value:
                return e
        raise ValueError("{} は有効な値ではありません".format(target_value))


def get_unch_type() -> UnchType:
    raw_value = __get()["unch_type"]
    if raw_value == None:
        raise ValueError("unch_typeが存在しませんでした")
    return UnchType.value_of(raw_value)


if __name__ == "__main__":
    print(get_unch_type())
