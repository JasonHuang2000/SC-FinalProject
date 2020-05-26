import mir_eval as mir
import sys

def main():
    ref_intervals, ref_pitches = mir.io.load_valued_intervals(sys.argv[1])
    est_intervals, est_pitches = mir.io.load_valued_intervals(sys.argv[2])
    scores = mir.transcription.evaluate(ref_intervals, ref_pitches, est_intervals, est_pitches)
    print("Precision: " + str(scores['Precision']))
    print("Recall: " + str(scores['Recall']))
    print("F-measure: " + str(scores['F-measure']))

if __name__ == "__main__":
    main()
