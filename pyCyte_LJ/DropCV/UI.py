# -*- coding: utf-8 -*-
"""
Created on Sun Nov 13 08:04:03 2016

@author: avandenbroucke

http://stackoverflow.com/questions/17252096/change-optionmenu-based-on-what-is-selected-in-another-optionmenu
"""

import sys
if sys.version_info[0] >= 3:
    import tkinter as tk
else:
    import Tkinter as tk

if __package__ is None or __package__ == '':
    from pyCyte.DropCV import ReaderDat
else:
    from ..DropCV import ReaderDat

class App(tk.Frame):

    def __init__(self, master):
        tk.Frame.__init__(self, master)



        self.dict = {'Ascent': ['082916UKOmics', '082916UKDMSO'],
                     'AscentUK': ['102016'],
                     'BMG': ['072016'],
                     'BMGUK': ['102016'],
                     'BioTek1': ['042016'],
                     'BioTek2': ['092016', '062016UKOmics', '042016', '062016UKDMSO']}

        #self.dict =  {'Asia': ['Japan', 'China', 'Malaysia'],
      #               'Europe': ['Germany', 'France', 'Switzerland']}

        self.variable_a = tk.StringVar(self)
        self.variable_b = tk.StringVar(self)

        self.variable_a.trace('w', self.update_options)

        self.optionmenu_a = tk.OptionMenu(self, self.variable_a, *self.dict.keys())
        self.optionmenu_b = tk.OptionMenu(self, self.variable_b, '')

        self.variable_a.set('BioTek1')

        self.optionmenu_a.pack()
        self.optionmenu_b.pack()
        button = tk.Button(self.master, text="Go", command=self.ok)
        button.pack()
        self.pack()

    def ok(self):
        print("Reader value is", self.variable_a.get())
        print("Calibration is", self.variable_b.get())
 #       self.master.quit()
        self.master.destroy()
        
    def update_options(self, *args):
        countries = self.dict[self.variable_a.get()]
        self.variable_b.set(countries[0])

        menu = self.optionmenu_b['menu']
        menu.delete(0, 'end')

        for country in countries:
            menu.add_command(label=country, command=lambda nation=country: self.variable_b.set(nation))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.mainloop()