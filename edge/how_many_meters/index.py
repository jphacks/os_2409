from math import pi
from config import config
from os import remove

save_file_path = "edge/how_many_meters/save.txt"


def how_many_meters(role):
    """
    消費したロール数から大体何メートルのトイレットペーパーを消費したのか算出する
    これは全体の平均での消費量なので、最初の方（巻き取り径が大きい場合）では慎重に算出されるし、最後の方（巻き取り径が小さい場合）では敏感に算出される。
    """
    return pi * role * config.get_mean_dimameter() / 1000


def save_and_check(role):
    consumed_meters = how_many_meters(role)
    current_consumed_meters = read_consumed_meters()
    total_consumed_meters = float(current_consumed_meters) + float(consumed_meters)
    remove(save_file_path)
    with open(save_file_path, mode="w") as f:
        f.write(str(total_consumed_meters))
    if total_consumed_meters > config.get_boundary_count():
        print("8割以上使ったっぽいので通知する")


def read_consumed_meters():
    with open("edge/how_many_meters/save.txt", mode="r+") as f:
        current_consumed_meters = f.readline()
        return float(current_consumed_meters)


if __name__ == "__main__":
    save_and_check(100)
