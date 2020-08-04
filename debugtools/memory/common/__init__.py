def read_all_mem(p):
    return p.read_bytes(p.process_base.lpBaseOfDll, 34148352)


def memory_find(data, memdump):
    i = memdump.find(data)
    if i == -1:
        return []
    return [i]


def memory_findall(data, memdump):
    occurences = []
    i = 0

    i = memdump.find(data, i)

    while i != -1:
        occurences.append(i)
        i = memdump.find(data, i + 1)

    return occurences


section_lengths = {
    "1001": 160800,
    "1033": 160800,
    "1002": 160800,
    "1003": 321600,
    "1037": 80400,
    "1043": 80400,
    "1004": 160800,
    "1020": 80400,
    "1036": 160800,
    "1005": 80400,
    "1045": 80400,
    "1006": 80400,
    "1007": 160800,
    "1008": 160800,
    "1009": 160800,
    "1010": 160800,
    "1030": 80400,
    "1026": 160800,
    "1118": 80400,
    "1012": 160800,
    "1021": 160800,
    "1049": 80400,
    "1028": 80400,
    "1029": 80400,
    "1034": 256000,
    "1041": 256000,
    "1013": 1624000,
    "1014": 312000,
    "1038": 128000,
    "1015": 2920000,
    "1025": 696000,
    "1077": 10000,
    "1016": 1025000,
    "1017": 28,
    "1091": 1062748,
    "1022": 133524,
    "1023": 262608,
    "1024": 4,
    "1099": 200000,
    "1018": 4,
    "1019": 4,
    "1044": 4,
    "1031": 103200,
    "1035": 4,
    "1046": 4,
    "1074": 4,
    "1056": 4,
    "1057": 4,
    "1058": 100,
    "1059": 80,
    "1067": 28,
    "1061": 4,
    "1073": 200,
    "1062": 4,
    "1063": 45600,
    "1064": 32000,
    "1065": 100,
    "1040": 40016,
    "1042": 4,
    "1050": 4,
    "1052": 4,
    "1053": 4,
    "1054": 4,
    "1047": 4,
    "1048": 4,
    "1066": 4,
    "1068": 4,
    "1071": 4,
    "1072": 4,
    "1108": 4,
    "1109": 4,
    "1110": 4,
    "1076": 4,
    "1051": 4,
    "1093": 4,
    "1055": 4,
    "1078": 32,
    "1080": 4,
    "1081": 4,
    "1090": 4,
    "1082": 4,
    "1083": 80000,
    "1084": 4,
    "1095": 4,
    "1085": 14,
    "1086": 2,
    "1087": 2,
    "1088": 2,
    "1111": 2,
    "1112": 2,
    "1113": 2,
    "1089": 128,
    "1125": 1912,
    "1100": 36,
    "1101": 36,
    "1106": 4,
    "1079": 32,
    "1102": 14,
    "1103": 80400,
    "1104": 80400,
    "1105": 723600,
    "1107": 252504,
    "1114": 307200,
    "1115": 816,
    "1116": 4,
    "1117": 4,
    "1119": 4,
    "1120": 4,
    "1121": 36,
    "1122": 4,
    "1123": 4,
    "1124": 264,
    "1126": 4,
    "1127": 4,
    "1129": 4,
    "1130": 4,
    "1131": 4,
    "1132": 4,
    "1133": 4,
    "1134": 2000,
    "1135": 4000,
    "1136": 1
}

# memory_complete = process.read_bytes(process.process_base.lpBaseOfDll, 34148352)

# test
import struct

import random