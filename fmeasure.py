import mir_eval as mir
import sys

def main():
    ref_intervals, ref_pitches = mir.io.load_valued_intervals(sys.argv[1])
    est_intervals, est_pitches = mir.io.load_valued_intervals(sys.argv[2])
    scores = mir.transcription.evaluate(ref_intervals, ref_pitches, est_intervals, est_pitches)
    print("| COn     | " + str(round(scores['Onset_F-measure'], 3)) + ' |')
    print("| COnP    | " + str(round(scores['F-measure_no_offset'], 3)) + ' |')
    print("| COnPOff | " + str(round(scores['F-measure'], 3)) + ' |')

if __name__ == "__main__":
    main()
