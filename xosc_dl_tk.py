import metadata
import download
import parsecontents
import updater
import platform
from PIL import Image, ImageTk
import tkinter as tk
from tkinter.ttk import Notebook, Style, Label, Frame, Button, LabelFrame, Entry, Progressbar

import urllib.request 
opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

WIDTH = 900
HEIGHT = 400

version = updater.current_version()

#Download a file at a url, returns file path
def download(fileURL):
	try:
		downloadedfile, headers = urllib.request.urlretrieve(fileURL)
		# downloadlocation = os.path.join("downloads",filename)
		# shutil.move(downloadedfile, downloadlocation)
		# print("downloaded {} from url {}".format(filename, fileURL))
		return downloadedfile
	except Exception as e: 
		print(e)
		return None

class labeledEntry(Frame):
	def __init__(self, text, *args, **kwargs):
		Frame.__init__(self, *args, **kwargs)
		self.label = Label(self, text = text)
		self.label.pack(side = 'left', expand = 0, fill = 'both', padx =2)
		self.entry = Entry(self)
		self.entry.pack(side = 'right', expand = 0, fill = 'both', padx = 2)

class AutoScroll(object):
	def __init__(self, master):
		try:
			vsb = tk.Scrollbar(master, orient='vertical', command=self.yview)
		except:
			pass
		hsb = tk.Scrollbar(master, orient='horizontal', command=self.xview)

		try:
			self.configure(yscrollcommand=self._autoscroll(vsb))
		except:
			pass
		self.configure(xscrollcommand=self._autoscroll(hsb))

		self.grid(column=0, row=0, sticky='nsew')
		try:
			vsb.grid(column=1, row=0, sticky='ns')
		except:
			pass
		hsb.grid(column=0, row=1, sticky='ew')

		master.grid_columnconfigure(0, weight=1)
		master.grid_rowconfigure(0, weight=1)

		methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
			| tk.Place.__dict__.keys()

		for meth in methods:
			if meth[0] != '_' and meth not in ('config', 'configure'):
				setattr(self, meth, getattr(master, meth))

	@staticmethod
	def _autoscroll(sbar):
		'''Hide and show scrollbar as needed.'''
		def wrapped(first, last):
			first, last = float(first), float(last)
			if first <= 0 and last >= 1:
				sbar.grid_remove()
			else:
				sbar.grid()
			sbar.set(first, last)
		return wrapped

	def __str__(self):
		return str(self.master)

def _create_container(func):
	'''Creates a tk Frame with a given master, and use this new frame to
	place the scrollbars and the widget.'''
	def wrapped(cls, master, **kw):
		container = tk.Frame(master)
		container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
		container.bind(
			'<Leave>', lambda e: _unbound_to_mousewheel(e, container))
		return func(cls, container, **kw)
	return wrapped

def _bound_to_mousewheel(event, widget):
	child = widget.winfo_children()[0]
	if platform.system() == 'Windows' or platform.system() == 'Darwin':
		child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
		child.bind_all('<Shift-MouseWheel>',
					   lambda e: _on_shiftmouse(e, child))
	else:
		child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
		child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
		child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
		child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
	if platform.system() == 'Windows' or platform.system() == 'Darwin':
		widget.unbind_all('<MouseWheel>')
		widget.unbind_all('<Shift-MouseWheel>')
	else:
		widget.unbind_all('<Button-4>')
		widget.unbind_all('<Button-5>')
		widget.unbind_all('<Shift-Button-4>')
		widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
	if platform.system() == 'Windows':
		widget.yview_scroll(-1 * int(event.delta / 120), 'units')
	elif platform.system() == 'Darwin':
		widget.yview_scroll(-1 * int(event.delta), 'units')
	else:
		if event.num == 4:
			widget.yview_scroll(-1, 'units')
		elif event.num == 5:
			widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
	if platform.system() == 'Windows':
		widget.xview_scroll(-1 * int(event.delta / 120), 'units')
	elif platform.system() == 'Darwin':
		widget.xview_scroll(-1 * int(event.delta), 'units')
	else:
		if event.num == 4:
			widget.xview_scroll(-1, 'units')
		elif event.num == 5:
			widget.xview_scroll(1, 'units')

class ScrolledListbox(AutoScroll, tk.Listbox):
	@_create_container
	def __init__(self, master, **kw):
		tk.Listbox.__init__(self, master, **kw,)
		AutoScroll.__init__(self, master)

class window(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.title("Open Shop Channel Downloader - Library")
		self.geometry(f"{WIDTH}x{HEIGHT}")
		self.wait_visibility(self)
		self.outer_frame = Frame(self)
		self.outer_frame.pack(fill = "both", expand = 1, padx = 5, pady = 5)


		self.left_column = LabelFrame(self.outer_frame, text = "Apps Library")
		self.left_column.pack(side = 'left', expand = 1, fill = "both", padx = 5, pady = 5)

		self.apps_listbox = ScrolledListbox(self.left_column)
		self.apps_listbox.pack(expand = 1, fill = "both", padx = 5, pady = 5)
		self.apps_listbox.bind("<<ListboxSelect>>", self.on_selection)

		self.right_column = Frame(self.outer_frame)
		self.right_column.pack(side = 'right', expand = 0, fill = "both", padx = 5, pady = 5)

		self.metadata_frame = LabelFrame(self.right_column, text = "Application Metadata")
		self.metadata_frame.pack(side = "top", expand = 0, fill = "both")

		self.mgr = Notebook(self.metadata_frame)
		self.mgr.pack(side = "top", expand = 0, fill = "both", padx = 5, pady = 5)
		self.general_page = general_page(self.mgr)
		self.mgr.add(self.general_page, text = "General")
		self.description_page = description_page(self.mgr)
		self.mgr.add(self.description_page, text = "Description")

		self.checkbutton_frame = Frame(self.metadata_frame)
		self.checkbutton_frame.pack(side = 'top', fill = 'x', expand = 0)
		self.extract_var = tk.IntVar()
		self.extract_checkbutton = tk.Checkbutton(self.checkbutton_frame, text = "Extract Downloaded App", variable = self.extract_var)
		self.extract_checkbutton.pack(side = 'left', fill = 'x', expand = 0)

		self.filename_entry = labeledEntry('Output File', self.metadata_frame)
		self.filename_entry.pack(side = 'top', expand = 0, fill = 'x', padx = 5, pady = 5)

		self.download_button = Button(self.metadata_frame, text = "Download App")
		self.download_button.pack(side = "left", expand = 0, padx = 5, pady = 5)

		self.download_progress_bar = Progressbar(self.metadata_frame)
		self.download_progress_bar.pack(side = "left", padx = 5, pady = 5)

		self.icon_frame = LabelFrame(self.right_column, text = "Application Icon")
		self.icon_frame.pack(side = "top", expand = 1, fill = "both")
		self.icon = Label(self.icon_frame)
		self.icon.pack(fill = "both")

		self.populate()

	def populate(self):
		for item in parsecontents.list():
			self.apps_listbox.insert('end', item)

	def on_selection(self, event):
		w = event.widget
		selection = w.get(w.curselection()[0])
		info = metadata.dictionary(selection)
		self.general_page.update(info)
		self.update_icon(download(metadata.icon(selection)))

	def update_icon(self,image_path):
		maxheight = self.icon_frame.winfo_height()
		maxwidth = self.icon_frame.winfo_width()
		if maxwidth > 0 and maxheight > 0:
			image = Image.open(image_path)
			wpercent = (maxwidth/float(image.size[0]))
			hsize = int((float(image.size[1])*float(wpercent)))
			if hsize <= 0:
				return
			new_image = image.resize((maxwidth,hsize), Image.ANTIALIAS)
			if new_image.size[1] > maxheight:
				hpercent = (maxheight/float(image.size[1]))
				wsize = int((float(image.size[0])*float(hpercent)))
				new_image = image.resize((wsize,maxheight), Image.ANTIALIAS)

			image = ImageTk.PhotoImage(new_image)

			self.icon.configure(image=image)
			self.icon.image = image

class page(Frame):
	def __init__(self, *args, **kwargs):
		Frame.__init__(self, *args, **kwargs)
		self.pack(fill = "both", expand = 1, padx = 10, pady = 10)

class general_page(page):
	def __init__(self, *args, **kwargs):
		page.__init__(self, *args, **kwargs)
		self.app_name_entry = labeledEntry('App Name', self)
		self.app_name_entry.pack(fill = 'x', expand = 0, side = 'top', pady = 5, padx = 5)
		self.version_entry = labeledEntry('Version', self)
		self.version_entry.pack(fill = 'x', expand = 0, side = 'top', pady = 5, padx = 5)
		self.developer_entry = labeledEntry('Developer', self)
		self.developer_entry.pack(fill = 'x', expand = 0, side = 'top', pady = 5, padx = 5)
		self.contributors_entry = labeledEntry('Contributors', self)
		self.contributors_entry.pack(fill = 'x', expand = 0, side = 'top', pady = 5, padx = 5)
		self.release_date_entry = labeledEntry('Release Date', self)
		self.release_date_entry.pack(fill = 'x', expand = 0, side = 'top', pady = 5, padx = 5)
		self.entries = [self.app_name_entry, self.version_entry, self.developer_entry, self.contributors_entry, self.release_date_entry]

	def update(self, info):
		for e in self.entries:
			e.entry.delete(0, 'end')
		self.app_name_entry.entry.insert(0, info["display_name"])
		self.version_entry.entry.insert(0, info["version"])
		self.developer_entry.entry.insert(0, info["coder"])
		self.contributors_entry.entry.insert(0, info["contributors"])
		self.release_date_entry.entry.insert(0, info["release_date"])




class description_page(page):
	def __init__(self, *args, **kwargs):
		page.__init__(self, *args, **kwargs)

if __name__ == "__main__":
	w = window()
	w.mainloop()