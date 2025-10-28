import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk
import subprocess
import os

class SimpleCodeEditor:
    """A simple code editor built with Python's Tkinter."""
    
    # Simple regex-like definitions for basic syntax highlighting
    KEYWORDS = {
        '.py': ['def', 'class', 'if', 'else', 'elif', 'for', 'while', 'import', 'from', 'return', 'try', 'except', 'with', 'as', 'lambda', 'True', 'False', 'None'],
        '.js': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'try', 'catch', 'class', 'import', 'export', 'default'],
        '.jsx': ['function', 'const', 'let', 'var', 'if', 'else', 'for', 'while', 'return', 'try', 'catch', 'class', 'import', 'export', 'default', 'React', 'Component'],
        '.html': ['html', 'head', 'body', 'div', 'span', 'p', 'a', 'img', 'script', 'style', 'link', 'meta'],
        '.css': ['body', 'div', 'class', 'id', 'margin', 'padding', 'color', 'background']
    }
    
    FUNCTIONS = {
        '.py': ['print', 'range', 'len', 'list', 'dict', 'set', 'tuple', 'str', 'int', 'float'],
        '.js': ['console.log', 'setTimeout', 'setInterval', 'fetch', 'map', 'filter', 'reduce'],
        '.jsx': ['render', 'useState', 'useEffect', 'useContext', 'createElement', 'Component'],
        '.html': [],
        '.css': []
    }
    
    def __init__(self, master):
        """Initializes the main application window and components."""
        self.master = master
        master.title("SimpleCode Editor")
        
        # --- Menu Bar Setup ---
        self.create_menu_bar()
        
        # Create main container
        self.main_container = tk.PanedWindow(master, orient=tk.VERTICAL)
        self.main_container.pack(fill='both', expand=True)

        # Upper section for editor
        self.editor_frame = tk.Frame(self.main_container)
        self.main_container.add(self.editor_frame)
        
        # Main frame to hold line numbers and code area side-by-side
        main_frame = tk.Frame(self.editor_frame)
        main_frame.pack(fill='both', expand=True)
        
        # Line Numbers
        self.line_numbers = tk.Text(main_frame, width=4, padx=3, bd=0,
                                     background='#333333', foreground='#999999',
                                     state='disabled', wrap='none', font=('Consolas', 10))
        self.line_numbers.pack(side='left', fill='y')
        
        # Code Area with Scrollbar
        self.scrollbar = tk.Scrollbar(main_frame)
        self.scrollbar.pack(side='right', fill='y')
     
        self.code_text = tk.Text(main_frame, wrap='word', undo=True,
                                  yscrollcommand=self.scrollbar.set,
                                  font=('Consolas', 10),
                                  background='#1e1e1e', foreground='#d4d4d4',
                                  insertbackground='white')
        self.code_text.pack(side='right', fill='both', expand=True)
     
        self.scrollbar.config(command=self.code_text.yview)
        
        # Lower section for command prompt
        self.lower_frame = tk.Frame(self.main_container)
        self.main_container.add(self.lower_frame, height=150)
        
        # Command prompt output
        self.cmd_output = tk.Text(self.lower_frame, height=10,
                                   background='#0C0C0C', foreground='#CCCCCC',
                                   font=('Consolas', 9))
        self.cmd_output.pack(fill='both', expand=True)
        
        # Command input frame
        self.cmd_input_frame = tk.Frame(self.lower_frame, background='#0C0C0C')
        self.cmd_input_frame.pack(fill='x')
        
        # Command prompt label
        self.cmd_label = tk.Label(self.cmd_input_frame, text=">",
                                   background='#0C0C0C', foreground='#CCCCCC')
        self.cmd_label.pack(side='left')
        
        # Command input
        self.cmd_input = tk.Entry(self.cmd_input_frame, background='#0C0C0C',
                                   foreground='#CCCCCC', insertbackground='#CCCCCC')
        self.cmd_input.pack(side='left', fill='x', expand=True)
        self.cmd_input.bind('<Return>', self.execute_command)
  
        # Status bar
        self.status_bar = tk.Label(master, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
        # Current file path and type
        self.current_file = None
        self.current_file_type = '.py'  # Default to Python
        
        # Initialize highlighting
        self.setup_highlighting_tags()
        self.update_line_numbers()
        
        # Bindings
        self.code_text.bind('<KeyRelease>', self.on_text_change)
        self.code_text.bind('<MouseWheel>', self.on_text_change)
        self.code_text.bind('<Return>', self.auto_indent)
        self.master.bind('<Control-f>', self.open_search_replace)
        self.master.bind('<Command-f>', self.open_search_replace)

    def create_menu_bar(self):
        """Creates the menu bar with standard options."""
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)
        
        # File Menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_command(label="Save As...", command=self.save_file_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.confirm_exit)

        # Edit Menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Cut", command=lambda: self.code_text.event_generate("<<Cut>>"))
        self.edit_menu.add_command(label="Copy", command=lambda: self.code_text.event_generate("<<Copy>>"))
        self.edit_menu.add_command(label="Paste", command=lambda: self.code_text.event_generate("<<Paste>>"))
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Find/Replace", command=lambda: self.open_search_replace(None))
        
        # View Menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Toggle Command Prompt", command=self.toggle_command_prompt)
        
        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
    
        # Bind keyboard shortcuts
        self.master.bind('<Control-n>', lambda e: self.new_file())
        self.master.bind('<Control-o>', lambda e: self.open_file())
        self.master.bind('<Control-s>', lambda e: self.save_file())

    def execute_command(self, event=None):
        """Executes the command entered in the command prompt."""
        command = self.cmd_input.get()
        self.cmd_input.delete(0, tk.END)
        
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, universal_newlines=True)
            output, error = process.communicate()

            self.cmd_output.insert(tk.END, f"> {command}\n")
            if output:
                self.cmd_output.insert(tk.END, output)
            if error:
                self.cmd_output.insert(tk.END, error)
            self.cmd_output.insert(tk.END, "\n")
            self.cmd_output.see(tk.END)
        except Exception as e:
            self.cmd_output.insert(tk.END, f"Error: {str(e)}\n")
   
        self.update_status_bar(f"Command executed: {command}")

    def toggle_command_prompt(self):
        """Toggles the visibility of the command prompt."""
        if self.lower_frame.winfo_viewable():
            self.main_container.forget(self.lower_frame)
            self.update_status_bar("Command prompt hidden")
        else:
            self.main_container.add(self.lower_frame, height=150)
            self.update_status_bar("Command prompt shown")

    def update_status_bar(self, message):
        """Updates the status bar with a message."""
        self.status_bar.config(text=message)

    def new_file(self):
        """Creates a new empty file."""
        if self.check_save_current():
            self.code_text.delete('1.0', tk.END)
            self.current_file = None
            self.current_file_type = '.py'  # Default to Python
            self.master.title("SimpleCode Editor - New File")
            self.on_text_change()
            self.update_status_bar("New file created")

    def open_file(self):
        """Opens a file for editing."""
        if self.check_save_current():
            file_path = filedialog.askopenfilename(
                filetypes=[
                    ("Python files", "*.py;*.pyw"),
                    ("JavaScript files", "*.js"),
                    ("React files", "*.jsx"),
                    ("HTML files", "*.html"),
                    ("CSS files", "*.css"),
                    ("All files", "*.*")
                ]
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    self.code_text.delete('1.0', tk.END)
                    self.code_text.insert('1.0', content)
                    self.current_file = file_path
                    self.current_file_type = os.path.splitext(file_path)[1]
                    self.master.title(f"SimpleCode Editor - {file_path}")
                    self.on_text_change()
                    self.update_status_bar(f"Opened: {file_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")

    def save_file(self):
        """Saves the current file."""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Saves the current file with a new name."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=self.current_file_type,
            filetypes=[
                ("Python files", "*.py;*.pyw"),
                ("JavaScript files", "*.js"),
                ("React files", "*.jsx"),
                ("HTML files", "*.html"),
                ("CSS files", "*.css"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self._save_to_file(file_path)
            self.current_file_type = os.path.splitext(file_path)[1]
            self.update_status_bar(f"Saved as: {file_path}")

    def _save_to_file(self, file_path):
        """Helper method to save content to a file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                content = self.code_text.get('1.0', tk.END)
                file.write(content)
            self.current_file = file_path
            self.master.title(f"SimpleCode Editor - {file_path}")
            self.update_status_bar(f"Saved: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")

    def check_save_current(self):
        """Checks if current file needs saving before proceeding."""
        if self.code_text.edit_modified():
            response = messagebox.askyesnocancel(
                "Save Changes?",
                "Do you want to save changes to the current file?"
            )
            if response is None:  # Cancel
                return False
            elif response:  # Yes
                return self.save_file()
        return True

    def confirm_exit(self):
        """Confirms if the user wants to exit and handles saving."""
        if self.check_save_current():
            self.master.quit()

    def show_about(self):
        """Shows the about dialog."""
        about_text = """SimpleCode Editor
Version 1.0

A lightweight code editor with syntax highlighting
for Python, JavaScript, React, HTML, and CSS files.
Includes integrated command prompt and status bar.

Created with Python and Tkinter."""
        
        about_window = tk.Toplevel(self.master)
        about_window.title("About SimpleCode Editor")
        about_window.geometry("300x200")
        about_window.resizable(False, False)
        about_window.transient(self.master)
        about_window.grab_set()
        
        # Center the window
        about_window.geometry("+%d+%d" % (
            self.master.winfo_rootx() + 50,
            self.master.winfo_rooty() + 50
        ))
        
        label = tk.Label(about_window, text=about_text, padx=20, pady=20,
                         justify=tk.CENTER)
        label.pack(expand=True)
        
        ok_button = tk.Button(about_window, text="OK",
                              command=about_window.destroy)
        ok_button.pack(pady=10)

    def setup_highlighting_tags(self):
        """Creates the text tags for syntax highlighting colors."""
        self.code_text.tag_configure('keyword', foreground='#569cd6')  # Blue
        self.code_text.tag_configure('function', foreground='#dcdcaa')  # Yellow-Green
        self.code_text.tag_configure('string', foreground='#ce9178')   # Orange/Brown
        self.code_text.tag_configure('comment', foreground='#6a9955')  # Green
        self.code_text.tag_configure('default', foreground='#d4d4d4')  # Default light gray

    def on_text_change(self, event=None):
        """Called on any text change or scroll to update the line numbers and highlighting."""
        self.update_line_numbers()
        self.apply_highlighting()

    def update_line_numbers(self):
        """Updates the line numbers in the gutter."""
        final_index = self.code_text.index("end-1c")
        num_of_lines = int(final_index.split('.')[0])
        line_numbers_text = '\n'.join(str(i) for i in range(1, num_of_lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')

    def apply_highlighting(self):
        """Applies syntax highlighting based on the current file type."""
        # Implementation of syntax highlighting goes here
        pass

    def auto_indent(self, event):
        """Handles auto-indentation when Enter is pressed."""
        # Get the current line's indentation
        current_line = self.code_text.get("insert linestart", "insert")
        indent = len(current_line) - len(current_line.lstrip())
        indent_str = current_line[:indent]
        
        # Check if the line ends with a colon (for blocks)
        if current_line.rstrip().endswith(':'):
            indent_str += '    '  # Add an extra level of indentation
        
        self.code_text.insert("insert", f"\n{indent_str}")
        return "break"  # Prevent the default Enter behavior

    def open_search_replace(self, event=None):
        """Opens a search and replace dialog."""
        # Placeholder for search/replace functionality
        simpledialog.askstring("Find/Replace", "Feature coming soon!")


# Main execution
if __name__ == '__main__':
    root = tk.Tk()
    editor = SimpleCodeEditor(root)
    root.mainloop()
