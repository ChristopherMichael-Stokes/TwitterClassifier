import curses
from curses import wrapper
from ImprovedClassifier import TweetClassifier
from preprocessingTest import ProcessInput
import numpy as np

class TweetPredictor:
  
  def __init__(self):
    self.tc = TweetClassifier()
    self.pi = ProcessInput()    
    self.labelIndices=["london","birmingham","manchester",
      "glasgow","newcastle","sheffield","los angeles","new york"]
    self.tc.loadModel()

  def startPredicting(self):
    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()    

    curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
    while (True):

      stdscr.clear()
      stdscr.border(0)
      i=2
      j=1
      stdscr.addstr(j,i,"please input a tweet:")
      j += 1
      curses.echo()
      stdscr.refresh()
      input=stdscr.getstr(j,i,140)
      curses.noecho()
      stdscr.clear()
      stdscr.border(0)

      temp = "tweet: {}".format(str(input)[1:])
      statement = temp.encode('ascii')
      stdscr.addstr(j,i,statement)
      j += 2

      labels = self.tc.predict(str(input)[2:-1])
      
      for step in range(0,labels.size):
        j += 1
        stdscr.addstr(j,i,self.labelIndices[step])
        stdscr.addstr(j,i+20,str(labels[0][step]),curses.color_pair(1))  

      j += 2
      stdscr.addstr(j,i,"press escape to quit, or any key to continue")
      stdscr.refresh()
      x = stdscr.getch()
      if (x == 27):
        break

def main():
  tp = TweetPredictor()
  try:
    wrapper(tp.startPredicting())
  except (RuntimeError, Exception, KeyboardInterrupt):
    print("program interrupted, coming to a halt")
  finally:
    curses.echo()
    curses.endwin()

if __name__ == "__main__":
  main()
