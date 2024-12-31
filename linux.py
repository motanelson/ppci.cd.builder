from io import StringIO
from ppci.api import ir_to_object, get_arch,objcopy, link
import io
from ppci.api import cc
from ppci.api import asm
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter import filedialog, messagebox
import subprocess
import shutil
import os
from pycdlib import PyCdlib
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

class FSProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FS to ISO Creator")
        self.root.geometry("400x200")
        self.root.configure( bg="yellow")
        
        # Dados carregados do arquivo .fs
        self.system_config=""
        self.system_name=""
        self.files_to_exe=b''
        self.files_to_process = None        
        # Botão para carregar arquivo .fs
        self.load_button = tk.Button(
            root, text="Load .fs File", command=self.load_fs_file, bg="black", fg="yellow")
        self.load_button.pack(pady=10)
        
        # Botão para criar arquivo .iso
        self.save_button = tk.Button(
            root, text="Save as .iso", command=self.save_iso_file, bg="black", fg="yellow")
        self.save_button.pack(pady=10)
        
        # Rótulo de status
        self.status_label = tk.Label(
            root, text="",  bg="black", fg="yellow", wraplength=350
        )
        self.status_label.pack(pady=10)
    def execute_command(self, command,show:bool):
        try:
            
            result = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, text=True)
            result = result.strip()
            if show and result!="":
                messagebox.showerror("error:",result)
        except subprocess.CalledProcessError as e:
            if show:
                messagebox.showerror("error:",e)
    def load_fs_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("c Files", "*.c"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            f1=open(file_path,"r")
            codes=f1.read()
            f1.close()
          
            
            source_file2 = io.StringIO(codes)
            obj3 = cc(source_file2, 'x86_64')
            obj=link([obj3],"link.ld")
        except Exception as e:
             messagebox.showerror("Error", f"Failed to load .fs file: {e}")
        else:
    
             objcopy(obj,"code", 'bin',"hello.c32")
        try:
            system_name=file_path
            splitdir=file_path.split("/")
            file_path=splitdir[len(splitdir)-1]
            
            

            self.system_name="SYSTEM"
            print(file_path)
            self.execute_command("cp mysys.dat mysys.o",False)
            

            self.execute_command("cat mysys.o hello.c32 > sys.bin",False)
            
            with open("sys.bin", "rb") as f:
                content = f.read()
                self.files_to_process=content
                self.files_to_exe = content
                       
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load .fs file: {e}")
            self.status_label.config(text="Failed to load .fs file.")

    def save_iso_file(self):
        
       
        f1=open("hello.c32","wb")
        f1.write(self.files_to_exe)
        f1.close()
        save_path = filedialog.asksaveasfilename(
            defaultextension=".iso", filetypes=[("ISO Files", "*.iso"), ("All Files", "*.*")]
        )
        if not save_path:
            return
        
        try:
            iso = PyCdlib()
            iso.new()

            # Adicionar os arquivos ao ISO
            bootstr = self.files_to_process            
            iso.add_fp(BytesIO(bootstr), len(bootstr), '/BOOT.;1')

            iso.add_eltorito('/BOOT.;1')
           
            iso.add_directory('/BOOT')
            
            iso.add_directory('/BOOT/GRUB')
            
            iso.add_directory('/BOOT/'+self.system_name+"")
            
            bootstr =self.files_to_process
            iso.add_fp(BytesIO(bootstr), len(bootstr), '/BOOT/'+self.system_name+"/"+self.system_name+".BIN")
            
            iso.write(save_path)
            iso.close()

            messagebox.showinfo("Success", f"ISO file saved at {save_path}")
            self.status_label.config(text="ISO file created successfully.")
            fff=f'qemu-system-x86_64 -cdrom "$1"'.replace("$1",save_path)
            self.execute_command(fff,False)


        except Exception as e:
            messagebox.showerror("Error", f"Failed to create ISO file: {e}")
            self.status_label.config(text="Failed to create ISO file.")

if __name__ == "__main__":
    root = tk.Tk()
    app = FSProcessorApp(root)
    root.mainloop()

