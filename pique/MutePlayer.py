'''
Command to not receive messages from a specific player. 
the message from that player is still sent to everyone else, just not to you.

This script is to be put high on the script hirarchie, above all
other scripts that overwrite on_chat or on_chat_message_recieved.

Authors:
	VierEck.
'''


from piqueserver.commands import command, target_player
from pyspades.contained import ChatMessage
from pyspades.constants import CHAT_ALL, CHAT_TEAM


@command("playermute", "pmute") #having the player/p part first might make typos less likely i think?
@target_player                  #staff should be careful nonetheless to not confuse this with /mute
def p_mute(c, pl):
	p = c.protocol
	if c is pl:
		#this may be a small concern, since it could be easy to misclick and send the 
		#command without args and unmute everyone without it being your intention. 
		c.MutePlayer_muted = []
		return "#Everyone unmuted"
	if pl in c.MutePlayer_muted:
		c.MutePlayer_muted.remove(pl)
		return pl.name + " unmuted"
	c.MutePlayer_muted.append(pl)
	return pl.name + " muted."


def apply_script(pro, con, cfg):
	
	
	class MutePlayer_C(con):
		MutePlayer_muted = []
		
		def on_chat(c, msg, is_global):
			#copy paste latter half of on_chat_message_recieved from source. modified
			p = c.protocol
			msg = msg.replace('\n', '')
			chat_pkt = ChatMessage()
			chat_pkt.chat_type = CHAT_ALL if is_global else CHAT_TEAM
			chat_pkt.value     = msg
			chat_pkt.player_id = c.player_id
			for pl in p.players.values():
				if not pl.deaf and (is_global or c.team is pl.team):
					if c in pl.MutePlayer_muted:
						continue
					pl.send_contained(chat_pkt)
			c.on_chat_sent(msg, is_global)
			return False #hijacks both on_chat and on_chat_message_recieved
		
		def on_disconnect(c):
			p = c.protocol
			for pl in p.players.values():
				if c in pl.MutePlayer_muted:
					pl.MutePlayer_muted.remove(c)
			return con.on_disconnect(c)
	
	
	return pro, MutePlayer_C
