#!/usr/bin/env python3
"""Generate VS Code color theme variations from base colors."""

import colorsys
import json
import os


def hex_to_hsl(hex_color: str) -> tuple[float, float, float]:
    """Convert hex color to HSL (hue 0-360, sat 0-100, light 0-100)."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s * 100, l * 100


def hsl_to_hex(h: float, s: float, l: float) -> str:
    """Convert HSL (hue 0-360, sat 0-100, light 0-100) to hex color."""
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def generate_bright_version(hex_color: str, lightness_boost: float = 25) -> str:
    """Generate a brighter version of the given color."""
    h, s, l = hex_to_hsl(hex_color)
    new_l = min(100, l + lightness_boost)
    return hsl_to_hex(h, s, new_l)


def generate_settings(base_color: str, bright_color: str) -> dict:
    """Generate VS Code settings dict."""
    return {
        "workbench.colorCustomizations": {
            "titleBar.activeBackground": base_color,
            "titleBar.inactiveBackground": bright_color,
            "titleBar.border": bright_color,
            "statusBar.background": bright_color,
            "statusBar.debuggingBackground": bright_color,
            "tab.activeBorder": bright_color,
        }
    }


def save_variation(output_dir: str, name: str, settings: dict) -> None:
    """Save settings to a JSON file."""
    path = os.path.join(output_dir, name)
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "settings.json"), "w") as f:
        json.dump(settings, f, indent=4)
    print(f"Created: {path}/settings.json")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "color_variations")

    # Base colors to generate variations from
    base_colors = {
        # Greens
        "green": "#008200",
        "forest": "#228b22",
        "emerald": "#046307",
        "olive": "#556b2f",
        "lime": "#32cd32",
        "sea_green": "#2e8b57",
        "dark_green": "#013220",
        "mint": "#3eb489",
        "sage": "#77815c",
        "fern": "#4f7942",
        "moss": "#8a9a5b",
        "hunter": "#355e3b",
        "jade": "#00a86b",
        "spring": "#00ff7f",
        "clover": "#009e60",
        "pine": "#01796f",
        "jungle": "#29ab87",
        "malachite": "#0bda51",
        "shamrock": "#009e49",
        "basil": "#579229",
        "avocado": "#568203",
        "pickle": "#597d35",
        "artichoke": "#8f9779",
        "asparagus": "#87a96b",
        "seaweed": "#1b4d3e",

        # Blues
        "blue": "#0055aa",
        "navy": "#000080",
        "royal_blue": "#4169e1",
        "steel_blue": "#4682b4",
        "dodger_blue": "#1e90ff",
        "midnight": "#191970",
        "slate_blue": "#6a5acd",
        "cobalt": "#0047ab",
        "azure": "#0080ff",
        "cerulean": "#007ba7",
        "sapphire": "#0f52ba",
        "denim": "#1560bd",
        "ocean": "#0077be",
        "sky": "#87ceeb",
        "powder": "#b0e0e6",
        "ice": "#99ffff",
        "electric_blue": "#7df9ff",
        "cornflower": "#6495ed",
        "periwinkle": "#ccccff",
        "baby_blue": "#89cff0",
        "carolina": "#4b9cd3",
        "oxford": "#002147",
        "prussian": "#003153",
        "ultramarine": "#3f00ff",
        "lapis": "#26619c",
        "blueberry": "#4f86f7",
        "space": "#1d2951",
        "admiral": "#051e3e",

        # Purples
        "purple": "#6b2d8b",
        "indigo": "#4b0082",
        "violet": "#8b008b",
        "plum": "#8e4585",
        "amethyst": "#9966cc",
        "grape": "#6f2da8",
        "lavender_dark": "#734f96",
        "mauve": "#76608a",
        "orchid": "#da70d6",
        "lilac": "#c8a2c8",
        "heather": "#b7a9d6",
        "eggplant": "#614051",
        "wine": "#722f37",
        "mulberry": "#c54b8c",
        "byzantium": "#702963",
        "imperial": "#602f6b",
        "royal_purple": "#7851a9",
        "iris": "#5a4fcf",
        "wisteria": "#c9a0dc",
        "thistle": "#d8bfd8",
        "aubergine": "#3d0734",
        "boysenberry": "#873260",
        "jam": "#58427c",

        # Reds
        "red": "#aa2200",
        "crimson": "#dc143c",
        "maroon": "#800000",
        "ruby": "#9b111e",
        "burgundy": "#722f37",
        "scarlet": "#ff2400",
        "blood_red": "#660000",
        "cherry": "#de3163",
        "cardinal": "#c41e3a",
        "fire": "#ff3c00",
        "vermillion": "#e34234",
        "brick": "#cb4154",
        "barn_red": "#7c0a02",
        "carmine": "#960018",
        "garnet": "#733635",
        "strawberry": "#fc5a8d",
        "candy_apple": "#ff0800",
        "rosewood": "#65000b",
        "merlot": "#730039",
        "redwood": "#a45a52",
        "tomato": "#ff6347",
        "poppy": "#e35335",
        "venetian": "#c80815",
        "ferrari": "#ff2800",
        "indian_red": "#cd5c5c",

        # Oranges
        "orange": "#cc6600",
        "burnt_orange": "#cc5500",
        "rust": "#b7410e",
        "tangerine": "#ff9966",
        "pumpkin": "#ff7518",
        "copper": "#b87333",
        "peach": "#ffcba4",
        "apricot": "#fbceb1",
        "coral": "#ff7f50",
        "salmon": "#fa8072",
        "cantaloupe": "#ffa62f",
        "mango": "#ff8243",
        "carrot": "#ed9121",
        "papaya": "#ffefd5",
        "persimmon": "#ec5800",
        "terracotta": "#e2725b",
        "sunset": "#fad6a5",
        "cinnamon": "#d2691e",
        "ginger": "#b06500",
        "caramel": "#ffd59a",
        "butterscotch": "#e09540",
        "tiger": "#fc6600",
        "marigold": "#eaa221",
        "nectarine": "#ff6a4d",

        # Yellows
        "gold": "#b8860b",
        "mustard": "#ffdb58",
        "amber": "#ffbf00",
        "honey": "#eb9605",
        "bronze": "#cd7f32",
        "lemon": "#fff44f",
        "canary": "#ffef00",
        "sunflower": "#ffda03",
        "saffron": "#f4c430",
        "dandelion": "#f0e130",
        "butter": "#ffff99",
        "cream": "#fffdd0",
        "flax": "#eedc82",
        "goldenrod": "#daa520",
        "corn": "#fbec5d",
        "banana": "#ffe135",
        "dijon": "#c49102",
        "ochre": "#cc7722",
        "jasmine": "#f8de7e",
        "champagne": "#f7e7ce",
        "wheat": "#f5deb3",
        "tuscany": "#fcd12a",
        "blonde": "#faf0be",
        "straw": "#e4d96f",

        # Pinks
        "pink": "#aa3366",
        "magenta": "#8b008b",
        "rose": "#c21e56",
        "fuchsia": "#c154c1",
        "hot_pink": "#ff1493",
        "raspberry": "#e30b5c",
        "blush": "#de5d83",
        "coral_pink": "#f88379",
        "watermelon": "#fd4659",
        "flamingo": "#fc8eac",
        "bubblegum": "#ffc1cc",
        "peony": "#ffb7c5",
        "carnation": "#ffa6c9",
        "rouge": "#a94064",
        "punch": "#ec5578",
        "cerise": "#de3163",
        "tulip": "#ff878d",
        "ballet": "#f4c2c2",
        "petal": "#f7cac9",
        "salmon_pink": "#ff91a4",
        "hibiscus": "#b6316c",
        "bougainvillea": "#9b2d30",
        "dragonfruit": "#ff7a7a",

        # Teals & Cyans
        "teal": "#008080",
        "cyan": "#008b8b",
        "turquoise": "#00ced1",
        "aqua": "#00868b",
        "peacock": "#005f6a",
        "seafoam": "#71eeb8",
        "lagoon": "#4e7f9e",
        "caribbean": "#00cccc",
        "mermaid": "#47a0b5",
        "arctic": "#5fa7d9",
        "glacier": "#80b3c4",
        "pool": "#00c5cd",
        "spruce": "#2f6669",
        "verdigris": "#43b3ae",
        "viridian": "#40826d",
        "celadon": "#ace1af",
        "eucalyptus": "#5f9ea0",
        "robins_egg": "#00cccc",
        "aegean": "#1f456e",
        "capri": "#00bfff",
        "bondi": "#0095b6",

        # Browns
        "brown": "#8b4513",
        "chocolate": "#7b3f00",
        "coffee": "#6f4e37",
        "sienna": "#a0522d",
        "mahogany": "#c04000",
        "chestnut": "#954535",
        "cocoa": "#d2691e",
        "mocha": "#967969",
        "walnut": "#773f1a",
        "umber": "#635147",
        "espresso": "#3c1414",
        "hazelnut": "#a67b5b",
        "cacao": "#5a3d2b",
        "truffle": "#483c32",
        "biscuit": "#d19c57",
        "tan": "#d2b48c",
        "camel": "#c19a6b",
        "fawn": "#e5aa70",
        "sand": "#c2b280",
        "taupe": "#483c32",
        "khaki": "#c3b091",
        "mushroom": "#b5a290",
        "beaver": "#9f8170",
        "latte": "#c1a582",
        "toffee": "#755139",
        "pecan": "#6d5146",
        "leather": "#906051",
        "cognac": "#9a463d",
        "brandy": "#87413f",
        "auburn": "#a52a2a",
        "hickory": "#87413f",

        # Grays
        "charcoal": "#36454f",
        "slate": "#708090",
        "gunmetal": "#2a3439",
        "graphite": "#474a51",
        "pewter": "#8f8f8f",
        "ash": "#b2beb5",
        "iron": "#48494b",
        "smoke": "#738276",
        "steel": "#71797e",
        "silver": "#c0c0c0",
        "platinum": "#e5e4e2",
        "fossil": "#787276",
        "flint": "#6b6969",
        "anchor": "#4e5754",
        "shadow": "#4a4e4d",
        "carbon": "#333333",
        "onyx": "#353839",
        "obsidian": "#3d3d3d",
        "raven": "#303030",
        "ink": "#1a1a1a",
        "jet": "#0a0a0a",
        "ebony": "#555d50",
        "storm": "#4f666a",
        "thunder": "#424e54",
        "cloud": "#c1c6c8",

        # Metallics & Special
        "brass": "#b5a642",
        "antique_gold": "#cfb53b",
        "rose_gold": "#b76e79",
        "patina": "#407d7a",
        "oxidized": "#4e5d5e",
        "aged_copper": "#6d8e8e",
        "verdigris_metal": "#669999",
        "burnished": "#a17d4d",
        "aged_bronze": "#6e5d3b",

        # Nature
        "bark": "#87591a",
        "pebble": "#a6a18a",
        "clay": "#b66a50",
        "sandstone": "#786d5f",
        "granite": "#676767",
        "marble": "#c8c8c8",
        "limestone": "#d9d0c0",
        "shale": "#4e5754",
        "driftwood": "#9f8c76",
        "bamboo": "#d4cd93",
        "palm": "#5f7552",
        "frog": "#71b551",
        "iguana": "#71aa34",
        "gecko": "#87a56c",

        # Food & Drinks
        "wine_red": "#591d35",
        "merlot_dark": "#4c1c24",
        "claret": "#7f1734",
        "port": "#6c3461",
        "sherry": "#b47e59",
        "bourbon": "#9e511f",
        "whiskey": "#d59746",
        "ale": "#bf660c",
        "stout": "#302316",
        "espresso_dark": "#231812",
        "chai": "#a67c52",
        "matcha": "#78a55a",
        "berry": "#8e4585",
        "plum_dark": "#660066",
        "fig": "#4d4e55",
        "raisin": "#563c36",
        "date": "#5e4530",
        "olive_oil": "#8a8d2a",
        "pistachio": "#93c572",
        "almond": "#ecdcb5",
        "cashew": "#f9d29d",
        "peanut": "#d4a76a",
        "hazel": "#a67449",

        # Gems & Minerals
        "ruby_gem": "#e0115f",
        "sapphire_dark": "#082567",
        "emerald_gem": "#046a38",
        "topaz": "#ffc87c",
        "citrine": "#e4d00a",
        "peridot": "#e6e200",
        "aquamarine": "#7fffd4",
        "tourmaline": "#86a1a9",
        "tanzanite": "#6c5b9e",
        "opal": "#a8c3bc",
        "moonstone": "#c4cfd0",
        "onyx_gem": "#0f0f0f",
        "jasper": "#d73b3e",
        "agate": "#b5a691",
        "turquoise_gem": "#40e0d0",
        "lapis_lazuli": "#26619c",
        "malachite_gem": "#0bda51",

        # Celestial
        "nebula": "#483d8b",
        "cosmos": "#493d5e",
        "supernova": "#ff4500",
        "aurora": "#78d64b",
        "eclipse": "#3e3e42",
        "meteor": "#4e4e56",
        "comet": "#c4c4c4",
        "starlight": "#f0f0ff",
        "twilight": "#4b5d67",
        "dusk": "#4e3d42",
        "dawn": "#ffb899",
        "solar": "#ffcc00",
        "lunar": "#c0c0c0",
        "mercury": "#e1e1e1",
        "venus": "#ffc649",
        "mars": "#ad6242",
        "jupiter": "#c99039",
        "saturn": "#c5ab6e",
        "neptune": "#3454b4",
        "pluto": "#d7c7aa",

        # Seasons
        "autumn": "#eb9e34",
        "harvest": "#da9100",
        "pumpkin_spice": "#c45a27",
        "falling_leaves": "#c65d07",
        "winter": "#68c3de",
        "frost": "#e1e9eb",
        "blizzard": "#b8d4e8",
        "spring_green": "#80ff72",
        "blossom": "#ffb7c5",
        "fresh": "#7fff00",
        "summer": "#ffcc00",
        "sunny": "#f9d71c",
        "tropical": "#00cc99",
    }

    for name, base in base_colors.items():
        bright = generate_bright_version(base, lightness_boost=25)
        h, s, l = hex_to_hsl(base)
        print(f"{name}: base={base} (HSL: {h:.0f}, {s:.0f}%, {l:.0f}%) -> bright={bright}")

        settings = generate_settings(base, bright)
        save_variation(output_dir, name, settings)


if __name__ == "__main__":
    main()
