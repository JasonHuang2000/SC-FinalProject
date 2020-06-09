import mir_eval as mir
import sys

def main():
    ref_intervals, ref_pitches = mir.io.load_valued_intervals("MIR-ST500/" + sys.argv[1] + "/" + sys.argv[1] + "_groundtruth.txt")
    est_intervals, est_pitches = mir.io.load_valued_intervals(sys.argv[2])
    scores = mir.transcription.evaluate(ref_intervals, ref_pitches, est_intervals, est_pitches)
    print("===================")
    print("| COn     | " + str(round(scores['Onset_F-measure'], 3)))
    print("| COnP    | " + str(round(scores['F-measure_no_offset'], 3)))
    print("| COnPOff | " + str(round(scores['F-measure'], 3)))
    print("-------------------")
    print("Final Score: " + str(round(scores['Onset_F-measure']*0.2 + scores['F-measure_no_offset']*0.6 + scores['F-measure']*0.2, 3)))
    print("===================")

if __name__ == "__main__":
    main()
