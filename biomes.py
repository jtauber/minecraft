from anvil import RegionReader
from png import output_png

DIRECTORY = "/Users/jtauber/Library/Application Support/minecraft/saves/Jamax (World 2)-2/region"

reader = RegionReader(DIRECTORY)


def get_biomes(cx, cz):
    return reader.get_chunk(cx, cz).get("Level", {}).get("Biomes")


def make_colour(features):

    r, g, b = 0, 0, 0


    if "stone" in features:
        r, g, b = (128, 128, 128)

    ## ocean

    if "ocean" in features:
        r, g, b = (0, 0, 255)

    ## plains

    if "plains" in features:
        r, g, b = (128, 192, 64)

    ## desert

    if "desert" in features:
        r, g, b = (192, 192, 128)

    ## badlands

    ## mountains

    if "mountains" in features:
        r, g, b = (192, 192, 192)

    ## forest

    if "forest" in features:
        r, g, b = (0, 128, 32)

    if "forest" in features and "mountains" in features:
        r, g, b = (128, 192, 96)

    ## taiga

    if "taiga" in features:
        r, g, b = (192, 224, 192)

    if "taiga" in features and "mountains" in features:
        r, g, b = (224, 255, 224)

    ## swamp

    if "swamp" in features:
        r, g, b = (32, 96, 128)

    ## river

    if "river" in features:
        r, g, b = (0, 128, 255)

    ## beach

    if "beach" in features:
        r, g, b = (255, 255, 192)

    ## savanna

    if "savanna" in features:
        r, g, b = (128, 192, 0)

    ## jungle

    if "jungle" in features:
        r, g, b = (32, 192, 64)

    ## mushroom fields?

    ## tundra

    if "tundra" in features:
        r, g, b = (224, 240, 255)

    if "frozen" in features:
        r = min(255, r + 64)
        g = min(255, g + 64)
        b = min(255, b + 64)
    if "cold" in features:
        r = min(255, r + 32)
        g = min(255, g + 32)
        b = min(255, b + 32)
    if "deep" in features:
        r = max(0, r - 64)
        g = max(0, g - 64)
        b = max(0, b - 32)

    if "hills" in features:
        r = min(255, r + 32)
        g = min(255, g + 32)
        b = min(255, b + 32)

    if "tall" in features:
        r = max(0, r - 16)
        g = max(0, g - 16)
        b = max(0, b - 16)

    if "dark" in features:
        r = max(0, r - 32)
        g = max(0, g - 32)
        b = max(0, b - 16)

    assert 0 <= r <= 255, features
    assert 0 <= g <= 255, features
    assert 0 <= b <= 255, features

    if (r, g, b) == (0, 0, 0):
        print(features)

    return r, g, b


PALETTE = {
    0: make_colour({"ocean"}),
    1: make_colour({"plains"}),
    2: make_colour({"desert"}),
    3: make_colour({"mountains"}),
    4: make_colour({"forest"}),
    5: make_colour({"taiga"}),
    6: make_colour({"swamp"}),
    7: make_colour({"river"}),
    10: make_colour({"frozen", "ocean"}),
    16: make_colour({"beach"}),
    17: make_colour({"desert", "hills"}),
    18: make_colour({"forest", "hills"}),  # wooded hills
    19: make_colour({"taiga", "hills"}),
    21: make_colour({"jungle"}),
    22: make_colour({"jungle", "hills"}),
    23: make_colour({"jungle", "edge"}),
    24: make_colour({"deep", "ocean"}),
    25: make_colour({"stone", "shore"}),
    27: make_colour({"birch", "forest"}),
    28: make_colour({"birch", "forest", "hills"}),
    29: make_colour({"dark", "forest"}),
    32: make_colour({"tall", "taiga"}),  # giant tree taiga
    33: make_colour({"tall", "taiga", "hils"}),  # giant tree taiga hills
    34: make_colour({"forest", "mountains"}),  # wooded mountains
    35: make_colour({"savanna"}),
    36: make_colour({"savanna", "hills"}),  # savanna plateau
    44: make_colour({"warm", "ocean"}),
    45: make_colour({"lukewarm", "ocean"}),
    46: make_colour({"cold", "ocean"}),
    48: make_colour({"deep", "lukewarm", "ocean"}),
    49: make_colour({"deep", "cold", "ocean"}),
    50: make_colour({"deep", "frozen", "ocean"}),
    129: make_colour({"sunflower", "plains"}),
    130: make_colour({"desert", "lakes"}),
    132: make_colour({"flower", "forest"}),
    133: make_colour({"taiga", "mountains"}),
    134: make_colour({"swamp", "hills"}),
    149: make_colour({"modified", "jungle"}),
    155: make_colour({"tall", "birch", "forest"}),
    156: make_colour({"tall", "birch", "hills"}),
    157: make_colour({"dark", "forest", "hills"}),
    160: make_colour({"tall", "spruce", "taiga"}),  # giant spruce taiga
    162: make_colour({"modified", "gravelly", "mountains"}),
    163: make_colour({"shattered", "savanna"}),
    164: make_colour({"shattered", "savanna", "hills"}),  # shattered savanna plateau
    168: make_colour({"bamboo", "jungle"}),
    169: make_colour({"bamboo", "jungle", "hills"}),
}


def map_biomes(sx, ex, sz, ez, output_filename):

    unknown_biomes = set()

    pixels = {}
    for cx in range(sx, ex):
        print(cx)
        for cz in range(sz, ez):
            biomes = get_biomes(cx, cz)
            if biomes:
                y = 1
                for x in range(4):
                    for z in range(4):
                        biome = biomes[(y * 4 + z) * 4 + x]
                        if biome not in PALETTE:
                            PALETTE[biome] = (128, 0, 0)
                            unknown_biomes.add(biome)
                        colour = PALETTE[biome]
                        pixels[(cx - sx) * 4 + x, (cz - sz) * 4 + z] = colour

    output_png(output_filename, (ex - sx) * 4, (ez - sz) * 4, pixels)

    print(f"{unknown_biomes=}")


if __name__ == "__main__":
    map_biomes(-32, 48, -32, 48, "biomes-local.png")
    map_biomes(-256, 256, -256, 300, "biomes.png")
