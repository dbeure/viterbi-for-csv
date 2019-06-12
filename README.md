# viterbi-for-csv
Simple Viterbi Algorithm for CSV files


This Viterbi works with CSV files, one for the emission probabilities, the other for the transition
probabilities. 

Arguments:
-t : file containing pretrained transition probabilities
-e : file containing pretrained emission probabilities
-o : file to write tagged sentences into, optional
-i : file containing tokenized sentences, or any sequence of states separated by an empty space
-first : if set to "True", the algorithm considers that the first element of the sequence
        is already known. It is considered its tag is the last column of the transmission file
-delim : delimiter of the CSV file, the default is set to "\t"

