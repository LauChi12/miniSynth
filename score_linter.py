"""
SCORE LINTER - WHAT IS IT, WHAT DOES IT DO, AND WHAT IS IT DOING HERE? 

1) What is it? 
    Generally speaking a linter is a secondary function or class that provides some sort of validation on a program. It's designed to 'filter out the lint'. 

2) What does it do? 
    In this case, I have a program that relies on an accurately built input .txt file in a rudimentary DSL(domain specific language). In order for the output to not sound really weird, I need to ensure that the songs are in 4/4 time, since all my constants (BPM/SAMPLE_RATE) depend on that. 
    
    However, I don't trust that I'm not making mistakes with my musical notation. If I run a file with 6 beats in a bar, the program will accept it. And it should; the goal there is to parse notes in Notes and to build/export song objects in Song. I needed/wanted a grammar checker for this musical DSL. 

    In this case it breaks down the .txt input when it's called in main(). Rather than parsing the note and creating frequency and duration strings, it ONLY creates a duration string. Then it maps that duration value against the hardcoded dictionary and ultimately sums up each bar of music's beats. If it's 4, it passes. If it isn't 4, you get a helpful error message that tells you exactly how many beats there are in what bar, so you know exactly what to do. 

    If this didn't exist the main program would run w/o issue and create a WAV file, but the song would sound off because the time signature would be messed up. Think spell-checker but for music. :) 

3) What is it doing here? 
    There's two main reasons. The first is for practicality. I was having a LOT of issues transcribing the bass line 'Alicia' since it's in 6/8 time. I ended up axing the whole bass line as a result, but this tool stayed because it's cool. 
    The second reason is because I love the idea of building and parsing languages in general, from music to Old English to Klingon, and this allowed me to try that out in a PL capacity. 

"""


import os

DURATION_TO_BEATS = {"W": 4, "DH": 3, "H": 2, "DQ": 1.5, "Q": 1, "DE": .75, "E": .5, "DS": 0.375, "S": .25} #hardcoding the duration_to_beats dictionary from to_samples is the easiest way I found to  have these values in this file. I REALLY wanted to import just the dictionary filepath-style, but I couldn't get it to work. 

class ScoreValidator: 
    def validate(self, filepath):
        score = open(os.path.join(os.path.dirname(__file__), filepath), encoding='utf-8', errors='ignore') #If I don't do this the program cannot find a file even when they're in the same folder. 
        content = score.read() #read and close
        score.close() 
        if "---" in content: #now we start an abbreviated parse - looking only for duration values
            channels = content.split("---") #create a channels object by splitting at '---'
        else:
            channels = [content] #unless there's no '---'
        for channel in channels: #iterate through channels by calling the function below. 
            self.validate_bars(channel)
        
    def validate_bars(self, channel):
        bars = channel.split('\n') #now we keep on splitting. this time we're taking a single channel and splitting on a new line to create a set of bars
        bar_num = 0 #set it to 0 so we can track which bar we're working on(used for error reporting)
        for bar in bars:
            if len(bar.strip()) == 0 or bar.strip() == "---": #ignore it if the bar is a channel marker - otherwise you'll get an error message at that line. 
                continue 
            beats = 0 #set the number of beats to 0 before parse
            bar_num += 1 #but count which bar you're on
            notes = bar.split(" ") #now split bar into notes
            for note_string in notes: #we're iterating through notes now. I wonder how/if I could have done recursion here. 
                if len(note_string) > 0: #if we have ourselves a note(you should see some similarities here with load_score() and parse_note().)
                    duration = "" 
                    found_digit = False
                    for i in note_string:
                        if found_digit: 
                            duration += i
                        elif i.isdigit():
                            found_digit = True
                    if duration in DURATION_TO_BEATS: #look up and see if the duration we get is in the hardcoded dict above
                        beats += DURATION_TO_BEATS[duration]#add the value to beats
                        #should i do an error here? not sure 
            if beats != 4: #if we don't have 4 beats per bar (the reason for this file's existence)
                raise ValueError (f"Bar {bar_num} currently has {beats} number of beats instead of 4. Review the score before running laurensynth.py. ") #provide a helpful guide on what to fix in the score
            