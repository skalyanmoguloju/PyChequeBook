#!/usr/bin/env python
'''
PyCheckbook.py  A personal finance manager in Python

This code is in development -- use at your own risk. Email
comments, patches, complaints to msaikalyan@gmail.com

Usage: PyCheckbook.py [options] [filename]

Options:
  -h     Print this help message
  -g     Use the GTK+ widget set
  -t     Use the Tk widget set (default)

filename is optional

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
'''

import sys,string,os
from pycheckbook.Checkbook import *

class PyCheckbook:
    version = 3.2
    def __init__(self,filename=None):
        self.cb = Checkbook()
        self.cbwidget = CheckbookWidget(self,
                                        "Python Checkbook Manager "
                                        "version %.1f" % self.version)
        self.edited = 0
        if filename:
            self.cb.read_qif(filename)
            self.redraw()
        self.cbwidget.mainloop()
        return

    def newentry(self,*args):
        cd = CheckWidget(self.cbwidget.head())
        if cd.check:
            self.edited = 1
            self.cb.append(cd.check)
        self.redraw()
        return

    def reconcile(self,*args):
        current_balance = askfloat("Current Balance",
                                   "What is the balance "
                                   "of your last statement?")
        if not current_balance: return
        cleared_balance = self.get_cleared_balance()
        difference = current_balance - cleared_balance
        if abs(difference) < 0.01:
            showinfo("Balances!",
                     "Your checkbook balances!")
        else:
            response = askquestion("Adjust Balance?",
                                   "Your checkbook balance differs "
                                   "by $%.2f. Adjust balance?" %\
                                   difference)
            if response == 'yes':
                self.adjust_balance(difference)
        return

    def adjust_balance(self,diff):
        check = Check()
        check.payee = "Balance Adjustment"
        check.amount = diff
        check.cleared = 1
        check.memo = "Adjustment"
        self.cb.append(check)
        self.redraw()
        return

    def get_cleared_balance(self):
        total = 0.
        for check in self.cb:
            if check.cleared:
                total = total + check.amount
        return total

    def markcleared(self,*args):
        try:
            index = self.cbwidget.get_index()
        except:
            return
        self.edited = 1
        check = self.cb[index]
        check.cleared = 1
        self.redraw(index)
        return

    def voidentry(self,*args):
        try:
            index = self.cbwidget.get_index()
        except:
            return
        self.edited = 1
        response = askquestion("Really Void?",
                               "Really void this check?")
        if response == "yes":
            today = Date()
            check = self.cb[index]
            check.amount = 0.
            check.payee = "VOID: " + check.payee
            check.memo = "voided %s" % today.formatUS()
        self.redraw(index)
        return

    def deleteentry(self,*args):
        try:
            index = self.cbwidget.get_index()
        except:
            return
        self.edited = 1
        response = askquestion("Really Delete?",
                               "Really delete this check?")
        if response == "yes": del self.cb[index]
        self.redraw(index)
        return

    def previousentry(self,*args):
        try:
            index = self.cbwidget.get_index()
        except:
            return
        newindex = index - 1
        if newindex >= 0: self.cbwidget.goto_new_index(newindex,index)
        return

    def nextentry(self,*args):
        try:
            index = self.cbwidget.get_index()
        except:
            return
        newindex = index + 1
        if newindex < self.cbwidget.display_size():
            self.cbwidget.goto_new_index(newindex,index)
        return

    def editentry(self,*args):
        try:
            index = self.cbwidget.get_index()
        except:
            return
        check = self.cb[index]
        cd = CheckWidget(self.cbwidget.head(),check)
        if cd.check:
            self.edited = 1
            self.cb[index] = cd.check
        self.redraw(index)
        return

    def redraw(self,index=None):
        self.cbwidget.clear()
        total = 0.
        for check in self.cb:
            total = total + check.amount
            self.cbwidget.append(check.date.formatUS(),check.number,
                                 check.payee,check.cleared,check.comment,
                                 check.memo,check.amount,total)
        self.cbwidget.goto_new_index(index)
        return        

    def load_file(self,*args):
        #Closes old file and opens a new file
        self.close()
        self.cb = Checkbook()
        self.edited = 0
        filename = askopenfilename(filetypes=[("Quicken Interchange Format",
                                               "*.qif")])
        if not filename: return
        self.cb.read_qif(filename)
        self.redraw()
        return

    def import_file(self,*args):
        #Appends the records from a file to the current checkbook
        filename = askopenfilename(filetypes=[("Quicken Interchange Format",
                                               "*.qif")])
        if not filename: return
        self.edited = 1
        self.cb.read_qif(filename,'import')
        self.redraw()


    def save_as_file(self,entry=None):
        filename = asksaveasfilename(filetypes=[("Quicken Interchange Format",
                                                 "*.qif")])
        if not filename: return
        self.edited = 0
        self.cb.write_qif(filename)
        return

    def export_text(self,entry=None):
        filename = asksaveasfilename(filetypes=[("Text",
                                                 "*.txt")])
        if not filename: return
        self.cb.write_txt()
        return

    def save_file(self,entry=None):
        if not self.cb.filename:
            self.save_as_file()
        else:
            self.edited = 0
            self.cb.write_qif()
        return

    def close(self,*args):
        if self.edited:
            response = askquestion("Question",
                                   "Save file before closing?")
            if response == 'yes':
                self.save_file()
        self.edited = 0
        self.cb = Checkbook()
        self.redraw()
        return

    def quit(self,*args):
        self.close()
        self.cbwidget.main_quit()
        return

if __name__ == "__main__":
    import getopt
    opts,args = getopt.getopt(sys.argv[1:],'hgt')

    widgets = 'tk'
    for (key,val) in opts:
        if key == '-h':
            print __doc__
            sys.exit()
        elif key == '-t': widgets = 'tk'
        elif key == '-g': widgets = 'gtk'

    if widgets == 'gtk':
        from pycheckbook.gtk_interface import CheckbookWidget, CheckWidget, \
             askfloat, askquestion,\
             askopenfilename,asksaveasfilename,showinfo
    else:
        from pycheckbook.tk_interface import CheckbookWidget, CheckWidget, \
             askfloat, askquestion,\
             askopenfilename,asksaveasfilename,showinfo

    if len(args):
        gp = PyCheckbook(args[0])
    else:                
        gp = PyCheckbook()

