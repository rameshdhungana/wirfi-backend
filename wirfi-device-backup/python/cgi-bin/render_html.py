#!/usr/bin/python
import os

def render_html(file_name):
    try:
        current_dir = os.path.dirname(os.path.realpath(__file__))
        print "Content-type:text/html\r\n\r\n"
        with open(current_dir+'/html/'+file_name) as f:
            for line in f:
                print line
    except Exception as e:
        print e
