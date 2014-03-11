#!/usr/bin/env python

# This script extracts the strongest opening lines from a chess opening book in
# Polyglot format. The output is fairly dirty PGN that can be used with various 
# chess database programs in order to study openings. This has been tested and 
# happily used with SCID.
#
# Example: to extract the best Caro-Kann lines for black from an opening book called
# "Elo2400.bin", you would call the program like this:
#
# ./parse_opening_books.py Elo2400.bin black "1.e4 c6"
#
# PGN would be written to stdout. Pipe output to the location of your choice.

import chess
import libchess
import re
import sys

book = ""
black = 1
color = 0
game_tree = {}
max_moves = 40 #some polyglot books contain infinite repetition so a cap is recommended
white = 0

def main():
	global color
	global book
	global black
	global game_tree
	global white

	if (len(sys.argv) != 4):
		print "USAGE: parse_opening_books.py <polyglot book> <white|black> \"<opening line>\"\n"
		sys.exit(0)

	book = chess.PolyglotOpeningBook(sys.argv[1])
	pos = chess.Position()
	i = 0

	if (sys.argv[2].lower() == "black"):
		color = 1

	opening_line = sys.argv[3]
	if (opening_line.lower() == "full"):
		process_full(pos)
	else:
		process_opening(pos, opening_line)
		
	clean_up()

	print_results()

def print_results():
	for key in game_tree:
		if (game_tree[key] == 1):
			print "[Event \"Opening Study\"]"
			print "[Result \"1/2-1/2\"]"
			print key
			print "1/2-1/2"
			print "\n"

def process_full(pos):
	global black
	global color
	global white

	line = "1."

	if (color == white):
		line = make_best_move(pos, line)

	step_through_moves(pos, line, False)

def process_opening(pos, opening_line):
	opening_line_array = re.sub(r'\d+\.', '', opening_line).split(' ')
	set_opening_line(pos, opening_line_array)

	if (((len(opening_line_array)%2 == 1) and color is black) 
		or ((len(opening_line_array)%2 == 0) and color is white)):
		opening_line = make_best_move(pos, opening_line)

	if (opening_line != ''):
		step_through_moves(pos, opening_line, False)

def make_best_move(pos, line):
	j = 0
	move = ""

	for entry in book.get_entries_for_position(pos):
		if (entry.weight > j):
			j = entry.weight
			move = entry.move

	if (move == ''):
		return ''

	add_move_to_line(move, line)
	pos.make_move(chess.Move.from_uci(str(move)))

	return line + " " + str(move)

def step_through_moves(pos, line, is_our_move):
	global book
	global max_moves

	move = ""
	entries = []

	if (is_our_move):
		fen = pos.fen
		old_line = line
		line = make_best_move(pos, line)

		if (line == '' or line.count(' ') > max_moves):
			pos = chess.Position(fen)
			return

		step_through_moves(pos, line, False)
		pos = chess.Position(fen)
		line = old_line
	else:
		for entry in book.get_entries_for_position(pos):
			entries.append(entry)
		for entry in entries:
			old_line = line
			line = add_move_to_line(entry.move, line)
			move = entry.move

			fen = pos.fen
			pos.make_move(chess.Move.from_uci(str(move)))
			step_through_moves(pos, line, True)
			pos = chess.Position(fen)
			line = old_line

def add_move_to_line(move, line):
	global game_tree

	new_line = line + " " + str(move)
	new_line.rstrip(' ')
	game_tree[new_line] = 1
	return new_line

def clean_up():
	global game_tree

	for line in game_tree:
		while (" " in line):
			line = line.rstrip(' ')
			line = line.split(' ')
			line[len(line)-1] = ''
			line = ' '.join(line)
			line = line.rstrip(' ')

			if (line in game_tree):
				game_tree[line] = 0

def set_opening_line(pos, opening_line):
	for move in opening_line:
		pos.make_move_from_san(move)

if __name__ == "__main__":
    main()

