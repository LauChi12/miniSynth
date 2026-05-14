
import os 
import wave
import struct
from score_linter import ScoreValidator #I did this for funsies - ask me more

"""
Section 0: set universal variables
"""
BPM = 120
SAMPLE_RATE = 44100


class Note: 
    """
    SECTION 1 - create a Note object from the imported file. 

    Functions: 
    1) parse_note
        This function iterates through a note_string that was opened in load_score, which has to come first in the list of function calls in main(). It parses the note string and creates a self.pitch and a self.duration that later functions use. 
    2) to_frequency
        This function uses the pitch string created in parse_note and compares it to the dictionary note_offset. Once it gets that value, it is able to calculate the intended frequency of the note and creates a self.frequency. 
    3) to_samples
        This function is identical in structure to to_frequency, except that it calculates the number of samples from the duration and creates self.duration 
    4) generate_wave
        This function takes self.frequency and self.samples and creates a n-length list, where n = # samples. From there, it appends each sample to a wave list, creating a single note of music. You could export to WAV at this point, but you're not getting a song. 
    """

    def __init__(self, note_string):
        self.note_string = note_string #we will read the score note by note and parse as we go
        self.pitch = None #intially set these to None and then parse_note does the rest
        self.duration = None

    def parse_note(self):
        #set pitch and duration empty first; we'll get that info in a moment
        pitch = "" 
        duration = ""
        found_digit = False #set it to false, then once we find the number, we set it to true! There will ALWAYS be a number in a note(it indicates octave)
        
        for i in self.note_string: #iterate through the INDIVIDUAL note string. Example: C4Q
            if found_digit: #have we gotten to the number yet? 
                duration += i #if yes, this is a part of the duration(note: duration will NEVER be a number) 
            elif i.isdigit(): 
                pitch += i #the number indicates octave, so it's part of the pitch notation 
                found_digit = True #and set it to true so we can start building duration 
            else: #this will be the first and/or second iteration of the note_string 
                pitch += i #and that means it's part of the pitch notation
        self.pitch = pitch #used in to_frequency
        self.duration = duration #used in to_samples

    def to_frequency(self):
        #note_offset is a dictionary designed to calculate the semitone difference between A and each note in an octave. If A=0, then C is 9 steps away. A is the standard 'central' point in musical theory, specifically A4 = 440hz. 
        note_offset = {"C": -9, "C#": -8,"D": -7,"D#": -6,"E": -5, "F": -4,"F#": -3,"G": -2, "G#": -1, "A": 0, "A#": 1,"B": 2 } 
        noteName = "" #keep it blank, write into it
        if self.pitch == "R0":
            self.frequency = 0 #there's no frequency if there's a rest! 
            return self.frequency
        noteOctave = 0 #assume it's at the 0th octave until proven otherwise
        for i in self.pitch: #iterate through self.pitch as created in parse_note
            if i.isdigit(): #if it's a number 
                noteOctave = i #set octave to whatever number it says it's at.
            else:
                noteName += i #else just add it to noteName
        if noteName not in note_offset: 
            raise ValueError(f"Invalid note name: {noteName}")
        n = note_offset[noteName] + (int(noteOctave) - 4) * 12 #get the value of n for the frequency calculation below
        self.frequency = 2**(n/12)*440 #and calculate frequency using 440hz(the frequency of A4) as a standard measurement
                

    def to_samples(self):
        #duration_to_beats is a library that maps the duration notation to a beat length. If we assume 4/4 time for all scores(which we are), then a quarter note = 1 beat. from there we can show how many beats in all the possible note durations in a score. 
        duration_to_beats = {"W": 4, "DH": 3, "H": 2, "DQ": 1.5, "Q": 1, "DE": .75 , "E": .5, "DS": 0.375, "S": .25}
        if self.duration not in duration_to_beats:
            raise ValueError(f"Invalid duration: {self.duration}")
        self.samples = int(duration_to_beats[self.duration] * (SAMPLE_RATE*60/BPM)) #beats are used to create samples. Because frequency is a float, I cast it to int so we're not creating partial waves in generate_wave. I am using a global standard BPM and SAMPLE_RATE variables that work for most songs. 

    def generate_wave(self): #now we create the values that will read into the actual WAV file
        wave = [] #append to a blank list
        if self.frequency == 0: #if the frequency is 0 (if it's a rest)
            wave = [0] * self.samples #add as many 0s to the list as there are samples
            self.wave = wave #and call it a wave
            return wave 
        cycle_length = SAMPLE_RATE/self.frequency #next we need to know how long our wave cycle is. You can get this by dividing the number of samples per second and the number of cycles per second. 
        #But wait, what's a cycle? For our purposes it's the length of the wave, ie: how many 1s and -1s in a single group of -1s and 1s. 
        for i in range(self.samples): #iterate through all samples generated so far
            if i % cycle_length < (cycle_length/2): #we determine if it's at the beginning half or end half of the cycle
                wave.append(1) #it's at the beginning, wave value = 1
            else: 
                wave.append(-1) #if it's at the end, wave value = -1
                #note: this method produces SQUARE WAVES only. We'd need more complex math here to create more complicated sounds. As it is, we are getting a simple NES-style beep boop sound. 
        self.wave = wave #and when we are done appending, we should have tens of thousands of digits in a list called wave for the build_waveform function. We need to do this for each note. 

            


class Song: 
    """
    SECTION 2 - create a Song object from the by iterating over the Note objects created above.

    Functions: 
    1) load_score:
        This function opens the file specified in main(), reads w/o printing, splits each line into a 'bar'(aka measure) and each bar into notes. Then as long as there are notes in the bar, it iterates over the bar using the functions in Note. 
    2) build_waveform:
        This function iterates over the list of waves that were created in generate_wave. Since the bass and treble lines were separated in load_score, we can create those two waveforms independently, creating a treble wave and a bass wave(if one exists). 
    3) mix_channels: 
        This function takes the waveforms above and literally adds them together using a zip function. It then normalizes each channel and adds them together in self.mixed_wave. 
    4) export_wav:
        This function takes self.mixed_wave and using the 'wave' and 'struct' modules, writes an empty WAV file using 'wave', break down mixed_wave into 16-bit binary data that a WAV file can read using 'struct', and packages it all up using 'wave' again. 
    """

    def __init__(self): #these are the things that exist in a Song object. For the purposes of outputting to a WAV file, we only need self.mixed_wave; the others are intermediary forms for building waveforms and mixing. 
        self.treble_notes = [] 
        self.bass_notes = []
        self.treble_wave = [] 
        self.bass_wave = []
        self.mixed_wave = []

    def load_score(self, filepath):
        score = open(os.path.join(os.path.dirname(__file__), filepath), encoding='utf-8', errors='ignore') #At the end of the day I probably could have just opened it, but it kept on crashing on hidden characters in the .txt file, so I just had it only read UTF-8 characters and ignore anything that is invisible. 
        content = score.read() #read file, do not display
        score.close() #close it before we accidentally change anything! 
        if not "---" in content: 
            bars = content.split("\n") #in this score, each line is a bar in 4/4 time. 
            for bar in bars: 
                notes = bar.split(" ") #notes are split by spaces.
                for note in notes:
                    if len(note) > 0: #if the note object is longer than 1 character(minimum 3) IDEA FOR TESTING: make minimum 3 and throw error if 2 or 1
                        note = Note(note) #make a note object
                        note.parse_note() #then parse it
                        note.to_frequency() #then get a frequency value
                        note.to_samples() #and a duration value
                        note.generate_wave() #from that you can generate the wave list for this note
                        self.treble_notes.append(note) #and add it to all the other note values. A waveform just needs one long list of waveform values, no need to keep notes separated from each other anymore. Now note is a super long list of -1 and 1s repeated over and over again! 

        else: 
            section = content.split("---") #this is the line that separates each channel
            treble = section[0] #first channel is treble
            bass = section[1] #second is bass
            bars = treble.split("\n") #in this score, each line is a bar in 4/4 time. 
            for bar in bars: 
                notes = bar.split(" ") #notes are split by spaces.
                for note in notes:
                    if len(note) > 0: #if the note object is longer than 1 character(minimum 3) IDEA FOR TESTING: make minimum 3 and throw error if 2 or 1
                        note = Note(note) #make a note object
                        note.parse_note() #then parse it
                        note.to_frequency() #then get a frequency value
                        note.to_samples() #and a duration value
                        note.generate_wave() #from that you can generate the wave list for this note
                        self.treble_notes.append(note) #and add it to all the other note values. A waveform just needs one long list of waveform values, no need to keep notes separated from each other anymore. Now note is a super long list of -1 and 1s repeated over and over again! 

            bars = bass.split("\n") #now we repeat the process for the bass section!  
            for bar in bars: 
                notes = bar.split(" ") #it's exactly the same as the treble section
                for note in notes:
                    if len(note) > 0:
                        note = Note(note)
                        note.parse_note()
                        note.to_frequency()
                        note.to_samples()
                        note.generate_wave()
                        self.bass_notes.append(note)
                    
    def build_waveform(self): #we can use self.note to create a waveform object we can export to WAV
        if len(self.bass_notes) != 0: #are there notes in the bass line? 
            for note in self.treble_notes: #iterate over note
                self.treble_wave = self.treble_wave + note.wave #add the lists together! They're the same thing now! 
            for note in self.bass_notes:
                self.bass_wave = self.bass_wave + note.wave
        else: 
            for note in self.treble_notes: 
                self.treble_wave = self.treble_wave + note.wave #only iterate over the treble line if there's no bass line


    def mix_channels(self):
        if len(self.bass_wave) != 0:
            for treble, bass in zip(self.treble_wave, self.bass_wave):
                self.mixed_wave.append((treble * 0.5) + (bass * 0.5))
            # I had a LOT ot trouble finding this - i was concatenating lists until i found the zip command. What does this do? zip creates a set of tuples at each index of bass and treble. Then the 'treble + bass for treble, bass' ensures that the values at each index are ADDED together. Each channel is multiplied by 0.5, making sure each summed value is still between -1 and 1 (square waves).
        else: 
            self.mixed_wave = self.treble_wave #no need to mix if there's no bass line - we just need the treble line. I thought it was more elegant than simply passing it. 

    def export_wav(self, filename):
        #ok this needs some walking-though. Despite what it looks like, this is the ONLY place where the 'wave' library is actually used. We also bring in the 'struct' library as well. I'll explain what they're doing.  

        #wave_open(file, mode ) = open a WAV file at the path indicated. The 'w' indicates that we're writing this file. The filename variable is passed from main as a string called 'output_filename'
        #So, to summarize, 'wave' is creating a new file called 'filename' to the current place you're working from 
        wav_file = wave.open(filename, 'w')

        #now we set a bunch of settings for the file before we write it
        wav_file.setnchannels(1) #while I'm technically doing two channels, they're both coming from all speakers at all times. No stereo here. 
        wav_file.setsampwidth(2) #we're acting on the wav_file object created above. 2 bytes per sample means I'm making good, old-fashioned 16-bit music 
        wav_file.setframerate(SAMPLE_RATE) #set the frame rate to the SAMPLE_RATE - otherwise it'll sound sped-up or slowed down. Like playing a 45 RPM record at a 78 or 33 1/3 RPM rate. 

        for sample in self.mixed_wave: #iterate through each sample in mixed_wave
            sample = int(sample * 32767) #that's a constant value and it has to be an int for packing into WAV form

            #here's how you break it all down into a wav-readable format:
            #struct.pack(format, object) = use the 'struct' module to convert python values to bytes. The '<h' indicates that we want it in 16-bit binary (h) in a certain format(<). This creates a huge set of binary data assigned to the variable 'packed_song'
            packed_song = struct.pack('<h', sample) 

            #and here's how you write the file: 
            #writeframe(data) = we're using the 'wave' module again to actually write the audio file using the data we packaged as 'packed_song'
            wav_file.writeframes(packed_song)
        wav_file.close() #and close


def main(): 
    """
    SECTION 3 - main function

    Create a workable UI with a way to choose which song to create, as well as display some fun facts about each song! 
    """

    print("Welcome! What song would you like to play?")
    print("Your options are: ")
    print("1: Doctor Who Theme")
    print("2: Alicia from Clair Obscur: Expedition 33 ")
    print("3: All Star by Smash Mouth")
    print("4: C-scale")

    validChoice = False
    while not validChoice: 
        decision = input("What would you like to listen to? (1,2,3,4)") 
        if decision in ["1","2","3","4"]:
            validChoice = True
        else: 
            print("I'm not sure what you meant. Try again!")

    if decision == "1":
        print("FUN FACT! The Doctor Who theme song was written and recorded in 1963, making it the first piece of electronic music recorded for television." "\n")
        song = Song()
        output_filename = "dw_theme_output.wav"
        validator = ScoreValidator()
        validator.validate("dw_theme.txt")
        song.load_score("dw_theme.txt")
        song.build_waveform()
        song.mix_channels()
        song.export_wav(output_filename)
        print(f"Your file has been saved as {output_filename}.")

    elif decision == "2":
        print("FUN FACT! The composer for Clair Obscur: Expedition 33 had never composed game music before! He was working as a guitar teacher before being hired to write the soundtrack for the game.", "\n")
        song = Song()
        output_filename = "alicia_output.wav"
        validator = ScoreValidator()
        validator.validate("alicia.txt")
        song.load_score("alicia.txt")
        song.build_waveform()
        song.mix_channels()
        song.export_wav(output_filename)
        print(f"Your file has been saved as {output_filename}.")

    elif decision == "3":
        print("FUN FACT! All Star was written for the 1999 movie 'Mystery Men', and NOT the 2001 movie 'Shrek'.", "\n")
        song = Song()
        output_filename = "all_star_output.wav"
        validator = ScoreValidator()
        validator.validate("all_star.txt")
        song.load_score("all_star.txt")
        song.build_waveform()
        song.mix_channels()
        song.export_wav(output_filename)
        print(f"Your file has been saved as {output_filename}.")

    elif decision == "4":
        song = Song()
        output_filename = "cscale_output.wav"
        validator = ScoreValidator()
        validator.validate("cscale.txt")
        song.load_score("cscale.txt")
        song.build_waveform()
        song.mix_channels()
        song.export_wav(output_filename)
        print(f"Your file has been saved as {output_filename}.")

if __name__ == "__main__":
    main()
