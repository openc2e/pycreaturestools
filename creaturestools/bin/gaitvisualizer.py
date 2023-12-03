import argparse
import os
import re
import creaturestools.sprites
import enum
import collections
import PIL.Image
import PIL.ImageDraw

# gait idx 0 13141516R - normal
# gait idx 2 78798081R - tired
# gait idx 7 8282838482858384R - drunk

# poses
# 0: ??13123120101XX
# 1: ??22122120102XX
# 2: ??22122121233XX
# 3: ??32102101233XX
# 4: ?011121120111XX
# 5: ?011121120112XX
# 6: ?12112110123XXX
# 7: ?221101100133XX
# 8: ?001121120222XX
# 9: ?021121120222XX
# 10: ?221121121223XX
# 11: ?321101101233XX
# 12: ??12022011201XX
# 13: ?201221010012XX
# 14: ?201013221101XX
# 15: ?101011221200XX
# 16: ?203221010111XX
# 17: ?113011222323XX
# 18: ?013210002323XX
# 19: ?011223012323XX
# 20: ?010003212323XX
# 21: ?022011221111XX
# 22: ?023220000011XX
# 23: ?021221010010XX
# 24: ?020013221100XX
# 25: ??33001212323XX
# 26: ??23200002323XX
# 27: ??31213002323XX
# 28: ??20003202323XX
# 29: ?123011220011XX
# 30: ?023210000012XX
# 31: ?121223011100XX
# 32: ?120003211200XX
# 33: X431221221111XX
# 34: X121223011100XX
# 35: X022122122323XX
# 36: X402122120202XX
# 37: X412122121111XX
# 38: 2422221112223XX
# 39: X422122122323XX
# 40: 2422221221211XX
# 41: 2422231221211XX
# 42: X431221220212XX
# 43: X431223120222XX
# 44: X122122121212XX
# 45: X222122120100XX
# 46: X103023022222XX
# 47: X002022022212XX
# 48: X123023021212XX
# 49: !222011220111XX
# 50: !223210000010XX
# 51: !221222010010XX
# 52: !220003211000XX
# 53: !421011222222XX
# 54: !422210002222XX
# 55: !421221012222XX
# 56: !120002212222XX
# 57: X023023021212XX
# 58: X003023020202XX
# 59: 2?22122120112XX
# 60: 3?22122120112XX
# 61: X201221010012XX
# 62: X201013221101XX
# 63: X101011221200XX
# 64: X203221010111XX
# 65: ?013123121212XX
# 66: ??31101103333XX
# 67: ?011221000022XX
# 68: ?231113332300XX
# 69: ?122212210133XX
# 70: ?132222220222XX
# 71: ?332222221100XX
# 72: ?122222121112XX
# 73: X122122122222XX
# 74: X222122121212XX
# 75: ?032212210223XX
# 76: ?221101102222XX
# 77: X003023022202XX
# 78: ?011010210100XX
# 79: ?013221010100XX
# 80: ?011212230001XX
# 81: ?010002220001XX
# 82: ?021222012322XX
# 83: ?113011222322XX
# 84: ?033210002311XX
# 85: ?010003212322XX
# 86: 242212212011200
# 87: 242212212011200
# 88: 242212212011200
# 89: 242212212011200
# 90: 242212212011200
# 91: 242212212011200
# 92: 242212212011200
# 93: 242212212011200
# 94: 242212212011200
# 95: 242212212011200
# 96: 242212212011200
# 97: 242212212011200
# 98: 242212212011200
# 99: 242212212011200


class Vec2:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)

    def __getitem__(self, i):
        if i == 0:
            return self.x
        if i == 1:
            return self.y
        raise NotImplementedError(i)

    def tuple(self):
        return (self.x, self.y)


class MockBody:
    def __init__(self, *, body_data, sprite):
        self.body_data = body_data
        self.sprite = sprite

    def current_sprite(self):
        return self.sprite[self.pose]

    __slots__ = ["body_data", "pose", "position", "sprite"]
    pass


class MockLimb:
    def __init__(self, *, limb_data, sprite):
        self.limb_data = limb_data
        self.sprite = sprite
        self.next = None

    def current_sprite(self):
        return self.sprite[self.pose]

    def start_relative(self):
        return self.limb_data[self.pose][0]

    def start_absolute(self):
        return self.position + self.limb_data[self.pose][0]

    def end_relative(self):
        return self.limb_data[self.pose][1]

    def end_absolute(self):
        return self.position + self.end_relative()

    def tip_start(self):
        limb = self
        while limb.next:
            limb = limb.next
        return limb.start_absolute()

    def tip_end(self):
        limb = self
        while limb.next:
            limb = limb.next
        return limb.end_absolute()

    __slots__ = ["limb_data", "next", "pose", "position", "sprite"]
    pass


def chunks(seq, n):
    return list(zip(*([iter(seq)] * n)))


def read_body_data(buf):
    if not isinstance(buf, str):
        if not isinstance(buf, bytes):
            buf = buf.read()
        buf = buf.decode("utf-8")
    lines = re.split("\r?\n", buf.strip())
    assert len(lines) == 10 or len(lines) == 26
    out = []
    for l in lines:
        out.append([])
        for x, y in chunks(re.split(r"\s+", l.strip()), 2):
            out[-1].append(Vec2(int(x), int(y)))
    return out


class CaseInsensitiveFilesystem:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def open(self, fname):
        # TODO: actually make it case insensitive
        return open(os.path.join(self.base_dir, fname), "rb")

    def read_body_data(self, name):
        return read_body_data(self.open(os.path.join("Body Data", name + ".att")))

    def read_spr_file(self, name):
        images = creaturestools.sprites.read_spr_file(
            self.open(os.path.join("Images", name + ".spr"))
        )
        for i in range(len(images)):
            # this is so stupid. why can't PIL support a basic colorkey on paletted images?
            img = images[i]
            img.info["transparency"] = 0
            img.apply_transparency()
            images[i] = img.convert("RGBA")
        return images


class Downfoot(enum.Enum):
    RIGHT = 0
    LEFT = 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data-directory", required=True)
    parser.add_argument(
        "-s",
        "--selector",
        required=True,
        help="species/gender, life stage, breed slot selector, e.g. 400 for a baby female norn in breed slot 0",
    )
    parser.add_argument(
        "-p",
        "--poses",
        required=True,
        type=lambda s: s.split(","),
        help="Comma-separated list of pose strings",
    )
    args = parser.parse_args()

    print(
        "WARNING: this does not calculate downfeet/walking in the same way as the official game"
    )

    fs = CaseInsensitiveFilesystem(args.data_directory)
    poses = args.poses
    if poses == ["default"]:
        poses = [
            "?201221010012XX",
            "?201013221101XX",
            "?101011221200XX",
            "?203221010111XX",
        ]
    elif poses == ["tired"]:
        poses = [
            "?011010210100XX",
            "?013221010100XX",
            "?011212230001XX",
            "?010002220001XX",
        ]
    elif poses == ["drunk"]:
        poses = [
            "?021222012322XX",
            "?021222012322XX",
            "?113011222322XX",
            "?033210002311XX",
            "?021222012322XX",
            "?010003212322XX",
            "?113011222322XX",
            "?033210002311XX",
        ]

    selector = args.selector

    # load att and spr data and set up structures
    body = MockBody(
        body_data=fs.read_body_data("b" + selector),
        sprite=fs.read_spr_file("b" + selector),
    )
    build_body_part = lambda part: MockLimb(
        limb_data=fs.read_body_data(part + selector),
        sprite=fs.read_spr_file(part + selector),
    )
    head = build_body_part("a")
    left_thigh = build_body_part("c")
    left_thigh.next = build_body_part("d")
    left_thigh.next.next = build_body_part("e")
    right_thigh = build_body_part("f")
    right_thigh.next = build_body_part("g")
    right_thigh.next.next = build_body_part("h")
    left_arm = build_body_part("i")
    left_arm.next = build_body_part("j")
    right_arm = build_body_part("k")
    right_arm.next = build_body_part("l")

    # set up canvas
    canvas = PIL.Image.new("RGBA", size=(5000, 5000))  # TODO: how big?
    # canvas.putpalette(creaturestools.sprites.CREATURES1_PALETTE)
    canvas.paste((0, 0, 0, 255), (0, 0, canvas.width, canvas.height))
    draw = PIL.ImageDraw.Draw(canvas)

    # helper functions
    def set_sprites(pose_string):
        assert len(pose_string) == 15
        if pose_string[0] != "?":
            raise NotImplementedError(pose_string)
        if pose_string[1] == "?":
            raise NotImplementedError(pose_string)
        if pose_string[13] != "X" or pose_string[14] != "X":
            raise NotImplementedError(pose_string)
        # assume direction is east
        head.pose = ord(pose_string[1]) - ord("0")
        body.pose = ord(pose_string[2]) - ord("0")
        left_thigh.pose = ord(pose_string[3]) - ord("0")
        left_thigh.next.pose = ord(pose_string[4]) - ord("0")
        left_thigh.next.next.pose = ord(pose_string[5]) - ord("0")
        right_thigh.pose = ord(pose_string[6]) - ord("0")
        right_thigh.next.pose = ord(pose_string[7]) - ord("0")
        right_thigh.next.next.pose = ord(pose_string[8]) - ord("0")
        left_arm.pose = ord(pose_string[9]) - ord("0")
        left_arm.next.pose = ord(pose_string[10]) - ord("0")
        right_arm.pose = ord(pose_string[11]) - ord("0")
        right_arm.next.pose = ord(pose_string[12]) - ord("0")

    def calculate_positions_from_body():
        for trunk_part, limb in enumerate(
            (head, left_thigh, right_thigh, left_arm, right_arm)
        ):
            offset = body.position + body.body_data[body.pose][trunk_part]
            while limb:
                limb.position = offset - limb.start_relative()
                offset += limb.end_relative() - limb.start_relative()
                limb = limb.next

    def calculate_positions_from_downfoot():
        # calculate body
        offset = Vec2(0, 0)
        if downfoot == Downfoot.LEFT:
            downthigh = left_thigh
            offset += body.body_data[body.pose][1]
        else:
            downthigh = right_thigh
            offset += body.body_data[body.pose][2]

        offset += downthigh.end_relative() - downthigh.start_relative()
        offset += downthigh.next.end_relative() - downthigh.next.start_relative()
        offset += (
            downthigh.next.next.end_relative() - downthigh.next.next.start_relative()
        )
        # MUST USE SAVED DOWNFOOT POSITION FROM LAST TIME, NOT BASED OFF OF NEW BODY DATA / NEW POSE
        body.position = downfoot_position - offset

        calculate_positions_from_body()

    def render_to_canvas():
        # assume direction is east
        for part in (
            left_arm.next,
            left_arm,
            left_thigh.next.next,
            left_thigh.next,
            left_thigh,
            body,
            head,
            right_thigh,
            right_thigh.next,
            right_thigh.next.next,
            right_arm,
            right_arm.next,
        ):
            canvas.alpha_composite(
                part.current_sprite(), (part.position.x, part.position.y)
            )

        # draw feet tips
        render_rect((0, 128, 0, 255), left_thigh.next.next.start_absolute())
        render_rect((0, 255, 0, 255), left_thigh.next.next.end_absolute())
        render_rect((0, 0, 128, 255), right_thigh.next.next.start_absolute())
        render_rect((0, 0, 255, 255), right_thigh.next.next.end_absolute())

    def annotate(text):
        # get bounds
        upper_left_corner = body.position
        for part in (head, left_thigh, right_thigh, left_arm, right_arm):
            while part:
                upper_left_corner = Vec2(
                    min(upper_left_corner.x, part.position.x),
                    min(upper_left_corner.y, part.position.y),
                )
                part = part.next

        # add text
        draw.text(upper_left_corner, text, fill=(255, 255, 255, 255))

    def render_rect(color, start):
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                canvas.putpixel((start.x + i, start.y + j), color)

    # generate first pose
    body.position = Vec2(50, 50)  # TODO: where to start?
    set_sprites(poses[0])
    calculate_positions_from_body()
    render_to_canvas()
    annotate("0")

    # figure out the initial downfoot
    if left_thigh.tip_start().y > right_thigh.tip_start().y:
        downfoot = Downfoot.LEFT
        downfoot_position = left_thigh.tip_end()
    else:
        downfoot = Downfoot.RIGHT
        downfoot_position = right_thigh.tip_end()

    for i in range(1, len(poses) + 1):
        pose_idx = i % len(poses)
        # shift down, generate next pose
        downfoot_position += Vec2(0, 75)
        set_sprites(poses[pose_idx])
        calculate_positions_from_downfoot()
        # did downfoot change?
        if downfoot == Downfoot.LEFT:
            if right_thigh.tip_start().y >= left_thigh.tip_start().y:
                downfoot = Downfoot.RIGHT
                downfoot_position.x = right_thigh.tip_end().x
                calculate_positions_from_downfoot()
        elif downfoot == Downfoot.RIGHT:
            if left_thigh.tip_start().y >= right_thigh.tip_start().y:
                downfoot = Downfoot.LEFT
                downfoot_position.x = left_thigh.tip_end().x
                calculate_positions_from_downfoot()
        render_to_canvas()
        annotate(str(pose_idx))

    # save
    bbox = canvas.convert("RGB").getbbox()  # so stupid, getbbox doesn't work on RGBA
    canvas = canvas.crop((bbox[0] - 50, bbox[1] - 50, bbox[2] + 50, bbox[3] + 50))
    canvas.save("gait.png")


if __name__ == "__main__":
    main()
