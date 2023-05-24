import ttkbootstrap as ttk
from ttkbootstrap.constants import *

window = ttk.Window(themename="solar")
window.geometry('600x650')
label_frame = ttk.LabelFrame(window, height=50, width=100, bootstyle=(DARK, OUTLINE))
label_frame.place(x=0, y=0)
label = ttk.Label(label_frame, text="for test", bootstyle="success")
label.pack(side="bottom")
window.mainloop()
