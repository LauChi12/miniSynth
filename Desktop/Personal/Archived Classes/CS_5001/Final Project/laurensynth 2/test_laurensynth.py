import unittest

from laurensynth import Note, Song

class TestMakeNote(unittest.TestCase):
    def test_parseGoodNote(self): #test to see if a good note is parsed correctly
        note = Note("A4Q")
        expectedPitch = "A4"
        expectedDuration = "Q"
        reality = note.parse_note()
        self.assertEqual(expectedPitch, note.pitch)
        self.assertEqual(expectedDuration, note.duration)

    def test_parseRest(self): #is a rest parsed correctly? 
        note = Note("R0Q")
        expectedPitch = "R0"
        expectedDuration = "Q"
        reality = note.parse_note()
        self.assertEqual(expectedPitch, note.pitch)
        self.assertEqual(expectedDuration, note.duration)

    def test_parseBadNote1(self): #valid pitch, invalid duration
        note = Note("A4M")
        note.parse_note()
        note.to_frequency()
        with self.assertRaises(ValueError):
            note.to_samples()

    def test_parseBadNote2(self): #note has no number! 
        note = Note("AQ") 
        note.parse_note()
        with self.assertRaises(ValueError):
            note.to_frequency()
            note.to_samples()

    def test_parseBadNote3(self): #missing duration! 
        note = Note("A4")
        note.parse_note()
        note.to_frequency()
        with self.assertRaises(ValueError):
            note.to_samples()

    def test_parseBadNote4(self): #invalid pitch, valid duration
        note = Note("T4Q")
        note.parse_note()
        with self.assertRaises(ValueError):
            note.to_frequency()


    def test_to_frequency(self): #is the frequency calculating correctly? 
        note = Note("A4Q")
        expectedFrequency = 440
        note.parse_note()
        reality = note.to_frequency()
        self.assertEqual(expectedFrequency, note.frequency)

    def test_rest_frequency(self): #what about if it's a rest? 
        note = Note("R0Q")
        expectedFrequency = 0
        note.parse_note()
        reality = note.to_frequency()
        self.assertEqual(expectedFrequency, note.frequency)

    def test_to_samples(self): #are we getting the correct # of samples? 
        note = Note("A4Q")
        expectedSamples = 22050
        note.parse_note()
        note.to_frequency()
        reality = note.to_samples()
        self.assertEqual(expectedSamples, note.samples)

    def test_generate_wave(self): #are we getting the correct square wave values in our wave list? 
        note = Note("A4Q")
        expectedValues = {-1, 1}
        expectedLength = 22050
        note.parse_note()
        note.to_frequency()
        note.to_samples()
        note.generate_wave()
        self.assertTrue(all(i in expectedValues for i in note.wave)) #gotta get documentation
        self.assertEqual(expectedLength, len(note.wave))
    
    def test_mix_channels(self): #test to see if the mixing works! 
        test_song = Song()
        test_song.load_score("all_star.txt") #load a song with 2 channels
        test_song.build_waveform()
        test_song.mix_channels()
        self.assertEqual(705600, len(test_song.mixed_wave)) #I know there will 705600 samples in the all_star song(I did a print statement inside the main file earlier) so if it's working correctly it will create that many samples. 

    def test_load_score(self): #are we loading the score files correctly? 
        test_song = Song()
        test_song.load_score("cscale.txt")
        self.assertEqual(8, len(test_song.treble_notes)) #easiest to see how many notes there are - if it's 0, you know something's wrong with the way it's loading

    def test_build_waveform(self): #are we building the waveforms correctly? 
        test_song = Song()
        test_song.load_score("cscale.txt")
        test_song.build_waveform()
        self.assertEqual(176400, len(test_song.treble_wave)) #again, we know how long this should be, and that's a good way to tell if something went wrong in this function

if __name__ == "__main__":
    unittest.main()