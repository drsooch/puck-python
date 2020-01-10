from puck.Games import get_game_ids, FullGame, BannerGame


def passing(type):
    if type == FullGame:
        print('FullGame')
    elif type == BannerGame:
        print('Banner')
    else:
        print('nope')


if __name__ == "__main__":
    passing(FullGame)
    passing(BannerGame)
