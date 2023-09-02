import os
from time import sleep
from threading import Thread, active_count
import datetime

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter.filedialog import askopenfilename
from PIL import ImageTk, Image

import pandas as pd

from chat_sql import pass_to_sql, request, to_excel

import json

defalt_text1 = "Esse banco de dados se chama 'sales.db' com uma unica tabela chamada 'main_table'.\nSabendo disso, faça um requisição sql onde:"
defalt_text2 = "Escreva apenas o código sql."

class Parallel:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        from threading import Thread

        pr = Thread(target = self.func, args = [*args], kwargs = kwargs)
        pr.start()

    def __repr__(self):
        return str(self.memoria)
  
def find_key():
    up_bar(20, "Choosing file.")
    globals()["path_key"] = askopenfilename(filetypes = [("Arquivos de texto", "*.txt")])
    up_bar(40, "Plotting.")
    show_paths()
    if globals()["path_key"] == "":
        down_bar()
        return
    up_bar(60, "Reading file.")
    global key_api
    with open(globals()["path_key"], "r") as arq:
        key_api = arq.read()
    up_bar(100)

def find_instructions():
    up_bar(20, "Choosing file.")
    globals()["path_instructions"] = askopenfilename(filetypes = [("Arquivos de texto", "*.txt")])
    up_bar(40, "Plotting.")
    show_paths()
    if globals()["path_instructions"] == "":
        down_bar()
        return
    up_bar(60, "Reading file.")
    global text_instruction
    with open(globals()["path_instructions"], "r") as arq:
        text_instruction = arq.read()
    up_bar(100)

def find_excel():
    up_bar(20, "Choosing file.")
    globals()["path_excel"] = askopenfilename(filetypes = [("Arquivos Excel e CSV", "*.xlsx *.csv")])
    if path_excel == "":
        down_bar()
        return
    up_bar(40, "Plotting.")
    show_paths()
    up_bar(60, "Reading file.")
    try:
        globals()["df"] = pd.read_excel(path_excel)
    except:
        globals()["df"] = pd.read_csv(path_excel)
    up_bar(100)
    

@Parallel
def time():
    global time_now
    while True:
        try:
            time_now = datetime.datetime.now()
            #time_now.year, time_now.month, time_now.day, time_now.hour, time_now.minute, time_now.second
            if time_now.minute > 10:
                Label(gp, text = f"⏳ {time_now.hour}:{time_now.minute}",
                      font = "Times 18", bg = c_main, fg = 'White').place(x = 728, y = 278)
            else:
                Label(gp, text = f"⏳ {time_now.hour}:0{time_now.minute}",
                      font = "Times 18", bg = c_main, fg = 'White').place(x = 728, y = 278)
            sleep(15)
        except:
            break

@Parallel
def num_characters():
    global num_characters_now
    while True:
        try:
            t = box_text.get("1.0","50.50")
            t.replace("  ", " ")
            num_characters_now = len(t)
            if num_characters_now - 1 < 10:
                ch = "00" + str(num_characters_now - 1)
            elif num_characters_now - 1 < 100:
                ch = "0" + str(num_characters_now - 1)
            else:
                ch = str(num_characters_now - 1)
            Label(gp, text = f"¶: {ch} ",
                    font = "Times 18", bg = c_main, fg = 'White').place(x = 658, y = 278)
            sleep(0.25)
        except:
            break

@Parallel
def show_paths():
    global path_key, path_instructions

    Label(gp, text = " "*80,
                font = "Times 22", bg = c_1, fg = 'White').place(x = 250, y = 500)
    Label(gp, text = " "*80,
                font = "Times 22", bg = c_1, fg = 'White').place(x = 250, y = 570)
    Label(gp, text = " "*80,
                font = "Times 22", bg = c_1, fg = 'White').place(x = 250, y = 640)
            
    Label(gp, text = "..." + path_key[-45:],
                font = "Times 22", bg = c_1, fg = 'White').place(x = 250, y = 500)
    Label(gp, text = "..." + path_instructions[-45:],
                font = "Times 22", bg = c_1, fg = 'White').place(x = 250, y = 570)
    Label(gp, text = "..." + path_excel[-45:],
                font = "Times 22", bg = c_1, fg = 'White').place(x = 250, y = 640)

@Parallel
def make_request():
    global memory, key_api, path_excel, df
    
    if path_excel == "← Choose the file":
        messagebox.showinfo(title = "Attention!",
                            message = "Choose excel file.")
        down_bar(0)
        return    
    up_bar(25)
    db_global = pass_to_sql(df)
    up_bar(35)
    globals()["cod"], globals()["temp_df"] = request(text_instruction + defalt_text1 + box_text.get("1.0","50.50") + defalt_text2,
                                                     key_api,
                                                     db_global)
    global cod, temp_df
    up_bar(85)
    db_global.close()
    up_bar(95)

    try:
        memory[f"{time_now.year}-{time_now.month}-{time_now.day}"].append({"time":f"{time_now.hour}:{time_now.minute}:{str(time_now.second)[:4]}",
                                                                              "input":box_text.get("1.0","50.50"),
                                                                              "output":temp_df,
                                                                              "query":cod["choices"][0]["text"]})
    except KeyError:
        memory[f"{time_now.year}-{time_now.month}-{time_now.day}"] = [{"time":f"{time_now.hour}:{time_now.minute}:{str(time_now.second)[:4]}",
                                                                              "input":box_text.get("1.0","50.50"),
                                                                              "output":temp_df,
                                                                              "query":cod["choices"][0]["text"]}]
    box_sql.delete("1.0", "1000.1000")
    box_sql.insert("1.0", cod["choices"][0]["text"].replace("\n", " "))

    
    with open(name_json, "w") as _json:
        json.dump(memory, _json)
    up_bar(98)
    with open(name_json, "r") as _json:
        memory = json.load(_json)
    up_bar(100)
        
    return cod, temp_df

@Parallel
def save_in_excel():
    if not "temp_df" in globals():
        messagebox.showinfo(title = "Attention!",
                        message = "You need to have made a request to be able to save the table.")
        return
    global temp_df, name_xlsx
    up_bar(10)
    to_excel(temp_df, name_xlsx.get())
    up_bar(100)

def clean():
    box_text.delete("1.0", "100000.100000")


@Parallel
def down_bar(m = 0):
    global down
    down = True
    while p_bar_value.get() > m + 0.005:
        p_bar_value.set(p_bar_value.get() * 0.9)

        Label(gp, text = " "*40,
                  font = "Times 10", bg = c_main, fg = 'White',
                  borderwidth = 0, relief = "sunken").place(x = 15, y = 681)
        
        sleep(0.01)
    down = False
        

@Parallel
def up_bar(m, load:str = "Loading..."):
    locals()["interation"] = 0
    while p_bar_value.get() < m and locals()["interation"] < 80 and not down:
        p_bar_value.set(p_bar_value.get()*0.985 + m*0.02)
        
        Label(gp, text = load + " "*(40 - len(load)),
          font = "Times 10", bg = c_main, fg = 'White',
          borderwidth = 0, relief = "sunken").place(x = 15, y = 681)

        locals()["interation"] += 1
        
        sleep(0.01)
        if p_bar_value.get() >= 100:
            down_bar(0)
    Label(gp, text = " "*40,
                  font = "Times 10", bg = c_main, fg = 'White',
                  borderwidth = 0, relief = "sunken").place(x = 15, y = 681)

@Parallel
def correct_bar():
    try:
        while True:
            n1 = p_bar_value.get()
            sleep(1)
            n2 = p_bar_value.get()
            if n1 == n2 and n1 > 0.1 and n2 > 0.1:
                down_bar(0)
            sleep(0.5)
    except RuntimeError:
        pass

@Parallel
def past_column():
    global memory
    n_column_past = 0

    def pass_example_0():
        global temp_df, name_xlsx
        clean()
        box_text.insert("1.0", memory[find_to.get()][0 + n_column_past]["input"])
        box_sql.delete("1.0", "1000.1000")
        box_sql.insert("1.0", memory[find_to.get()][0 + n_column_past]["query"].replace("\n"," "))
        temp_df = memory[find_to.get()][0 + n_column_past]["output"]
    def pass_example_1():
        global temp_df, name_xlsx
        clean()
        box_text.insert("1.0", memory[find_to.get()][1 + n_column_past]["input"])
        box_sql.delete("1.0", "1000.1000")
        box_sql.insert("1.0", memory[find_to.get()][1 + n_column_past]["query"].replace("\n"," "))
        temp_df = memory[find_to.get()][1 + n_column_past]["output"]
    def pass_example_2():
        global temp_df, name_xlsx
        clean()
        box_text.insert("1.0", memory[find_to.get()][2 + n_column_past]["input"])
        box_sql.delete("1.0", "1000.1000")
        box_sql.insert("1.0", memory[find_to.get()][2 + n_column_past]["query"].replace("\n"," "))
        temp_df = memory[find_to.get()][2 + n_column_past]["output"]
    def pass_example_3():
        global temp_df, name_xlsx
        clean()
        box_text.insert("1.0", memory[find_to.get()][3 + n_column_past]["input"])
        box_sql.delete("1.0", "1000.1000")
        box_sql.insert("1.0", memory[find_to.get()][3 + n_column_past]["query"].replace("\n"," "))
        temp_df = memory[find_to.get()][3 + n_column_past]["output"]
    def pass_example_4():
        global temp_df, name_xlsx
        clean()
        box_text.insert("1.0", memory[find_to.get()][4 + n_column_past]["input"])
        box_sql.delete("1.0", "1000.1000")
        box_sql.insert("1.0", memory[find_to.get()][4 + n_column_past]["query"].replace("\n"," "))
        temp_df = memory[find_to.get()][4 + n_column_past]["output"]
    def pass_example_5():
        global temp_df, name_xlsx
        clean()
        box_text.insert("1.0", memory[find_to.get()][5 + n_column_past]["input"])
        box_sql.delete("1.0", "1000.1000")
        box_sql.insert("1.0", memory[find_to.get()][5 + n_column_past]["query"].replace("\n"," "))
        temp_df = memory[find_to.get()][5 + n_column_past]["output"]
    
    while True:
        try:
            list_past = ttk.Combobox(gp, textvariable = find_to,
                                     values = list(memory.keys()), font = "Arial 20").place(x = 860, y = 15)

            for i in range(6):
                try:
                    m = memory[find_to.get()][i + n_column_past]
                    Label(gp, text = m["time"] + " " * (55 - len(m["time"])),
                          font = "Times 19", bg = c_1, fg = 'White',
                          borderwidth = 0, relief = "sunken").place(x = 860, y = 60 + 120 * i)
                    Label(gp, text = m["input"][:30] + "..." + " " * (35 - len(m["input"][:30])) ,
                          font = "Times 19", bg = c_1, fg = 'White',
                          borderwidth = 0, relief = "sunken").place(x = 860, y = 90 + 120 * i)
                    Label(gp, text = m["query"][:30].replace("\n"," ").replace("  "," ") + "..." + " " * (35 - len(m["query"][:30].replace("\n"," ").replace("  "," "))),
                          font = "Times 19", bg = c_1, fg = 'White',
                          borderwidth = 0, relief = "sunken").place(x = 860, y = 120 + 120 * i)

                    function = eval(f"pass_example_{i}")
                    Button(gp, text = "←",
                           bg = c_atention, borderwidth = 1, font = "Arial 10", activebackground = c_help,
                           activeforeground = 'White', fg = 'White',
                           command = function).place(x = 1175, y = 60 + 120 * i)        
                except:
                    pass
        except RuntimeError:
            break  

        sleep(3)

@Parallel
def how_many_threads():
    try:
        while True:
            hm = active_count()
            if hm < 10:
                hm = "0"+str(hm)
            Label(gp, text = f"Active concurrent threads: {str(hm)}",
                          font = "Times 10", bg = c_1, fg = 'White',
                          borderwidth = 0, relief = "sunken").place(x = 5, y = 5)
            sleep(1)
    except RuntimeError:
        pass
        


def help_key():
    messagebox.showinfo(title = "Information!",
                        message = "You must have your open-ai key in a txt file and choose it.\nIf you don't have the open-ai key get one here https://platform.openai.com/account/api-keys.")

def help_instructions():
    messagebox.showinfo(title = "Information!",
                        message = "You should have a txt briefly explaining your database variables.")

def help_request():
    messagebox.showinfo(title = "Information!",
                        message = "After writing your request in the larger box, you can make the request, then you can save the table of your request by pressing 'save'.")

def help_excel():
    messagebox.showinfo(title = "Information!",
                        message = "Choose the spreadsheet you want to work on, everything involving the spreadsheet will be done locally on your computer for security.")

def help_save_excel():
    messagebox.showinfo(title = "Information!",
                        message = "Save your request in an Excel table with the name you chose in the box on the side.") 

### Parte gráfica:
if __name__ == "__main__":

    name_json = "memory.json"

    try:
        with open(name_json, "r") as _json:
            memory = json.load(_json)
    except FileNotFoundError:
        try:
            with open(name_json, "w") as _json:
                json.dump({}, _json)
                print(f"File '{name_json}' created and data written successfully.")
                with open(name_json, "r") as _json:
                    memory = json.load(_json)
        except FileNotFoundError:
            print(f"The file '{name_json}' could not be created.")

    
    

    #Graphic:
    main_path = os.getcwd()
    
    gp = Tk()

    gp.geometry("1200x700")
    gp.resizable(width = False, height = False)
    gp.title("SQL request")

    c_main = '#3a597a'
    c_atention = '#6960ee'
    c_1 = '#4a698c'
    c_3 = '#3c79a0'
    c_2 = '#596f71'
    c_help = '#13868f'
    c_6 = '#cd3131'
    c_7 = '#ad2929'
    
    gp.configure(bg = c_main)

    #Vars:
    time_now = 0
    num_characters_now = ""
    path_instructions = "← Choose the file"
    path_key = "← Choose the file"
    name_xlsx = StringVar(gp, "new_table")
    path_excel = "← Choose the file"
    p_bar_value = DoubleVar()
    find_to = StringVar()
    text_instruction = ""
    key_api = ""
    down = False

    #Process:
    show_paths()

    #Parallels process:
    time()
    #past_column()
    
    #Texto principal:
    Label(gp, text = "EASY QUERY",
          font = "Times 60", bg = c_main, fg = 'White',
          borderwidth = 0, relief = "sunken").place(x = 15, y = 15)

    #Buttons:
    Button(gp, text = "Key openai",
           bg = c_atention, borderwidth = 1, font = "Arial 24", activebackground = c_help,
           activeforeground = 'White', fg = 'White',
           command = find_key).place(x = 15, y = 480)

    Button(gp, text = "?",
            bg = c_help, borderwidth = 1, font = "Arial 12", activebackground = c_help,
            activeforeground = 'White', fg = 'White',
            command = help_key).place(x = 200, y = 480)


    Button(gp, text = "Instructions",
           bg = c_atention, borderwidth = 1, font = "Arial 24", activebackground = c_help,
           activeforeground = 'White', fg = 'White',
           command = find_instructions).place(x = 15, y = 550)

    Button(gp, text = "?",
            bg = c_help, borderwidth = 1, font = "Arial 12", activebackground = c_help,
            activeforeground = 'White', fg = 'White',
            command = help_instructions).place(x = 209, y = 550)

    Button(gp, text = "Excel/csv",
           bg = c_atention, borderwidth = 1, font = "Arial 24", activebackground = c_help,
           activeforeground = 'White', fg = 'White',
           command = find_excel).place(x = 15, y = 620)

    Button(gp, text = "?",
            bg = c_help, borderwidth = 1, font = "Arial 12", activebackground = c_help,
            activeforeground = 'White', fg = 'White',
            command = help_excel).place(x = 176, y = 620)


    Button(gp, text = "Request",
           bg = c_7, borderwidth = 1, font = "Arial 24", activebackground = c_help,
           activeforeground = 'White', fg = 'White',
           command = make_request).place(x = 15, y = 320)

    Button(gp, text = "?",
            bg = c_help, borderwidth = 1, font = "Arial 12", activebackground = c_help,
            activeforeground = 'White', fg = 'White',
            command = help_request).place(x = 162, y = 320)

    Button(gp, text = "Save",
           bg = c_7, borderwidth = 1, font = "Arial 24", activebackground = c_help,
           activeforeground = 'White', fg = 'White',
           command = save_in_excel).place(x = 15, y = 390)

    Button(gp, text = "?",
            bg = c_help, borderwidth = 1, font = "Arial 12", activebackground = c_help,
            activeforeground = 'White', fg = 'White',
            command = help_save_excel).place(x = 115, y = 390)


    #Entrys:
    Entry(gp, textvariable = name_xlsx,
          font = "Times 37", width = 12).place(x = 140, y = 390)

    #Text box:
    position_box_text = [13, 120]
    box_text = Text(gp, width = 40, height = 4,
                 font = "Times 30", borderwidth = 2,
                 relief = "sunken")
    
    box_text.place(x = position_box_text[0], y = position_box_text[1])
    
    Button(gp, text = chr(128465),
           bg = c_6, borderwidth = 1, font = "Arial 12", activebackground = c_7,
           activeforeground = 'White', fg = 'White',
           command = clean).place(x = position_box_text[0]+776, y = position_box_text[1])


    position_box_sql = [453, 320]
    box_sql = Text(gp, width = 30, height = 6,
                   font = "Times 18", borderwidth = 2,
                   relief = "sunken")

    box_sql.place(x = position_box_sql[0], y = position_box_sql[1])

    #Progress Bar:
    s = ttk.Style()
    s.theme_use("clam")
    s.configure("green.Horizontal.TProgressbar", foreground = "Green", background = "Green",
                troughcolor = "Gray")

    container = ttk.Frame(gp)
    container.place(x = 190, y = 320, width = 254, height = 60)

    p_bar = ttk.Progressbar(container,
                            style = "custon.Horizontal.TProgressbar",
                            orient = "horizontal",
                            mode = "determinate",
                            variable = p_bar_value)
    p_bar.pack(fill="both", expand=True)
    
    #Final Process:
    num_characters()
    correct_bar()
    past_column()
    how_many_threads()

    gp.mainloop()

