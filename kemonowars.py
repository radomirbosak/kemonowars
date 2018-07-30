import json
import random

from PIL import Image


STATE_PATH = 'state.json'
TILE_SIZE = 48


CELL_WATER = -1
CELL_RESERVED = -2


def load_state(filename):
    with open(filename, 'r') as fd:
        return json.load(fd)


def save_state(filename, newstate):
    with open(filename, 'w') as fd:
        json.dump(newstate, fd, indent=2, sort_keys=True)


def load_avatars():
    avatarid_min, avatarid_max = (-1, 31)
    
    avatars = {}

    for avatar_id in range(avatarid_min, avatarid_max + 1):
        # avatar_id = i + 1
        filename = 'images/{}.png'.format(avatar_id)
        avatars[avatar_id] = Image.open(filename).resize(size=(TILE_SIZE, TILE_SIZE), resample=Image.BICUBIC)

    return avatars


def get_players(tiles):
    players = set()
    for row in tiles:
        for cell in row:
            if cell > 0:
                players.add(cell)
    return players


def state_from_image(filename, water=(0, 0, 0)):
    mapimg = Image.open(filename)

    result = []

    for y in range(mapimg.height):
        row = []
        for x in range(mapimg.width):
            color = mapimg.getpixel((x, y))

            row.append(
                -1 if color == water
                else 0
            )
        result.append(row)

    return result


def gen_neighbors(tiles, x, y):
    for (xd, yd) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        if x + xd < 0:
            continue
        if x + xd >= len(tiles[0]):
            continue
        if y + yd < 0:
            continue
        if y + yd >= len(tiles):
            continue

        yield (x + xd, y + yd)


# def get_all_tiles(tiles):
#     for y in range(tiles):
#         for x in range(stop)


def possible_expansion(player_id, tiles):
    possibilities = set()

    for y, row in enumerate(tiles):
        for x, cell in enumerate(row):
            neighbor_players = set(
                tiles[ny][nx] for
                nx, ny in gen_neighbors(tiles, x, y)
            )

            if cell not in [CELL_WATER, player_id] \
                    and player_id in neighbor_players:
                possibilities.add((x, y))
    return possibilities


def choose_attack(player_id, tiles):
    return random.choice(list(possible_expansion(player_id, tiles)))


def compose_final_image(tiles, attacks):
    width = len(tiles[0])
    height = len(tiles)

    fullimg = Image.new("RGB", (width * TILE_SIZE, height * TILE_SIZE))
    avatars = load_avatars()
    attackimg = Image.open('images/paw.png').resize(size=(TILE_SIZE, TILE_SIZE), resample=Image.BICUBIC)

    # update expansions
    # expansions = possible_expansion(tiles, 1)
    # for y, row in enumerate(tiles):
    #     for x, cell in enumerate(row):
    #         if (x, y) in expansions:
    #             tiles[y][x] = -2



    for y, row in enumerate(tiles):
        for x, cell in enumerate(row):
            fullimg.paste(avatars[cell], (x*TILE_SIZE, y*TILE_SIZE))

    for player_id, attack_tiles in attacks:
        for x, y in attack_tiles:
            fullimg.paste(attackimg, (x*TILE_SIZE, y*TILE_SIZE), attackimg)

    return fullimg


def process_attacks(tiles, attacks):
    for player_id, attack_tiles in attacks:
        for x, y in attack_tiles:
            if random.choice([True, True, False]):
                tiles[y][x] = player_id


def plan_attacks(tiles):
    attacks = []
    for player_id in get_players(tiles):
        ax, ay = choose_attack(player_id, tiles)
        attacks.append([player_id, [[ax, ay]]])
    return attacks


def main():
    state = load_state(STATE_PATH)
    tiles = state['tiles']

    old_attacks = state.get('attacks') or []

    process_attacks(tiles, old_attacks)

    # for player_id in get_players(tiles):
    #     ax, ay = choose_attack(player_id, tiles)
    #     tiles[ay][ax] = -2

    #new_attacks = [[1, [[4, 4]]]]

    new_attacks = plan_attacks(tiles)

    fullimg = compose_final_image(tiles, new_attacks)
    fullimg.save('result.png')

    newstate = {
        'tiles': tiles,
        'attacks': new_attacks,
    }

    save_state(STATE_PATH, newstate)


if __name__ == '__main__':
    main()
