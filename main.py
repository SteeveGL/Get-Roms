import threading
import customtkinter as ctk
import json
import os
import tkinter as tk

from tkinter import ttk

from lib.roms import Links

class App(ctk.CTk):

  def __init__(self):
    super().__init__()

    self.title("Get ROMs")
    self.geometry("800x500")

    self.config_file = "config.json"
    self.config = {
      "server": {
          "url": ""
      },
      "roms": {
        "path": "./ROMs"
      }
    }

    self.config_load()

    if not self.config["server"]["url"]:
      self.dialog_setup()
    self.roms_links = Links(self.config["server"]["url"])

    treeview_frame = ctk.CTkFrame(self)
    treeview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    treeview_frame.pack_propagate(False)  # Prevent the frame from resizing with its content
    treeview_frame.configure(width=50)

    self.treeview = ttk.Treeview(treeview_frame)
    self.treeview_scrollbar = ttk.Scrollbar(treeview_frame, orient="vertical", command=self.treeview.yview)
    self.treeview.configure(yscrollcommand=self.treeview_scrollbar.set)
    self.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.treeview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    self.treeview_items = {}

    for link in self.roms_links.roms_console_links():
      title_full = link["title"]

      if not " - " in title_full:
        continue

      title_split = title_full.split(" - ", 1)
      manufacturer = title_split[0]
      console = title_split[1].replace("/", "")

      if not manufacturer in self.treeview_items:
        self.treeview_items[manufacturer] = self.treeview.insert("", tk.END, text=manufacturer, values=("parent"))

      self.treeview.insert(self.treeview_items[manufacturer], tk.END, text=console, values=("child", link["link"]))

    self.treeview.bind("<<TreeviewSelect>>", self.on_tree_select)

    self.roms_frame = ctk.CTkFrame(self)
    self.roms_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    self.rom_label = ctk.CTkLabel(self.roms_frame, text="Select a console.")
    self.rom_label.pack(anchor=tk.CENTER, pady=10)

    self.download_button = ctk.CTkButton(self.roms_frame, text="Download", state=ctk.DISABLED, command=self.button_download)
    self.download_button.pack(side=tk.BOTTOM, pady=20)

  def on_tree_select(self, event):
    self.selected_item = self.treeview.selection()[0]
    self.selected_parent = self.treeview.parent(self.selected_item)
    item_text = self.treeview.item(self.selected_item, "text")
    item = self.treeview.item(self.selected_item)

    if item["values"] and item["values"][0] == "parent":
      self.rom_label.configure(text="Select a console.")
      self.download_button.configure(state=ctk.DISABLED)
      return

    self.links = self.roms_links.roms_links(item["values"][1])
    self.rom_label.configure(text=f"{len(self.links)} items found.")
    self.download_button.configure(state=ctk.NORMAL)

  def button_download(self):
    self.start_download()

  def start_download(self):
    threading.Thread(target=self.rom_download, daemon=True).start()

  def rom_download(self):
    progress_label = ctk.CTkLabel(self.roms_frame)
    progress_label.pack(anchor=tk.CENTER, pady=10)
    progress = ctk.CTkProgressBar(self.roms_frame, orientation="horizontal")
    progress.pack(anchor=tk.CENTER, pady=20)

    self.download_button.configure(state=ctk.DISABLED)

    done = 0
    for link in self.links:
      manufacturer = self.treeview.item(self.selected_parent, "text")
      console = self.treeview.item(self.selected_item, "text")
      download_path = f"{self.config['roms']['path']}/{manufacturer}/{console}/{link['title']}"

      progress_label.configure(text=link['title'])
      self.roms_links.rom_download(link["link"], download_path)

      done += 1
      progress.set((done / len(self.links)) * 100)
      
    progress_label.destroy()
    progress.destroy()

  def dialog_setup(self):
    dialog = ctk.CTkInputDialog(text="Server URL:", title="ROMs source")
    self.config['server']['url'] = dialog.get_input()
    self.config_save()

  def config_load(self):
    if os.path.exists(self.config_file):
      with open(self.config_file, 'r') as file:
        self.config = json.load(file)
    else:
      with open(self.config_file, 'w') as file:
        json.dump(self.config, file, indent=2)
        self.dialog_setup()

  def config_save(self):
    try:
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=2)
    except IOError as e:
        print(f"Error saving to file: {e}")

if __name__ == "__main__":
  app = App()
  app.mainloop()
