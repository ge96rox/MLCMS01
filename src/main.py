# Created by longtaoliu at 19.04.21

from class.Grid import *
def runApp(r,c,w,h):
    root = Tk()
    myapp = GridWindow(root,r,c,w,h)
    myapp.draw_grid()
    #myapp.draw_cells()
    #myapp.get_EUtilMap()
    root.mainloop()

if __name__ == '__main__':
    #p1 = Cell(0,0)
    #p1.set_state(1)
    #p2 = Cell(2,3)
    #p2.set_state(1)
    #t = Cell(1,4)
    #t.set_state(2)
    #o = Cell(2,4)
    #o.set_state(3)

    runApp(5, 5,600,600)