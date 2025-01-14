'''
Translate a demo into humanly readable information.


based on aos_replay by BR
	https://github.com/BR-/aos_replay

Authors:
	VierEck.
	BR-
'''


from struct import unpack, calcsize


TRANSLATOR_VER   = 0
AOS_REPLAY_VER   = 1
AOS_PROTOCOL_VER = 3 #0.75

TOOL_IDs  = { 0: "spade", 1: "block", 2: "weap" , 3: "nade", }
WEAP_IDs  = { 0: "semi" , 1: "smg"  , 2: "pump" , }
BLOCK_IDs = { 0: "block", 1: "lmb"  , 2: "rmb"  , 3: "nade", }
KILL_IDs  = { 0: "body" , 1: "head" , 2: "melee", 3: "nade", 4: "fall", 5: "team", 6: "class", }

players    = {}
packets    = {}
pkt_filter = [ 2, 3, 4, ]
#recommended to filter worldupdate, inputdata and weapondata due to sheer amount of these packets in a demo.

def format_string(s):
	new_s = ""
	for i in range(len(s)):
		if s[i] in ("(", ")", "[", "]", "\\"):
			new_s += "\\"
		new_s += s[i]
	return new_s


def PositionData(data):
	x, y, z = unpack("fff", data[0:12])
	return ("00/PositionData     : (" + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")")
packets[0] = PositionData

def OrientationData(data):
	x, y, z = unpack("fff", data[0:12])
	return ("01/OrientationData  : (" + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")")
packets[1] = OrientationData

def WorldUpdate(data):
	info = ""
	i = 0
	j = -1
	while i < len(data):
		x, y, z, a, b, c = unpack("ffffff", data[i:i+24])
		i += 24
		j += 1
		for val in [x, y, z, a, b, c]:
			if val != 0:
				info += "(" + f"{j:02d}" + ")"
				info += "(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")"
				info += "(ori: " + f"{a:5.2f}" + ", " + f"{b:5.2f}" + ", " + f"{c:5.2f}" + "); "
				break
	return "02/WorldUpdate      : " + info
packets[2] = WorldUpdate

def InputData(data):
	pl_id = data[0]
	pl_info = f"{pl_id:02d}"
	if pl_id in players:
		pl_info += ": " + players[pl_id]
	inp_info = ""
	if data[1] & 0b00000001:
		inp_info += "up "
	if data[1] & 0b00000010:
		inp_info += "down "
	if data[1] & 0b00000100:
		inp_info += "left "
	if data[1] & 0b00001000:
		inp_info += "right "
	if data[1] & 0b00010000:
		inp_info += "jump "
	if data[1] & 0b00100000:
		inp_info += "crouch "
	if data[1] & 0b01000000:
		inp_info += "sneak "
	if data[1] & 0b10000000:
		inp_info += "sprint "
	return "03/InputData        : (" + pl_info + ")( " + inp_info + ")"
packets[3] = InputData

def WeaponInput(data):
	pl_id = data[0]
	pl_info = f"{pl_id:02d}"
	if pl_id in players:
		pl_info += ": " + players[pl_id]
	weap_info = ""
	if data[1] & 0b00000001:
		weap_info += "pri "
	if data[1] & 0b00000010:
		weap_info += "sec "
	return "04/WeaponInput      : (" + pl_info + ")( " + weap_info + ")"
packets[4] = WeaponInput

def SetHp(data):
	x, y, z = unpack("fff", data[2:14])
	info_Type = "fall" if not data[1] else "weap"
	return ("05/SetHp            : (hp: " + str(data[0]) + ")(type: " + info_Type
		+ ")(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")")
packets[5] = SetHp

def GrenadePacket(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	fuse, x, y, z, a, b, c = unpack("fffffff", data[1:29])
	return ("06/GrenadePacket    : (" + f"{pl_id:02d}" + pl_name + ")(fuse: " + str(fuse) 
		+ ")(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}"
		+ ")(vel: " + f"{a:5.2f}" + ", " + f"{b:5.2f}" + ", " + f"{c:5.2f}" + ")")
packets[6] = GrenadePacket

def SetTool(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return "07/SetTool          : (" + f"{pl_id:02d}" + pl_name + ")(tool: " + TOOL_IDs[data[1]] + ")"
packets[7] = SetTool

def SetColor(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return ("08/SetColor         : (" + f"{pl_id:02d}" + pl_name 
		+ ")(color: " + str(data[3]) + ", " + str(data[2]) + ", " + str(data[1]) + ")")
packets[8] = SetColor	

def ExistingPlayer(data):
	pl_id = data[0]
	decode_name = format_string(data[11:-1].decode("cp437", "replace"))
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	players[pl_id] = decode_name
	kills = unpack("I", data[4:8])[0]
	return ("09/ExistingPlayer   : (" + f"{pl_id:02d}" + pl_name + ")(team: " + str(data[1]) 
		+ ")(weap: " + WEAP_IDs[data[2]] + ")(tool: " + TOOL_IDs[data[3]] + ")(kills: " + str(kills)
		+ ")(color: " + str(data[10]) + ", " + str(data[9]) + ", " + str(data[8]) + ")"
		+ "(name: " + decode_name + ")")
packets[9] = ExistingPlayer

def ShortPlayer(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return ("10/ShortPlayer      : (" + f"{pl_id:02d}" + pl_name 
		+ ")(team: " + str(data[1]) + ")(weap: " + WEAP_IDs[data[2]] + ")")
packets[10] = ShortPlayer

def MoveObject(data):
	x, y, z = unpack("fff", data[2:14])
	return ("11/MoveObject       : (obj: " + str(data[0]) + ")(team: " + str(data[1]) 
		+ ")(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")")
packets[11] = MoveObject

def CreatePlayer(data):
	pl_id = data[0]
	decode_name = format_string(data[15:-1].decode("cp437", "replace"))
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	players[pl_id] = decode_name
	x, y, z = unpack("fff", data[3:15])
	return ("12/CreatePlayer     : (" + f"{pl_id:02d}" + pl_name 
		+ ")(weap: " + WEAP_IDs[data[1]] + ")(team: " + str(data[2])
		+ ")(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")(name: " + decode_name + ")")
packets[12] = CreatePlayer

def BlockAction(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	x, y, z = unpack("III", data[2:14])
	return ("13/BlockAction      : (" + f"{pl_id:02d}" + pl_name + ")(action: " + BLOCK_IDs[data[1]]
		+ ")(pos: " + str(x) + ", " + str(y) + ", " + str(z) + ")")
packets[13] = BlockAction

def BlockLine(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	x, y, z, a, b, c = unpack("IIIIII", data[1:25])
	return ("14/BlockLine        : (" + f"{pl_id:02d}" + pl_name
		+ ")(start: " + str(x) + ", " + str(y) + ", " + str(z) 
		+ ")(end: " + str(a) + ", " + str(b) + ", " + str(c) + ")")
packets[14] = BlockLine

def CTFState(data):
	info = ""
	if data[3] & 0b00000001:
		pl_id = data[4]
		pl_name = ""
		if pl_id in players:
			pl_name = ": " + players[pl_id]
		info += "(player1: " + f"{pl_id:02d}" + pl_name + ")"
	else:
		x, y, z = unpack("fff", data[4:16])
		info += "(pos1: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")"
	if data[3] & 0b00000010:
		pl_id = data[16]
		pl_name = ""
		if pl_id in players:
			pl_name = ": " + players[pl_id]
		info += "(player2: " + f"{pl_id:02d}" + pl_name + ")"
	else:
		x, y, z = unpack("fff", data[16:28])
		info += "(pos2: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")"
	x1, y1, z1, x2, y2, z2 = unpack("ffffff", data[28:52])
	return ("(score1: " + str(data[0]) + ")(score2: " + str(data[1]) + ")(limit: " + str(data[2]) + ")" + info
		+ "(base1: " + f"{x1:5.2f}" + ", " + f"{y1:5.2f}" + ", " + f"{z1:5.2f}"
		+ ")(base2: " + f"{x2:5.2f}" + ", " + f"{y2:5.2f}" + ", " + f"{z2:5.2f}" + ")")

def TCState(data):
	info = ""
	i = 1
	while i < len(data):
		x, y, z = unpack("fff", data[i:i+12])
		info += "(team: " + str(data[i+12]) + ")"
		info += "(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + "); "
		i += 13
	return "(terrs: " + str(data[0]) + "): " + info + ")"

GAME_STATEs = { 0: CTFState, 1: TCState, }

def StateData(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	game_mode = "ctf"
	if data[30] > 0:
		game_mode = "tc"
	team1_name = format_string(data[10:20].decode("cp437", "replace"))
	team2_name = format_string(data[20:30].decode("cp437", "replace"))
	return ("15/StateData        : (" + f"{pl_id:02d}" + pl_name
		+ ")(fog: " + str(data[3]) + ", " + str(data[2]) + ", " +  str(data[1])
		+ ")(team1: " + str(data[6]) + ", " + str(data[5]) + ", " +  str(data[4])
		+ ")(team2: " + str(data[9]) + ", " + str(data[8]) + ", " +  str(data[7])
		+ ")(team1: " + "".join(team1_name) + ")(team2: " + "".join(team2_name) 
		+ ")(mode: " + game_mode + ")" + GAME_STATEs[data[30]](data[31:]))
packets[15] = StateData

def KillAction(data):
	victim_id = data[0]
	victim_name = ""
	if victim_id in players:
		victim_name = ": " + players[victim_id]
	killer_id = data[1]
	killer_name = ""
	if killer_id in players:
		killer_name = ": " + players[killer_id]
	return ("16/KillAction       : (victim: " + f"{victim_id:02d}" + victim_name 
		+ ")(killer: " + f"{killer_id:02d}" + killer_name 
		+ ")(type: " + KILL_IDs[data[2]] + ")(respawn: " + str(data[3]) + ")")
packets[16] = KillAction

def ChatMessage(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	chat_type = "global"
	if data[1] == 1:
		chat_type = "team"
	elif data[1] == 2:
		chat_type = "sys"
	msg = format_string(data[2:-1].decode("cp437", "replace"))
	return ("17/ChatMessage      : (" + f"{pl_id:02d}" + pl_name + 
		")(" + chat_type + ")(" + "".join(msg) + ")")
packets[17] = ChatMessage

def MapStart(data):
	size = unpack("I", data)
	return "18/MapStart         : (size: " + str(size[0]) + ")"
packets[18] = MapStart

def MapChunk(data):
	return "19/MapChunk         : (size: " + str(len(data)) + ")"
packets[19] = MapChunk

def PlayerLeft(data):
	pl_info = "(player doesnt exist)"
	pl_id = data[0]
	if pl_id in players:
		pl_info = "(" + f"{pl_id:02d}" + ": " + players[pl_id] + ")"
		del players[pl_id]
	return "20/PlayerLeft       : " + pl_info
packets[20] = PlayerLeft

def TerritoryCapture(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	win = "win"
	if data[2] < 1:
		win = "lose"
	return ("20/TerritoryCapture : (" + f"{pl_id:02d}" + pl_name 
		+ ")(obj: " + str(data[1]) + ")(" + win + ")(team: " + str(data[3]) + ")")
packets[21] = TerritoryCapture

def ProgressBar(data):
	rate, progress = unpack("bf", data[2:7])
	return ("21/ProgressBar      : (obj: " + str(data[0]) + ")(team: " + str(data[1]) 
		+ ")(rate: " + str(rate) + ")(progress: " + "{:5.2f}".format(progress * 100) + "%)")
packets[22] = ProgressBar

def IntelCapture(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	win = "win"
	if data[1] < 1:
		win = "lose"
	return "23/IntelCapture     : (" + f"{pl_id:02d}" + pl_name + ")(" + win + ")"
packets[23] = IntelCapture

def IntelPickup(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return "24/IntelPickup      : (" + f"{pl_id:02d}" + pl_name + ")"
packets[24] = IntelPickup

def IntelDrop(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	x, y, z = unpack("fff", data[1:13])
	return ("25/IntelDrop        : (" + f"{pl_id:02d}" + pl_name 
		+ ")(pos: " + f"{x:5.2f}" + ", " + f"{y:5.2f}" + ", " + f"{z:5.2f}" + ")")
packets[25] = IntelDrop

def Restock(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return "26/Restock          : (" + f"{pl_id:02d}" + pl_name + ")"
packets[26] = Restock

def FogColor(data):
	return ("27/FogColor         : " 
		+ "(fog: " + str(data[3]) + ", " + str(data[2]) + ", " + str(data[1]) + ", " + str(data[0]) + ")")
packets[27] = FogColor

def WeaponReload(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return ("28/WeaponReload     : (" + f"{pl_id:02d}" + pl_name 
		+ ")(mag: " + str(data[1]) + ")(reserve: " + str(data[2]) + ")")
packets[28] = WeaponReload

def ChangeTeam(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return "29/ChangeTeam       : (" + f"{pl_id:02d}" + pl_name + ")(team: " + str(data[1]) + ")"
packets[29] = ChangeTeam

def ChangeWeapon(data):
	pl_id = data[0]
	pl_name = ""
	if pl_id in players:
		pl_name = ": " + players[pl_id]
	return "30/ChangeWeapon     : (" + f"{pl_id:02d}" + pl_name + ")(weap: " + WEAP_IDs[data[1]] + ")"
packets[30] = ChangeWeapon

def HandshakeInit(data):
	return "31/HandshakeInit    : (" + str(int(unpack("I", data)[0])) + ")"
packets[31] = HandshakeInit

def HandshakeResponse(data):
	return "32/HandshakeResponse: (" + str(int(unpack("I", data)[0])) + ")"
packets[32] = HandshakeResponse

def VersionGet(data):
	return "33/VersionGet"
packets[33] = VersionGet

def VersionResponse(data):
	major   = unpack("b", data[1])
	minor   = unpack("b", data[2])
	rev1    = unpack("b", data[3])
	rev2    = unpack("b", data[4])
	os_info = data[5:].decode("cp437", "replace")
	return ("34/VersionResponse  : (client: " + data[0].decode("cp437", "replace")
		+ ")(ver: " + str(major) + "." + str(minor) + "." + str(rev1) + str(rev2) + ")(os: " + os_info + ")")
packets[34] = VersionResponse

def ProtocolExtension(data):
	info = "(size: " + str(data[0]) + ")"
	i = 1
	while i + 1 < len(data):
		info += "(" + str(data[i]) + ", " + str(data[i + 1]) + ")"
		i += 2
	return ("60/ProtocolExtension: " + info)
packets[60] = ProtocolExtension


def translate(file_name):
	with open(file_name, "rb") as of:
		if of.read(1)[0] != AOS_REPLAY_VER:
			return "wrong aos_replay version"
		if of.read(1)[0] != AOS_PROTOCOL_VER:
			return "wrong aos protocol version"
		with open(file_name + ".txt", "w", encoding="cp437") as nf:
			nf.write("demo translator version: " + str(TRANSLATOR_VER) + "\n")
			nf.write("aos_replay version     : " + str(AOS_REPLAY_VER) + "\n")
			nf.write("aos protocol version   : " + str(AOS_PROTOCOL_VER) + "\n")
			time = 0
			while True:
				fmt = "fH"
				fmtlen = calcsize(fmt)
				meta = of.read(fmtlen)
				if len(meta) < fmtlen:
					break
				dt, size = unpack(fmt, meta)
				time += dt
				data = of.read(size)
				pkt_id = data[0]
				if pkt_id in pkt_filter:
					continue
				nf.write("[" + "{:015.4f}".format(time))
				pkt = ""
				try:
					pkt = ": " + packets[pkt_id](data[1:])
				except KeyError:
					print("packet not recognised: " + str(pkt_id))
				nf.write(pkt)
				nf.write("]\n")
			nf.close()
		of.close()
	return "task succesful"

if __name__ == "__main__":
	from os import path
	from argparse import ArgumentParser
	
	parser = ArgumentParser(description="Translate a demo into text")
	parser.add_argument("file", help="File to read from")
	args = parser.parse_args()
	
	if path.exists(args.file):
		print(translate(args.file))
	else:
		print("no such file exists")
