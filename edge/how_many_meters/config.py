from singleton import Singleton


class Config(Singleton):
    """各種設定を保存する・提供するシングルトンクラス"""

    def __init__(self):
        # 芯の内径（直径）
        self.__core_inner_diameter = 38
        # 全体の内径（直径）
        self.__inner_dimameter = 100
        # ひとロールの合計m
        self.__meters = 37.5

    def get_meters(self):
        return self.__meters

    def get_mean_dimameter(self):
        return (self.__core_inner_diameter + self.__inner_dimameter) / 2

    def get_boundary_count(self):
        return self.__meters * 0.8


config = Config()
