import tkinter as tk
import customtkinter as ctk
#import ttkbootstrap as ttkbooster
from tkinter import ttk
from tkinter import filedialog
from io import TextIOWrapper
from PIL import Image


def safe_opener(io:TextIOWrapper):
    if io is None:
        return ''
    io.close()
    proxies_var.set(io.name)


def spinbox_behave(mode:str):
    if mode == 'increment':
        delay_var.set(delay_var.get()+1)
    if mode == 'decrement':
        delay_var.set(delay_var.get()-1)
    if delay_var.get() < 5:
        delay_var.set(60)
    elif delay_var.get() > 60:
        delay_var.set(5)

def increment_delay(event:tk.Event):
    if event.delta > 0:
        spinbox_behave(mode='increment')
    if event.delta < 0:
        spinbox_behave(mode='decrement')

def get_all_variables():
    return {'v':verify_var.get(), 'a':api_var.get(), 'p':proxies_var.get(), 'd':delay_var.get()*60, 'n':nsfw_var.get()}
    

root = ctk.CTk(fg_color='#2C2B2B')
root.geometry('1000x600')
root.title('esser')
root.resizable(False,False)

content_frame = ctk.CTkFrame(master=root)
#content_frame.grid()

root.columnconfigure((0,1,2,3,4,5), weight=1)
root.rowconfigure((0,1,2,3,4), weight=1)

account_creator_button = ctk.CTkButton(root, text='Account creator')
account_creator_button.grid(row=0, column=0)
# comment_upvoter = ctk.CTkButton(root, text='Upvote/Downvote comments')
# account_creator_button.grid(row=1, column=0)

verify_label = ctk.CTkLabel(master=root, text='Verify')
verify_label.grid(row=0, column=1)

verify_var = ctk.IntVar()
verify_check = ctk.CTkCheckBox(master=root, variable=verify_var, checkbox_height=20, checkbox_width=20, border_width=18, border_color='#206ca4', text='')
verify_check.grid(row=0, column=2)

api_label = ctk.CTkLabel(root, text='Give accounts access to Reddit API')
api_label.grid(row = 1, column=1)

api_var = ctk.IntVar()
api_check = ctk.CTkCheckBox(root, variable=api_var, checkbox_height=20, checkbox_width=20, border_width=18, border_color='#206ca4', text='')
api_check.grid(row=1, column=2)

proxy_label = ctk.CTkLabel(master=root, text = 'Proxies')
proxy_label.grid(row=2, column=1)

proxies_frame = ctk.CTkFrame(master=root)
proxies_frame.grid(row=2, column=2)

open_proxies_image = ctk.CTkImage(Image.open('./icons/folder.png'))
open_proxies = ctk.CTkButton(master=proxies_frame, command=lambda:safe_opener(filedialog.askopenfile(initialdir='C:\\', defaultextension=['.txt'])), width=1, image=open_proxies_image, text='')#.......Musi być zamykane!!
open_proxies.grid(row=0, column=2, padx=5)

proxies_var = ctk.StringVar()
proxies_path = ctk.CTkEntry(master=proxies_frame, textvariable=proxies_var)
proxies_path.grid(row=0, column=1)

delay_label = ctk.CTkLabel(master=root, text='Delay between reach creation in minutes')
delay_label.grid(row=3, column=1)

delay_frame = ctk.CTkFrame(root)
delay_frame.columnconfigure((0,1,2), weight=1)
delay_frame.rowconfigure(0, weight=1)
delay_frame.grid(row=3, column=2)

delay_var = ctk.IntVar(value=5)
delay_entry = ctk.CTkEntry(master=delay_frame, textvariable=delay_var)
delay_entry.grid(row=0, column=1)
delay_entry.bind('<MouseWheel>', increment_delay)
delay_down = ctk.CTkButton(master=delay_frame, width=20, height=28, command=lambda:spinbox_behave('decrement'), text='V')
delay_down.grid(row=0, column=0)
delay_up = ctk.CTkButton(master=delay_frame, width=20, height=28, command=lambda:spinbox_behave('increment'), text='Ʌ')
delay_up.grid(row=0, column=2)

nsfw_label = ctk.CTkLabel(root, text='Set account as NSFW')
nsfw_label.grid(row=4, column=1)

nsfw_var = ctk.IntVar()
nsfw_check = ctk.CTkCheckBox(root, variable=nsfw_var, checkbox_height=20, checkbox_width=20, border_width=18, border_color='#206ca4', text='')
nsfw_check.grid(row=4, column=2)

output_label = ctk.CTkFrame(root, bg_color='#2C2B2B', fg_color='#2C2B2B')
output_label.grid(row=0, column=3, columnspan=3, rowspan=3, sticky='nsew')
output_label.columnconfigure((0,1), weight=1)
output_label.rowconfigure((0,1,2,3), weight=1)

output_var = ctk.StringVar(value='aaaa\n\n\n\n\n\n\aaaaaaa')
text_output = ctk.CTkTextbox(master=output_label, width=20)
text_output.grid(row=0, column=0, columnspan=4, sticky='ew')
stop_button = ctk.CTkButton(master=output_label, text='STOP')
stop_button.grid(row=1, column=0)
run_button = ctk.CTkButton(master=output_label, text='START', command=lambda:print(get_all_variables()))
run_button.grid(row=1, column=1)
# text_output.grid(row=0, column=0, columnspan=3,rowspan=3)

root.mainloop()