import os

def main():
    for i in range (1, 3):
        os.chdir("AIcup_testset_ok/" + str(i))
        os.system("ls -l")
        stream = os.popen("cat " + str(i) + "_link.txt | head -n 1")
        link = stream.read();
        os.system("youtube-dl -x --audio-format mp3  -o \"audio.%(ext)s\" " + link)
        os.system("spleeter separate -i audio.mp3 -o audio_output")
        os.system("rm -f audio.mp3; ls -l")
        os.system("rm -rf audio_output; ls -l")
        os.chdir("../..")

if __name__ == "__main__":
    main()
