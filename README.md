# viterbi-for-csv
Simple Viterbi Algorithm for CSV files<br />


This Viterbi works with CSV files, one for the emission probabilities, the other for the transition probabilities.<br /><br />

Arguments:<br />
-t : file containing pretrained transition probabilities<br />
-e : file containing pretrained emission probabilities<br />
-o : file to write tagged sentences into, optional<br />
-i : file containing tokenized sentences, or any sequence of states separated by an empty space<br />
-first : if set to "True", the algorithm considers that the first element of the sequence is already known. It is considered its tag is the last column of the transmission file<br />
-delim : delimiter of the CSV file, the default is set to "\t"<br />
<br />
Please take note that for the moment, this algorithm is not working :-)

