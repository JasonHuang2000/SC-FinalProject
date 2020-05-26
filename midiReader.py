import mido
import sys

class Info:

    def __init__(self, note_type, note, t):
        self.note_type = note_type
        self.note = note
        self.t = t

    def printInfo(self):
        print(self.note_type, self.t, self.note)


def main():

    mid = mido.MidiFile(sys.argv[1], clip=True)
    
    time = 0
    tempo = 0
    Infos = []
    
    for msg in mid.tracks[0]:
    
        if msg.type == "set_tempo":
            tempo = msg.tempo
        
        time += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
        
        if msg.type == 'note_on':
            Infos.append(Info(0, msg.note, time))
        elif msg.type == 'note_off':
            Infos.append(Info(1, msg.note, time))

    for i in range(len(Infos)):
        if Infos[i].note_type == 0:
            j = i+1
            while Infos[j].note != Infos[i].note:
                j += 1
            print('%f %f %d' % (Infos[i].t, Infos[j].t, Infos[i].note))


if __name__ == "__main__":
    main()
