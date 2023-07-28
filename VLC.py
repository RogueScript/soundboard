import vlc

def play_audio(filename):
    # create vlc instance
    instance = vlc.Instance()
    #create player instance
    player = instance.media_player_new()
    #get the provided media files data
    media = instance.media_new(filename)
    #give the media data to the player to play
    player.set_media(media)
    # set the start volume, while the doc states val is from 0 to 100, I found that it can go higher, and even 100 is low for my case
    player.audio_set_volume(50*2)
    player.play()
    #return the player instance back
    return player

def pause_audio(player):
    player.pause()

def resume_audio(player):
    player.play()

def set_Volume(player, value):
    player.audio_set_volume(value*2)
    
def stop_audio(player):
    player.stop()



