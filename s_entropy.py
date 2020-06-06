import sys
import json
from statistics import median
from statistics import mean

class Note:

    def __init__(self):
        self.onset = 0.0
        self.offset = 0.0
        self.pitch = 0

    def Onset(self, onset):
        self.onset = onset

    def Offset(self, offset):
        self.offset = offset

    def Pitch(self, pitch):
        self.pitch = pitch

    def Print(self):
        print(self.onset, self.offset, self.pitch, sep=' ')

def main(feature):

    features = json.load(open(feature))
    s_entrp = features['spectral_entropy']
    time = features['time']
    v_pitch = features['vocal_pitch']

    state = 0
    pitches = []
    notes = []
    sizz = len(s_entrp)

    for i in range(sizz):
        
        if state == 0 and s_entrp[i] < 0.65:
            state = 1
            note = Note()
            note.Onset(time[i])
        
        if state == 1:
            pitches.append(v_pitch[i])
            if i+1 < sizz and s_entrp[i+1] >= 0.65:
                note.Offset(time[i]) 
                note.Pitch(round(median(pitches)))
                if  note.pitch > 10 and note.onset != note.offset: 
                    notes.append(note)
                state = 0

    for note in notes:
        note.Print();

if __name__ == "__main__":  
    feature = sys.argv[1]
    main(feature)
