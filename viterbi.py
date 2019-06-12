#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#author: Debora Beuret


import csv
import math
from typing import TextIO
import nltk
import argparse
import sys
import numpy as np


class PretrainedHMM:
    def __init__(self, trans_probs: TextIO, emi_probs: TextIO, delimiter='\t'):  # IO object is what is return by "open"
        self.delim = delimiter
        trans = self.read_files(trans_probs)
        em = self.read_files(emi_probs)
        self.trans_matrix = trans[0]
        self.trans_row_i = trans[1]
        self.trans_col_i = trans[2]
        self.em_matrix = em[0]
        self.em_row_i = em[1]
        self.em_col_i = em[2]

    def read_files(self, filename):
        reader = csv.reader(filename, delimiter=self.delim, quotechar='|')
        #row_count = sum(1 for row in reader)
        i = 0
        row_index_dict = {}
        column_index_dict = {}
        all_probs = []
        for row in reader:
            if i == 0:
                for n in range(1, len(row)):
                    column_index_dict.update({row[n]:n-1})
            else:
                row_index_dict.update({row[0]:i-1})
                all_probs.append([math.log(float(row[x]), 2) for x in range(1, len(row))])
            i += 1
        the_matrix = np.array(all_probs)

        return the_matrix, row_index_dict, column_index_dict

    def tag_sent(self, tok_sent : str, with_first = False):
        sentence = tok_sent.split()
        #leaves me with a list of the words in the sentence, a list of "observations"
        #my tags are the 8 I have seen
        #access probs: p(O|BOS) = self.trans_matrix[self.trans_row_i['O]][self.trans_col_i['BOS]] = transBOS-O
        trans = self.trans_matrix
        em = self.em_matrix
        results = np.zeros((len(sentence), len(self.em_col_i)))  # elements x possible states
        results[:, :] = float('-inf')
        backpointers = np.zeros((len(sentence), len(self.em_col_i)), 'int')


        #base case, V = 1, no maximizing
        if with_first == True:
            first = getKeysByValue(self.trans_col_i, len(self.trans_col_i)-1)
            for i in range(len(self.em_col_i)):
                results[0, i] = self.em_matrix[self.em_row_i[sentence[0]]][i]+self.trans_matrix[i][self.trans_col_i[first]]+math.log(1, 2)
        #print(results)
        #results[0, :]
        else:
            for i in range(len(self.em_col_i)):
                results[0, i] = self.em_matrix[self.em_row_i[sentence[0]]][i]+math.log(1/len(self.em_col_i), 2)


        #rest of the sentence, recursive
        for t in range(1, len(sentence)):   #for all the words in the sentence
            for s2 in range(len(self.em_col_i)):#for all tags in this time step
                maxv = -1000000 #my maximized is set lower than could ever be
                best = None #no best index to give the backpointer yet
                for s1 in range(len(self.em_col_i)):    #for all tags in the previous time step
                    score = self.trans_matrix[s2][s1]+results[t-1][s1]
                    if score > maxv:
                        maxv = score
                        best = s1
                #results[t][s2] = self.em_matrix[self.em_row_i[sentence[t]]][s2]+self.trans_matrix[s2][best]+maxv
                results[t][s2] = self.em_matrix[self.em_row_i[sentence[t]]][s2]+maxv
                backpointers[t][s2] = best
        #print(results)

        #follow backpointers
        best_seq = []
        index_best = np.argmax(results[len(sentence)-1, :])
        for tag, index in self.em_col_i.items():
            if index == index_best:
                b_tag = tag
        best_seq.append(b_tag)
        for x in range(len(sentence)-1, 0, -1):
            best_i = backpointers[x][index_best]
            for tag, index in self.em_col_i.items():
                if index == best_i:
                    b_tag = tag
            best_seq.append(b_tag)
            index_best = best_i
        first = getKeysByValue(self.trans_col_i, len(self.trans_col_i)-1)
        best_seq.append(first)
        return list(reversed(best_seq)), np.max(results[len(sentence)-1,:])


parser = argparse.ArgumentParser(description = 'Hidden Markov Model for likeliest sequence of POS')

def get_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=str, dest='transition', help='file containing pretrained transition probabilities')
    parser.add_argument('-e', type=str, dest='emission', help='file containing pretrained emission probabilities')
    parser.add_argument('-o', type=str, dest='output', default=sys.stdout, required=False, help='file to write tagged sentences into')
    parser.add_argument('-i', nargs='?', type=str, dest='input', default=sys.stdin, required=False, help='file containing tokenized sentences')
    parser.add_argument('-first', type=bool, dest='first', required=False, help='if set to "True", the algorithm considers that the first element of the sequence'
                                                        'is already known. It is considered its tag is the last column of the transmission file')
    parser.add_argument('-delim', type=str, dest='delim', default='\t', required=False, help='delimiter of the CSV file, the default is set to "\t"')
    return parser

def main():
    parser = get_arg_parser()
    args=parser.parse_args()

    transition = open(args.transition, 'r')
    emission = open(args.emission, 'r')

    if args.delim:
        classifier = PretrainedHMM(transition, emission, args.delim)
    else:
        classifier = PretrainedHMM(transition, emission)

    full_output = ''

    if type(args.input) == str: #an input file is given
        input_file = open(args.input, 'r')
        for line in input_file:
            if args.first == True:
                out = classifier.tag_sent(line, True)
            else:
                out = classifier.tag_sent(line)
            #print(out)
            tokens = nltk.word_tokenize(line)
            out_sent = ''
            for i in range(len(tokens)):
                out_sent = out_sent + tokens[i] + '_' + out[0][i+1] + ' '
            if type(args.output) != str:
                print('Sequence Probability: ', out[1])
                print(out_sent)
            full_output = full_output+'Sequence Probability :'+ str(out[1])+'\n'+ out_sent+'\n'
    else:
        for line in args.input:
            out = classifier.tag_sent(line)
            tokens = nltk.word_tokenize(line)
            out_sent = ''
            for i in range(len(tokens)):
                out_sent = out_sent + tokens[i] + '_' + out[0][i+1] + ' '
            if type(args.output) != str:
                print('Sequence Probability: ', out[1])
                print(out_sent)
            full_output = full_output + 'Sequence Probability :' + str(out[1]) + '\n' + out_sent+'\n'


    if type(args.output) == str:
        with open(args.output, 'w') as file:
            file.write(full_output)



if __name__ == '__main__':
    main()
