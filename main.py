import os
import json
import requests

import customtkinter as ctk
from tkinter import ttk
from bs4 import BeautifulSoup

config_file = "config.json"
config_default = {
   "host": {
      "url": ""
   }
}

if os.path.exists(config_file):
  with open(config_file, 'r') as file:
    config = json.load(file)
else:
  with open(config_file, 'w') as file:
    json.dump(config_default, file, indent=2)
  config = config_default



def config_save():
  try:
      with open(config_file, 'w') as file:
          json.dump(config, file, indent=2)
  except IOError as e:
      print(f"Error saving to file: {e}")

def button_setup():
  dialog = ctk.CTkInputDialog(text="URL:", title="ROMs source")
  text = dialog.get_input()
  if text:
    config['host']['url'] = text
    config_save()
    panel_setup.pack_forget()
    panel_roms.pack(expand=True, fill='both')

def links_load():
  url = f"{config['host']['url']}/files/No-Intro/"
  response = requests.get(url)
  if not response.status_code == 200:
    return None
  
  html_content = response.text

  soup = BeautifulSoup(html_content, 'html.parser')
  table_body = soup.find('table', {'id': 'list'}).find('tbody')
  link_info = [(f"{url}{link.get('href')}", link.get_text()) for link in table_body.find_all('a')]
  link_info.pop(0)

  return link_info


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("600x600")

panel_setup = ctk.CTkFrame(app)
button_setup = ctk.CTkButton(panel_setup, text="Setup", command=button_setup)
button_setup.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

panel_roms = ctk.CTkFrame(app)
tree_view = ttk.Treeview(panel_roms)
tree_view.pack(pady=20, expand=True, fill='both')

# Define columns
tree_view['columns'] = ("Column1", "Column2")
tree_view.column("#0", width=120, stretch='no')
tree_view.column("Column1", anchor='center', width=120)
tree_view.column("Column2", anchor='center', width=120)

tree_view.heading("#0", text="Name", anchor='w')
tree_view.heading("Column1", text="Column 1", anchor='center')
tree_view.heading("Column2", text="Column 2", anchor='center')

# Insert parent and child items
parent1 = tree_view.insert("", "end", text="Parent 1", values=("Value1", "Value2"))
parent2 = tree_view.insert("", "end", text="Parent 2", values=("Value3", "Value4"))

tree_view.insert(parent1, "end", text="Child 1.1", values=("Value5", "Value6"))
tree_view.insert(parent1, "end", text="Child 1.2", values=("Value7", "Value8"))

tree_view.insert(parent2, "end", text="Child 2.1", values=("Value9", "Value10"))


if not config['host']['url']:
  panel_setup.pack(expand=True, fill='both')
else:
  panel_roms.pack(expand=True, fill='both')

app.mainloop()