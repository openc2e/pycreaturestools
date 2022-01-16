from typing import NewType

from ._io_utils import *
from .exceptions import *


def _SimpleClass(cls):
    cls.__slots__ = [
        key
        for key, typ in cls.__annotations__.items()
        if getattr(typ, "__supertype__", None) != padding
    ]

    def __init__(self):
        for _ in self.__slots__:
            setattr(self, _, None)

    def __repr__(self):
        return (
            "<{} ".format(type(self).__name__)
            + " ".join("{}={!r}".format(_, getattr(self, _)) for _ in self.__slots__)
            + ">"
        )

    cls.__init__ = __init__
    cls.__repr__ = __repr__
    return cls


u8 = NewType("u8", int)
u8_8 = NewType("u8_8", [u8])
u8_256 = NewType("u8_256", [u8])
u16be = NewType("u16be", int)
padding = NewType("padding", bytes)
padding5 = NewType("padding5", padding)
padding7 = NewType("padding7", padding)
bytes4 = NewType("bytes4", bytes)
bytes16 = NewType("bytes16", bytes)
bytes32 = NewType("bytes32", bytes)
svrule48 = NewType("svrule48", bytes)


@_SimpleClass
class GeneHeader:
    type: u8
    subtype: u8
    id: u8
    generation: u8
    switchontime: u8
    flags: u8
    mutability: u8
    variant: u8


@_SimpleClass
class UnknownGene:
    header: GeneHeader
    data: bytes


@_SimpleClass
class NonGeneData:
    data: bytes


@_SimpleClass
class BrainLobeGene:
    header: GeneHeader
    lobe: bytes4
    updatetime: u16be
    x: u16be
    y: u16be
    width: u8
    height: u8
    red: u8
    green: u8
    blue: u8
    WTA: u8
    tissue: u8
    initrulealways: u8
    padding_always_zero: padding7
    initrule: svrule48
    updaterule: svrule48


@_SimpleClass
class BrainOrganGene:
    header: GeneHeader
    clockrate: u8
    damagerate: u8
    lifeforce: u8
    biotickstart: u8
    atpdamagecoefficient: u8


@_SimpleClass
class BrainTractGene:
    header: GeneHeader
    updatetime: u16be
    srclobe: bytes4
    srclobe_lowerbound: u16be
    srclobe_upperbound: u16be
    srclobe_numconnections: u16be
    destlobe: bytes4
    destlobe_lowerbound: u16be
    destlobe_upperbound: u16be
    destlobe_numconnections: u16be
    migrates: u8
    num_random_connections: u8
    srcvar: u8
    destvar: u8
    initrulealways: u8
    padding_always_zero: padding5
    initrule: svrule48
    updaterule: svrule48


@_SimpleClass
class BiochemistryReceptorGene:
    header: GeneHeader
    organ: u8
    tissue: u8
    locus: u8
    chemical: u8
    threshold: u8
    nominal: u8
    gain: u8
    flags: u8


@_SimpleClass
class BiochemistryReactionGene:
    header: GeneHeader
    r1_amount: u8
    r1_chem: u8
    r2_amount: u8
    r2_chem: u8
    p1_amount: u8
    p1_chem: u8
    p2_amount: u8
    p2_chem: u8
    rate: u8


@_SimpleClass
class BiochemistryEmitterGene:
    header: GeneHeader
    organ: u8
    tissue: u8
    locus: u8
    chemical: u8
    threshold: u8
    rate: u8
    gain: u8
    flags: u8


@_SimpleClass
class BiochemistryHalflivesGene:
    header: GeneHeader
    chemical_halflives: u8_256


@_SimpleClass
class BiochemistryInitialConcentrationGene:
    header: GeneHeader
    chemical: u8
    amount: u8


@_SimpleClass
class BiochemistryNeuroemitterGene:
    header: GeneHeader
    lobe0: u8
    neuron0: u8
    lobe1: u8
    neuron1: u8
    lobe2: u8
    neuron2: u8
    rate: u8
    chem0: u8
    amount0: u8
    chem1: u8
    amount1: u8
    chem2: u8
    amount2: u8
    chem3: u8
    amount3: u8


@_SimpleClass
class CreatureStimulusGene:
    header: GeneHeader
    stimulus: u8
    significance: u8
    input: u8
    intensity: u8
    features: u8
    chemical0: u8
    amount0: u8
    chemical1: u8
    amount1: u8
    chemical2: u8
    amount2: u8
    chemical3: u8
    amount3: u8


@_SimpleClass
class CreatureGenusGene:
    header: GeneHeader
    genus: u8
    mom: bytes32
    dad: bytes32


@_SimpleClass
class CreatureAppearanceGene:
    header: GeneHeader
    part: u8
    variant: u8
    species: u8


@_SimpleClass
class CreaturePoseGene:
    header: GeneHeader
    pose_number: u8
    pose_string: bytes16


@_SimpleClass
class CreatureGaitGene:
    header: GeneHeader
    gait: u8
    pose: u8_8


@_SimpleClass
class CreatureInstinctGene:
    header: GeneHeader
    lobe0: u8
    cell0: u8
    lobe1: u8
    cell1: u8
    lobe2: u8
    cell2: u8
    action: u8
    reinforcement_chemical: u8
    reinforcement_amount: u8


@_SimpleClass
class CreaturePigmentGene:
    header: GeneHeader
    pigment: u8
    amount: u8


@_SimpleClass
class CreaturePigmentBleedGene:
    header: GeneHeader
    rotation: u8
    swap: u8


@_SimpleClass
class CreatureFacialExpressionGene:
    header: GeneHeader
    expression: u8
    padding_always_zero: u8
    weight: u8
    drive0: u8
    amount0: u8
    drive1: u8
    amount1: u8
    drive2: u8
    amount2: u8
    drive3: u8
    amount3: u8


@_SimpleClass
class OrganGene:
    header: GeneHeader
    clockrate: u8
    damagerate: u8
    lifeforce: u8
    biotickstart: u8
    atpdamagecoefficient: u8


SVRULE3_OPCODES = {
    0: "stopImmediately",
    1: "blankOperand",
    2: "storeAccumulatorInto",
    3: "loadAccumulatorFrom",
    4: "ifEqualTo",
    5: "ifNotEqualTo",
    6: "ifGreaterThan",
    7: "ifLessThan",
    8: "ifGreaterThanOrEqualTo",
    9: "ifLessThanOrEqualTo",
    10: "ifZero",
    11: "ifNonZero",
    12: "ifPositive",
    13: "ifNegative",
    14: "ifNonNegative",
    15: "ifNonPositive",
    16: "add",
    17: "subtract",
    18: "subtractFrom",
    19: "multiplyBy",
    20: "divideBy",
    21: "divideInto",
    22: "minIntoAccumulator",
    23: "maxIntoAccumulator",
    24: "setTendRate",
    25: "tendAccumulatorToOperandAtTendRate",
    26: "negateOperandIntoAccumulator",
    27: "loadAbsoluteValueOfOperandIntoAccumulator",
    28: "getDistanceTo",
    29: "flipAccumulatorAround",
    30: "noOperation",
    31: "setToSpareNeuron",
    32: "boundInZeroOne",
    33: "boundInMinusOnePlusOne",
    34: "addAndStoreIn",
    35: "tendToAndStoreIn",
    36: "doNominalThreshold",
    37: "doLeakageRate",
    38: "doRestState",
    39: "doInputGainLoHi",
    40: "doPersistence",
    41: "doSignalNoise",
    42: "doWinnerTakesAll",
    43: "doSetSTtoLTRate",
    44: "doSetLTtoSTRateAndDoWeightSTLTWeightConvergence",
    45: "storeAbsInto",
    46: "ifZeroStop",
    47: "ifNZeroStop",
    48: "ifZeroGoto",
    49: "ifNZeroGoto",
    50: "divideAndAddToNeuronInput",
    51: "mulitplyAndAddToNeuronInput",
    52: "gotoLine",
    53: "ifLessThanStop",
    54: "ifGreaterThanStop",
    55: "ifLessThanOrEqualStop",
    56: "ifGreaterThanOrEqualStop",
    57: "setRewardThreshold",
    58: "setRewardRate",
    59: "setRewardChemicalIndex",
    60: "setPunishmentThreshold",
    61: "setPunishmentRate",
    62: "setPunishmentChemicalIndex",
    63: "preserveVariable",
    64: "restoreVariable",
    65: "preserveSpareVariable",
    66: "restoreSpareVariable",
    67: "ifNegativeGoto",
    68: "ifPositiveGoto",
}

SVRULE3_OPERAND_TYPES = {
    0: "accumulator",
    1: "inputNeuron",
    2: "dendrite",
    3: "neuron",
    4: "spareNeuron",
    5: "random",
    6: "chemicalIndexedBySourceNeuronId",
    7: "chemical",
    8: "chemicalIndexedByDestinationNeuronId",
    9: "zero",
    10: "one",
    11: "value",
    12: "negativeValue",
    13: "valueTen",
    14: "valueTenth",
    15: "valueInt",
}


def svrule3_from_bytes(data):
    if len(data) != 48:
        raise ValueError(
            "Expected length of data to be 48, but got {}".format(len(data))
        )
    value = []
    for i in range(0, 48, 3):
        opcode = SVRULE3_OPCODES.get(data[i], data[i])
        operandtype = SVRULE3_OPERAND_TYPES.get(data[i + 1], data[i + 1])
        operand = data[i + 2]
        value.append(f"{opcode}:{operandtype}:{operand}")
        while value and value[-1] == "stopImmediately:accumulator:0":
            value.pop()
    return value


def read_gen3_file(fname_or_stream):
    with open_if_not_stream(fname_or_stream, "rb") as original_f:
        f = better_peekable_stream(original_f)

        magic = read_exact(f, 4)
        if magic != b"dna3":
            raise ReadError(
                "Expected file magic to be b'dna3', but got {}".format(magic)
            )

        genes = []
        while True:

            unknown_data = b""
            while peek_exact(f, 4) not in (b"gene", b"gend"):
                unknown_data += read_exact(f, 1)
            if unknown_data:
                gene = NonGeneData()
                gene.data = unknown_data
                genes.append(gene)

            marker = read_exact(f, 4)
            if marker == b"gend":
                break

            header = GeneHeader()
            header.type = read_u8(f)
            header.subtype = read_u8(f)
            header.id = read_u8(f)
            header.generation = read_u8(f)
            header.switchontime = read_u8(f)
            header.flags = read_u8(f)
            # >=C2
            header.mutability = read_u8(f)
            # >=C3
            header.variant = read_u8(f)

            gene = {
                (0, 0): BrainLobeGene,
                (0, 1): BrainOrganGene,
                (0, 2): BrainTractGene,
                (1, 0): BiochemistryReceptorGene,
                (1, 1): BiochemistryEmitterGene,
                (1, 2): BiochemistryReactionGene,
                (1, 3): BiochemistryHalflivesGene,
                (1, 4): BiochemistryInitialConcentrationGene,
                (1, 5): BiochemistryNeuroemitterGene,
                (2, 0): CreatureStimulusGene,
                (2, 1): CreatureGenusGene,
                (2, 2): CreatureAppearanceGene,
                (2, 3): CreaturePoseGene,
                (2, 4): CreatureGaitGene,
                (2, 5): CreatureInstinctGene,
                (2, 6): CreaturePigmentGene,
                (2, 7): CreaturePigmentBleedGene,
                (2, 8): CreatureFacialExpressionGene,
                (3, 0): OrganGene,
            }.get((header.type, header.subtype), UnknownGene)()
            gene.header = header

            for key, typ in gene.__annotations__.items():
                if key == "header":
                    continue
                if typ == u8:
                    value = read_u8(f)
                elif typ == u8_8:
                    value = []
                    for _ in range(8):
                        value.append(read_u8(f))
                elif typ == u8_256:
                    value = []
                    for _ in range(256):
                        value.append(read_u8(f))
                elif typ == u16be:
                    value = read_u16be(f)
                elif typ == padding5:
                    value = read_exact(f, 5)
                    if value != b"\0" * 5:
                        raise ReadError(
                            "Expected padding to be zeros, but got {}".format(value)
                        )
                elif typ == padding7:
                    value = read_exact(f, 7)
                    if value != b"\0" * 7:
                        raise ReadError(
                            "Expected padding to be zeros, but got {}".format(value)
                        )
                elif typ == bytes4:
                    value = read_exact(f, 4)
                elif typ == bytes16:
                    value = read_exact(f, 16)
                elif typ == bytes32:
                    value = read_exact(f, 32)
                elif typ == svrule48:
                    value = svrule3_from_bytes(read_exact(f, 48))
                elif typ == bytes:
                    value = b""
                    while peek_exact(f, 4) not in (b"gene", b"gend"):
                        value += read_exact(f, 1)
                else:
                    raise NotImplementedError(typ.__name__)
                if typ.__supertype__ != padding:
                    setattr(gene, key, value)

            if isinstance(gene, UnknownGene):
                raise NotImplementedError(gene)
            genes.append(gene)

    return genes
