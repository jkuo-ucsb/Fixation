# Fixation
Testing effect of pressure constraint of limited time on visual perception strategies

Fixation.py uses an EyeLink desktop eyetracker to read 100 images and display them in sections of 10 per trial. Eye movements are tracked 
written to events.hdf5.

FileReadingTargetSlice.py reads the events file along with coordFile.txt which stores the slice data of the visual target, along with 
its (X,Y) location. It then plots the saccades on the target slice, with differing sizes and opacity relative to fixation duration.  
