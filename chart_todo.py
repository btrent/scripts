#!/usr/bin/python

import calendar
import csv
import math
import re
import sys
from pygooglechart import StackedHorizontalBarChart, StackedVerticalBarChart, \
    GroupedHorizontalBarChart, GroupedVerticalBarChart, Axis

categories = {}
meetingcategories = {}
name = ""
width = 750
height = 400
bar_width = 10

def main():
	global name
	if len(sys.argv) != 2:		
		print "Usage: ./chart_todo.py <todo to chart>"
		sys.exit(0)
	name = sys.argv[1]
	fh = open(name, 'r')
	dialect = csv.Sniffer().sniff(fh.read(1024))
	fh.seek(0)
	reader = csv.reader(fh, dialect)

	for row in reader:
		processline(row)

	makechart()

#item,time,category,unexpected,meeting
#org chart,6,strategy,0,0
#email,1,admin,0,0
#org chart planning,1,strategy,0,0
#1-on-1 with sara,1,meet,0,1
#1-on-1 with sara,1,team,0,1
#1-on-1 with david,1,meet,0,1
#1-on-1 with david,1,team,0,1
def processline(row):
	global categories
	#only the header line and null lines should not contain numbers
	if row is None or len(row) < 5:
		return
	m = re.search('\d', row[1])
	if m is None:
		return
	
	#just skip pure meeting rows for now. they are duplicates of the regular category row, which 
	#also has the meeting flag set to 1. it might be useful to have these lines separate in 
	#the future, but I will probably just remove them from the csvs
	if row[2] == 'meet':
		return

	#increment total for this category
	x = categories.get(row[2], 0)
	x += float(row[1])
	categories[row[2]] = x

	#if this is a meeting, also increment the meetings total for this category
	if row[4] == "1":
		x = meetingcategories.get(row[2], 0)
		x += float(row[1])
		meetingcategories[row[2]] = x	

def makechart():
	global name, width, height, bar_width

	totaltime = [0.0]*len(categories)
	totalmeetingtime = [0.0]*len(categories)
	allcategories = [""]*len(categories)
	i = 0
	max = 0

	for x in categories:
		mtime = 0.0
		allcategories[i] = x[0:9]
		if categories[x] > max:
			max = categories[x]
		if x in meetingcategories:
			mtime = meetingcategories[x]
			
		totalmeetingtime[i] = mtime
		totaltime[i] = categories[x] - mtime
		i+=1

	max = int(math.ceil(max / 100.0) * 100)
	part = int(max/4)
	bar_width = int(width/(len(categories)+4.5))

	#general chart properties
	chart = StackedVerticalBarChart(width,height,y_range=(0, max))
	chart.set_title('Working Hours in ' + get_month(name))
	chart.set_legend(['Tasks', 'Meetings'])
	chart.set_bar_width(bar_width)


	#left label
	leftlabel = chart.set_axis_labels(Axis.LEFT, [0, part, part*2, part*3, max])
	chart.set_axis_style(leftlabel, '202020', font_size=10, alignment=0)
	#chart.set_axis_positions(leftlabel, [50])

	#bottom label
	bottomlabel = chart.set_axis_labels(Axis.BOTTOM, allcategories)
	chart.set_axis_style(bottomlabel, '202020', font_size=10, alignment=0)

       	#colors and data
	chart.set_colours(['00ff00', 'ff0000'])
	chart.add_data(totaltime)
	chart.add_data(totalmeetingtime)

	#get it
	chart.download(name+'.png')

def get_month(name):
	global months

	if name[0] == '0':
		return calendar.month_name[int(name[1])]
	elif name[0] == '1':
		return calendar.month_name[int(name[0:2])]

	return "Unknown Month"

if __name__ == "__main__":
	main()
