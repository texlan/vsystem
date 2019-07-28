
# Library of known commands.

# startBatteries is sent at 9600 baud
startBatteries = bytes.fromhex('00 00 01 01 c0 74 0d 0a 00 00')

# Known commands are sent at 115200 baud.  The first byte is the module being queried (starting with 0x01). the value in
# cmds[#]['cmd'] is sent, then the checksum (which is a little endian version of the modbus crc algo), then \r\n
# respones follow a similar format.  They consist of the module #, then 2 bytes, then the fields displayed below, then
# a checksum and finally \r\n.   Because  "0D 0A" can show up in the data, you have to use a length to figure out the
# end of the transmission, hence the cmds[#]['rlen'].
cmds = {}
cmds[1] = {
    'name':'',
    'cmd': bytes.fromhex('03 00 EE 00 01'),
    # Fields:
    # <bat> 03 02 <2.?>
    # Runs each time you switch batteries.
    'rlen': 9,
}

cmds[2] = {
    'name':'',
    'cmd': bytes.fromhex('05 00 00 10'),
    # Fields:
    # <bat> 03 00 <2.?> <2.?>
    # Runs each time you switch batteries.
    'rlen': 10,
}
cmds[3] = {
    'name':'',
    'cmd': bytes.fromhex('05 00 00 08'),
    # Fields:
    # <bat> 03 00 <2.?> <2.?>
    # Only runs once when diag starts reading, regardless of switching batteries.
    'rlen': 10,
}
cmds[4] = {
    'name':'voltage',
    'cmd': bytes.fromhex('03 00 45 00 09'),
    # fields:      0         1        2                    3      4      5      6      7
    # <bat> 03 12 <2.highV> <2.lowV> <2.uncalbatvoltage?> <2.v1> <2.v2> <2.v3> <2.v4> <4 remaining octets, probably cell 5 and 6>
    'rlen': 25,
}
cmds[5] = {
    'name': 'temp',
    'cmd': bytes.fromhex('03 00 50 00 07'),
    # fields:      0           1         2         3         4         5         6
    # <bat> 03 0E <2.PCBTemp> <2.Temp1> <2.Temp2> <2.Temp3> <2.Temp4> <2.Temp5> <2.Temp6>
    'rlen': 21,
}
cmds[6] = {
    'name': 'history',
    'cmd': bytes.fromhex('03 00 01 00 07'),
    # fields:      0               1     2                  3                  4     5                 6
    # <bat> 03 0E <2.MaxLifeTemp> <2.?> <2.MaxCellVoltage> <2.MinCellVoltage> <2.?> <2.OscFaultCount> <2.MemAccessFaultCount>
    'rlen': 21,
}
cmds[7] = {
    'name': 'counts',
    'cmd': bytes.fromhex('03 00 12 00 02'),
    # fields:      0                            1
    # <bat> 03 04 <2.ProbablyCalibrationCount> <2.ChargeDischargeCycleCnt>
    'rlen': 11,
}
cmds[8] = {
    'name': 'systembalancing',
    'cmd': bytes.fromhex('03 00 1E 00 01'),
    # fields:      0
    # <bat> 03 02 <2.?>
    'rlen': 9,
}
cmds[9] = {
    'name': 'unknown',
    'cmd': bytes.fromhex('03 00 21 00 02'),
    # fields:      0
    # <bat> 03 04 <2.?=14> <2.?>
    'rlen': 11,
}
cmds[10] = {
    'name': 'Current',
    'cmd': bytes.fromhex('03 00 6A 00 0C'),
    # fields:      0          1     2    3     4                       5                    6                        7                        8                    9     10    11
    # <bat> 03 18 <2.SoC.1%> <2.?> <2.? <2.?> <2.MaxDischargeCurrent> <2.MaxChargeCurrent> <2.IntraModBalanceCount> <2.InterModBalanceCount> <2.SocCalCorrection> <2.?> <2.?> <2.?>
    'rlen': 31,
}
cmds[11] = {
    'name': 'unknown',
    'cmd': bytes.fromhex('03 00 82 00 12'),
    # fields:      0-9              10                  12    13    14    15    16    17
    # <bat> 03 24 <2.?=0>*10fields <2.MaxCellVoltTime> <2.?> <2.?> <2.?> <2.?> <2.?> <2.?>
    'rlen': 43,
}
cmds[12] = {
    'name': 'unknown',
    'cmd': bytes.fromhex('03 00 39 00 0A'),
    # fields:      0     1     2     3     4     5     6     7                 8                                          9
    # <bat> 03 14 <2.?> <2.?> <2.?> <2.?> <2.?> <2.?> <2.?> <2.? current*.01> <2. temperature probably pcb tracks close> <2.BatteryVoltage>
    # field 6:
    # 16348 when no balance                       11111111011100
    # 15324 cell 3 balancing                      11101111011100
    # 13276 when cell 3 and 4 balancing           11001111011100
    # 12765 when cell 2 and 3 and 4 bal           11000111011101
    # 13277 when cell 3 and 4 bal                 11001111011101
    # 13277 cell 3 and 4 and 1                    11001011011101
    # so cell 1 is >> 8,
    # cell 2 is >> 9,
    #



    'rlen': 27,

}
cmds[13] = {
    'name': 'unknown',
    'cmd': bytes.fromhex('03 00 E0 00 16'),
    # fields:
    # Says Valence. Probably useless, Same for all batteries.
    'rlen': 51,

}
cmds[14] = {
    'name': 'unknown',
    'cmd': bytes.fromhex('03 00 5A 00 01'),
    # fields:
    # <bat> 03 02 <2.?>
    'rlen': 9,

}
