"""
DIY Electronic Shelf Label Management System
Distributed under the MIT License
© Copyright Maxim Bortnikov 2024
For more information please visit
https://sourceforge.net/projects/esl-management-system/
https://github.com/Northstrix/Electronic-Shelf-Label-Management-System
Required libraries:
https://github.com/me-no-dev/ESPAsyncUDP
https://github.com/adafruit/Adafruit-GFX-Library
https://github.com/adafruit/Adafruit_BusIO
https://github.com/adafruit/Adafruit_ILI9341
https://github.com/adafruit/Adafruit-ST7735-Library
https://github.com/Northstrix/AES_in_CBC_mode_for_microcontrollers
Credit:
https://www.pexels.com/photo/gray-and-black-hive-printed-textile-691710/
https://github.com/nishantprj/custom_tkinter_login
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter
from PIL import ImageTk, Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import sv_ttk
import sqlite3
import random
import string
import numpy as np
import os
import time
import hashlib
import secrets
import socket
from time import sleep

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect('esls.db')
# Create a cursor object
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS ESLs 
                  (id text, label TEXT, encryption_key Text, udp_port_and_ip_address Text)''')

selected_image_path = ""

id_list = []

string_for_data = ""
array_for_CBC_mode = bytearray(16)
back_aes_key = bytearray(32)
decract = 0

aes_key = bytearray([])

image_encryption_key = bytearray([])

def incr_image_encryption_key():
    global image_encryption_key
    i = 15
    while i >= 0:
        if image_encryption_key[i] == 255:
            image_encryption_key[i] = 0
            i -= 1
        else:
            image_encryption_key[i] += 1
            break

def encrypt_iv_for_aes_for_image_encr(iv):
    global array_for_CBC_mode
    array_for_CBC_mode = bytearray(iv)
    encrypt_with_aes_for_image_encr(bytearray(iv))

def encrypt_with_aes_for_image_encr(to_be_encrypted):
    global string_for_data
    global decract
    to_be_encrypted = bytearray(to_be_encrypted)  # Convert to mutable bytearray
    if decract > 0:
        for i in range(16):
            to_be_encrypted[i] ^= array_for_CBC_mode[i]
            
    cipher = AES.new(image_encryption_key, AES.MODE_ECB)
    encrypted_data = cipher.encrypt(pad(to_be_encrypted, AES.block_size))
    incr_image_encryption_key()
    if decract > 0:
        for i in range(16):
            if i < 16:
                array_for_CBC_mode[i] = int(encrypted_data[i])
    
    for i in range(16):
        if encrypted_data[i] < 16:
            string_for_data += "0"
        string_for_data += hex(encrypted_data[i])[2:]
    
    decract += 11

def back_aes_k():
    global back_aes_key
    back_aes_key = bytearray(aes_key)

def rest_aes_k():
    global aes_key
    aes_key = bytearray(back_aes_key)

def incr_aes_key():
    global aes_key
    i = 15
    while i >= 0:
        if aes_key[i] == 255:
            aes_key[i] = 0
            i -= 1
        else:
            aes_key[i] += 1
            break

def encrypt_iv_for_aes(iv):
    global array_for_CBC_mode
    array_for_CBC_mode = bytearray(iv)
    encrypt_with_aes(bytearray(iv))

def encrypt_with_aes(to_be_encrypted):
    global string_for_data
    global decract
    to_be_encrypted = bytearray(to_be_encrypted)  # Convert to mutable bytearray
    if decract > 0:
        for i in range(16):
            to_be_encrypted[i] ^= array_for_CBC_mode[i]
            
    cipher = AES.new(aes_key, AES.MODE_ECB)
    encrypted_data = cipher.encrypt(pad(to_be_encrypted, AES.block_size))
    incr_aes_key()
    if decract > 0:
        for i in range(16):
            if i < 16:
                array_for_CBC_mode[i] = int(encrypted_data[i])
    
    for i in range(16):
        if encrypted_data[i] < 16:
            string_for_data += "0"
        string_for_data += hex(encrypted_data[i])[2:]
    
    decract += 11
    
def decrypt_string_with_aes_in_cbc(ct):
    global decract
    global array_for_CBC_mode
    global string_for_data
    back_aes_k()
    clear_variables()
    ct_bytes = bytes.fromhex(ct)
    ext = 0
    decract = -1
    while len(ct) > ext:
        split_for_decr(ct_bytes, ext)
        ext += 16
        decract += 10

    rest_aes_k()

def split_for_decr(ct, p):
    global decract
    global array_for_CBC_mode
    global string_for_data

    res = bytearray(16)
    prev_res = bytearray(16)
    br = False

    for i in range(0, 16):
        if i + p > len(ct) - 1:
            br = True
            break
        res[i] = ct[i + p]

    for i in range(0, 16):
        if i + p - 16 > len(ct) - 1:
            break  # Skip if index is out of bounds
        prev_res[i] = ct[i + p - 16]

    if not br:
        if decract > 16:
            array_for_CBC_mode = prev_res[:]

        cipher_text = res
        ret_text = bytearray(16)

        cipher = AES.new(bytes(aes_key), AES.MODE_ECB)
        ret_text = bytearray(cipher.decrypt(bytes(cipher_text)))

        incr_aes_key()

        if decract > 2:
            for i in range(16):
                ret_text[i] ^= array_for_CBC_mode[i]

            for byte in ret_text:
                if byte > 0:
                    string_for_data += chr(byte)
                    

        if decract == -1:
            array_for_CBC_mode = ret_text[:]

        decract += 1

def decrypt_hex_str_with_aes_in_cbc(ct):
    global decract
    global array_for_CBC_mode
    global string_for_data
    back_aes_k()
    clear_variables()
    ct_bytes = bytes.fromhex(ct)
    ext = 0
    decract = -1
    while len(ct) > ext:
        split_for_decr_hex_str(ct_bytes, ext)
        ext += 16
        decract += 10

    rest_aes_k()

def split_for_decr_hex_str(ct, p):
    global decract
    global array_for_CBC_mode
    global string_for_data

    res = bytearray(16)
    prev_res = bytearray(16)
    br = False

    for i in range(0, 16):
        if i + p > len(ct) - 1:
            br = True
            break
        res[i] = ct[i + p]

    for i in range(0, 16):
        if i + p - 16 > len(ct) - 1:
            break  # Skip if index is out of bounds
        prev_res[i] = ct[i + p - 16]

    if not br:
        if decract > 16:
            array_for_CBC_mode = prev_res[:]

        cipher_text = res
        ret_text = bytearray(16)

        cipher = AES.new(bytes(aes_key), AES.MODE_ECB)
        ret_text = bytearray(cipher.decrypt(bytes(cipher_text)))

        incr_aes_key()

        if decract > 2:
            for i in range(16):
                ret_text[i] ^= array_for_CBC_mode[i]

            string_for_data += ''.join(format(byte, '02x') for byte in ret_text)
                    

        if decract == -1:
            array_for_CBC_mode = ret_text[:]

        decract += 1

def clear_variables():
    global string_for_data
    global decract
    string_for_data = ""
    decract = 0

def encr_str_with_aes():
    global string_for_data
    global decract
    back_aes_k()
    string_for_data = ""
    decract = 0
    
    iv = [secrets.randbelow(256) for _ in range(16)]  # Initialization vector
    encrypt_iv_for_aes(iv)

def encrypt_string_with_aes_in_cbc(input_string):
    global string_for_data
    global decract
    back_aes_k()
    string_for_data = ""
    decract = 0
    
    iv = [secrets.randbelow(256) for _ in range(16)]  # Initialization vector
    encrypt_iv_for_aes(iv)
    padded_length = (len(input_string) + 15) // 16 * 16
    padded_string = input_string.ljust(padded_length, '\x00')
    byte_arrays = [bytearray(padded_string[i:i+16], 'utf-8') for i in range(0, len(padded_string), 16)]
    
    for i, byte_array in enumerate(byte_arrays):
        encrypt_with_aes(byte_array)
    
    rest_aes_k()
    
def encrypt_hex_str_with_aes_in_cbc(input_string):
    global string_for_data
    global decract
    back_aes_k()
    string_for_data = ""
    decract = 0
    hex_array = bytes.fromhex(input_string)
    iv = [secrets.randbelow(256) for _ in range(16)]  # Initialization vector
    encrypt_iv_for_aes(iv)
    split_arrays = [hex_array[i:i+16] for i in range(0, len(hex_array), 16)]
    for i, arr in enumerate(split_arrays):
        encrypt_with_aes(arr)
    
    rest_aes_k()
    
def encrypt_byte_arr_with_aes_in_cbc(input_arr):
    global string_for_data
    global decract
    back_aes_k()
    string_for_data = ""
    decract = 0
    iv = [secrets.randbelow(256) for _ in range(16)]  # Initialization vector
    encrypt_iv_for_aes(iv)
    encrypt_with_aes(input_arr)
    
    rest_aes_k()
    
def construct_udp_and_ip_address(udp_port_value, ip_address_value):
    udp_and_ip_address = bytearray(16)
    # Extract UDP port characters
    udp_chars = udp_port_value[:min(4, len(udp_port_value))]
    udp_chars_bytes = udp_chars.encode('ascii')
    udp_and_ip_address[:len(udp_chars_bytes)] = udp_chars_bytes
    # Parse IP address into bytes
    ip_bytes = socket.inet_aton(ip_address_value)
    udp_and_ip_address[4:8] = ip_bytes
    # Generate random bytes for the remaining part
    random_bytes = bytearray(secrets.randbits(8) for _ in range(8))
    udp_and_ip_address[8:] = random_bytes
    return udp_and_ip_address

def hex_string_to_udp_port(hex_str):
    # Convert hex string to a bytearray
    byte_array = bytearray.fromhex(hex_str)
    
    # Extract the first four bytes and convert them to a string
    udp_port_bytes = byte_array[:4]
    udp_port_str = ''.join(chr(byte) for byte in udp_port_bytes)
    
    return udp_port_str

def hex_string_to_ip_address(hex_str):
    # Convert hex string to a bytearray
    byte_array = bytearray.fromhex(hex_str)

    # Extract elements 5 to 8 from the array
    ip_bytes = byte_array[4:8]

    # Convert the extracted bytes to an IP address string
    ip_address_str = '.'.join(str(byte) for byte in ip_bytes)

    return ip_address_str

class App(ttk.Frame):
    def __init__(self, parent, image):
        ttk.Frame.__init__(self)
        self.image = image
        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create widgets :)
        self.setup_widgets()
        self.refresh_treeview()
        global photo
        photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo  # Keep a reference to prevent garbage collection

    def setup_widgets(self):
        # Create a Frame for input widgets
        self.widgets_frame = ttk.Frame(self, padding=(0, 0, 0, 10))
        self.widgets_frame.grid(
            row=0, column=1, padx=10, pady=(30, 10), sticky="nsew", rowspan=2
        )
        
        self.button = ttk.Button(self.widgets_frame, text="Send Image To Wireless Display", command=self.send_image)
        self.button.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
        
        self.accentbutton = ttk.Button(
            self.widgets_frame, text="Edit Wireless Display Settings", style="Accent.TButton", command=self.edit_esl_settings
        )
        self.accentbutton.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")
        
        self.button = ttk.Button(self.widgets_frame, text="Remove Wireless Display From DB", command=self.remove_esl)
        self.button.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        self.accentbutton = ttk.Button(
            self.widgets_frame, text="About Wireless Display Handler Part", style="Accent.TButton", command=about_eslms
        )
        self.accentbutton.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")
        
        # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(row=0, column=2, pady=(25, 5), sticky="nsew", rowspan=3)

        # Pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_1, weight=1)

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.pane_1)
        self.scrollbar.pack(side="right", fill="y")

        # Treeview
        self.treeview = ttk.Treeview(
            self.pane_1,
            selectmode="browse",
            yscrollcommand=self.scrollbar.set,
            columns=(1, ),
            height=10,
        )
        
        self.treeview.pack(expand=True, fill="both")
        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview.column("#0", anchor="w", width=100)
        self.treeview.column(1, anchor="w", width=340)

        # Treeview headings
        self.treeview.heading("#0", text="  IP", anchor="w")
        self.treeview.heading(1, text="  Label", anchor="w")

        # Notebook, pane #2
        self.pane_2 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_2, weight=3)

        # Notebook, pane #2
        self.notebook = ttk.Notebook(self.pane_2)
        self.notebook.pack(fill="both", expand=True)
        
        # Tab #1
        self.tab_1 = ttk.Frame(self.notebook)
        for index in [0, 1]:
            self.tab_1.columnconfigure(index=index, weight=1)
            self.tab_1.rowconfigure(index=index, weight=1)
        self.notebook.add(self.tab_1, text="Preview")
        
        #self.bg_image = Image.open("./assets/pattern.jpg")
        #self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        #self.bg_label = tk.Label(self.tab_1, image=self.bg_photo)
        #self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Create a Canvas on Tab #1
        self.canvas = tk.Canvas(self.tab_1, width=320, height=240, highlightthickness=0, borderwidth=0)
        self.canvas.pack()

        # Tab #2
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Add Wireless Display")
        
        # Labels for entries
        label_1 = ttk.Label(self.tab_2, text=" Label: ")
        label_1.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        label_2 = ttk.Label(self.tab_2, text=" Encryption Key: ")
        label_2.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        label_3 = ttk.Label(self.tab_2, text=" UDP Port: ")
        label_3.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        label_4 = ttk.Label(self.tab_2, text=" IP Address: ")
        label_4.grid(row=3, column=0, padx=5, pady=5, sticky="e")

        # Entries
        self.entry_1 = ttk.Entry(self.tab_2)
        self.entry_1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.entry_2 = ttk.Entry(self.tab_2)
        self.entry_2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.entry_3 = ttk.Entry(self.tab_2)
        self.entry_3.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.entry_4 = ttk.Entry(self.tab_2)
        self.entry_4.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        # Buttons
        button_clear = ttk.Button(self.tab_2, text="Clear", command=self.clear_fields)
        button_clear.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        button_add = ttk.Button(self.tab_2, text="Add", style="Accent.TButton", command=self.on_add_button_click)
        button_add.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Bind treeview selection event
        self.treeview.bind("<<TreeviewSelect>>", self.on_treeview_select)

    def on_treeview_select(self, event):
        global selected_image_path
        # Get the selected item's ID
        selected_items = self.treeview.selection()
        if selected_items:
            selected_index = self.treeview.index(selected_items[0])
            selected_id = id_list[selected_index]

    def send_image(self):
        selected_items = self.treeview.selection()
        if selected_items:       
            global image_encryption_key
            global string_for_data
            selected_index = self.treeview.index(selected_items[0])
            selected_id = id_list[selected_index]
            cursor.execute("SELECT encryption_key FROM ESLs WHERE id=?", (selected_id,))
            decrypt_hex_str_with_aes_in_cbc(cursor.fetchone()[0])
            encryption_key_hex = string_for_data
            # Convert encryption key from hexadecimal string to bytes
            encryption_key_bytes = bytes.fromhex(encryption_key_hex)
            # Replace data in aes_key with encryption_key_bytes
            image_encryption_key[:len(encryption_key_bytes)] = encryption_key_bytes
            # Open the selected image
            img = self.image
            width, height = img.size[:2]
            px = np.array(img)
            px_bytes = px.tobytes()
            print("Encrypting the image and sending it to the Wireless Display...")
            cursor.execute("SELECT udp_port_and_ip_address FROM ESLs WHERE id=?", (selected_id,))
            decrypt_hex_str_with_aes_in_cbc(cursor.fetchone()[0])
            udp_port_and_ip_addr = string_for_data
            chsn_hex_udp_port = hex_string_to_udp_port(udp_port_and_ip_addr)
            chsn_int_udp_port = int(chsn_hex_udp_port, 16)
            chsn_ip = hex_string_to_ip_address(udp_port_and_ip_addr)
            #print("Hex UDP Port: ", chsn_hex_udp_port)
            #print("Int UDP Port: ", chsn_int_udp_port)
            #print("IP Address: ", chsn_ip)
            print("Please, wait for a while")
            byteList = bytearray()
            byteList.clear()
            udp_socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket1.sendto(b'\x01', (chsn_ip, chsn_int_udp_port))
            udp_socket1.close()
            sleep(0.31)
            #Print each pixel to the console
            for i in range(height):
                global decract
                string_for_data = ""
                decract = 0
                iv = [secrets.randbelow(256) for _ in range(16)]
                encrypt_iv_for_aes_for_image_encr(iv)
                for j in range(width):
                    pixel = px[i, j]
                    # Extract RGB components
                    r = pixel[0]
                    g = pixel[1]
                    b = pixel[2]
                    # Convert to 565 format
                    r_565 = (r >> 3) & 0x1F
                    g_565 = (g >> 2) & 0x3F
                    b_565 = (b >> 3) & 0x1F
                    # Combine RGB components into a single 16-bit value
                    color_565 = (r_565 << 11) | (g_565 << 5) | b_565
                    byte_1 = color_565 & 0xFF
                    byte_2 = (color_565 >> 8) & 0xFF
                    #print(i, j, color_565, byte_1, byte_2)
                    byteList.append(byte_1)
                    byteList.append(byte_2)
                    if len(byteList) == 16:
                        # Print all elements to the serial terminal
                        #for byte in byteList:
                            #print(hex(byte), end=' ')
                        encrypt_with_aes_for_image_encr(byteList)
                        byteList.clear()
                    if len(string_for_data) == 1312:
                        #hex_string = ' '.join(format(byte, '02x') for byte in image_encryption_key)
                        #print(hex_string)
                        #print(string_for_data, ' ', str(i))
                        image_encryption_key[:len(encryption_key_bytes)] = encryption_key_bytes
                        print("Progress: " + '{0:.2f}'.format(((i + 1)/ 241) * 100) + "%")
                        encrypted_line = bytes.fromhex(string_for_data)
                        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        try:
                            # Send the UDP packet
                            udp_socket.sendto(encrypted_line, (chsn_ip, chsn_int_udp_port))
                            print("UDP packet with the encrypted line N", str(i + 1), " sent successfully!")
                        except Exception as e:
                            print("Error:", e)
                        finally:
                            # Close the socket
                            udp_socket.close()
                        sleep(0.5)
            print("Progress: 100.00%")
        else:
            messagebox.showwarning("Warning", "Select a wireless display to continue.")

    def edit_esl_settings(self):
        selected_items = self.treeview.selection()
        if selected_items:
            global id_list
            selected_index = self.treeview.index(selected_items[0])
            selected_id = id_list[selected_index]
            selected_label = self.treeview.item(selected_items[0], "values")[0]

            # Open a new window for editing
            edit_window = EditForm(self, selected_id, selected_label)
            self.wait_window(edit_window)  # Wait for the edit window to close
        else:
            messagebox.showwarning("Warning", "Select a wireless display to continue.")

    def remove_esl(self):
        selected_items = self.treeview.selection()
        if selected_items:
            confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to remove this record from the database?")
            if confirmation:
                global id_list
                selected_index = self.treeview.index(selected_items[0])
                selected_id = id_list[selected_index]
                self.delete_record_from_database(selected_id)
                # Refresh the treeview
                self.refresh_treeview()
            else:
                messagebox.showinfo("Operation Cancelled", "Operation was cancelled by user.")
        else:
            messagebox.showwarning("Warning", "Select a wireless display to continue.")
            
    def delete_record_from_database(self, id_value):
        # Delete the record from the database based on the provided ID
        cursor.execute("DELETE FROM ESLs WHERE id=?", (id_value,))
        # Commit the transaction
        conn.commit()

    def clear_treeview(self):
        # Clear all items from the treeview
        self.treeview.delete(*self.treeview.get_children())
        
    def add_to_treeview(self, id_value, label_value):
        self.treeview.insert("", "end", text=id_value, values=(label_value,))
        
    def clear_fields(self):
        # Clear all entry fields
        self.entry_1.delete(0, tk.END)
        self.entry_2.delete(0, tk.END)
        self.entry_3.delete(0, tk.END)
        self.entry_4.delete(0, tk.END)

    def generate_random_id(self):
        # Generate a random ID of length 10 consisting of numbers, lowercase, and uppercase letters
        characters = string.ascii_letters + string.digits
        generated_id = ''.join(random.choice(characters) for i in range(8))
        return generated_id

    def check_id_existence(self, id_value):
        # Check if the ID already exists in the database
        cursor.execute("SELECT id FROM ESLs WHERE id=?", (id_value,))
        existing_id = cursor.fetchone()
        return existing_id is not None
    
    def on_add_button_click(self):
        # Extract data from the entry fields
        label_value = self.entry_1.get()
        encryption_key_value = self.entry_2.get()
        udp_port_value = self.entry_3.get()
        ip_address_value = self.entry_4.get()

        # Check if the label_value is empty
        if not label_value.strip():
            tk.messagebox.showwarning("Warning", "Label value cannot be empty.")
            return

        # Remove characters from encryption_key_value that don't fit in the range of ascii value 48-102
        encryption_key_value = ''.join(c for c in encryption_key_value if 48 <= ord(c) <= 102)

        # Check if the encryption_key_value is a hexadecimal string with exactly 64 characters
        if len(encryption_key_value) != 64 or not all(c in string.hexdigits for c in encryption_key_value):
            tk.messagebox.showwarning("Warning", "Encryption key must be a hexadecimal string with exactly 64 characters.")
            return

        # Check if the udp_port_value has exactly 4 characters
        if len(udp_port_value) != 4:
            tk.messagebox.showwarning("Warning", "UDP port value must have exactly 4 characters.")
            return

        # Check if the ip_address_value is a valid IP address
        if not self.is_valid_ip(ip_address_value):
            tk.messagebox.showwarning("Warning", "Invalid IP address.")
            return

        generated_id = self.generate_random_id()
        # Check if the generated ID already exists in the database
        while self.check_id_existence(generated_id):
            # If record with the generated ID already exists, generate a new ID and check again
            generated_id = self.generate_random_id()

        # Add the record to the database
        udp_and_ip_address = construct_udp_and_ip_address(udp_port_value, ip_address_value)
        encrypt_string_with_aes_in_cbc(label_value)
        encrypted_label = string_for_data
        encrypt_hex_str_with_aes_in_cbc(encryption_key_value)
        encrypted_key = string_for_data
        encrypt_byte_arr_with_aes_in_cbc(udp_and_ip_address)
        encrypted_udp_ip = string_for_data
        self.add_record_to_database(generated_id, encrypted_label, encrypted_key, encrypted_udp_ip)
        # Inform the user that the record has been added
        tk.messagebox.showinfo("Success", "Record added to the database.")
        self.refresh_treeview()

    def add_record_to_database(self, id_value, label_value, encryption_key_value, udp_port_and_ip_address_value):
        # Insert the record into the database
        cursor.execute("INSERT INTO ESLs (id, label, encryption_key, udp_port_and_ip_address) VALUES (?, ?, ?, ?)",
                       (id_value, label_value, encryption_key_value, udp_port_and_ip_address_value))
        # Commit the transaction
        conn.commit()

    def is_valid_ip(self, ip):
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False
        return True

    def print_list_with_indexes(lst):
        for index, element in enumerate(lst):
            print(f"Index: {index}, Element: {element}")

    def refresh_treeview(self):
        # Clear the treeview
        self.clear_treeview()
        # Retrieve all records from the database
        cursor.execute("SELECT id, udp_port_and_ip_address, label FROM ESLs")
        records = cursor.fetchall()
        global id_list
        id_list.clear()
        # Add each record to the treeview
        for record in records:
            record_id, udp_ip_value, label_value = record
            id_list.append(record_id)
            decrypt_string_with_aes_in_cbc(label_value)
            decrypted_label = string_for_data
            decrypt_hex_str_with_aes_in_cbc(udp_ip_value)
            decrypted_udp_and_ip = string_for_data
            self.add_to_treeview(hex_string_to_ip_address(decrypted_udp_and_ip), decrypted_label)
        #for index, element in enumerate(id_list):
            #print(f"Index: {index}, Element: {element}")
            
class EditForm(tk.Toplevel):
    def __init__(self, parent, selected_id, selected_label):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.selected_id = selected_id
        self.title("Edit ESL Settings")
        self.geometry("259x191")
        self.resizable(True, True)  # Allow the window to be resizable
        self.position_window()  # Center the window on the screen

        self.label = ttk.Label(self, text="Label:")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.label_entry = ttk.Entry(self)
        self.label_entry.insert(0, selected_label)
        self.label_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.encryption_key = ttk.Label(self, text="Encryption Key:")
        self.encryption_key.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        cursor.execute("SELECT encryption_key FROM ESLs WHERE id=?", (selected_id,))
        decrypt_hex_str_with_aes_in_cbc(cursor.fetchone()[0])
        encryption_key = string_for_data

        self.encryption_key_entry = ttk.Entry(self)
        self.encryption_key_entry.insert(0, encryption_key)
        self.encryption_key_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        cursor.execute("SELECT udp_port_and_ip_address FROM ESLs WHERE id=?", (selected_id,))
        decrypt_hex_str_with_aes_in_cbc(cursor.fetchone()[0])
        udp_port_and_ip_addr = string_for_data

        self.udp_port = ttk.Label(self, text="UDP Port:")
        self.udp_port.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.udp_port_entry = ttk.Entry(self)
        self.udp_port_entry.insert(0, hex_string_to_udp_port(udp_port_and_ip_addr))
        self.udp_port_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        self.ip_address = ttk.Label(self, text="IP Address:")
        self.ip_address.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.ip_address_entry = ttk.Entry(self)
        self.ip_address_entry.insert(0, hex_string_to_ip_address(udp_port_and_ip_addr))
        self.ip_address_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        self.update_button = ttk.Button(self, text="Update", style="Accent.TButton", command=self.update_record)
        self.update_button.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.destroy)
        self.cancel_button.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    def update_record(self):
        label_value = self.label_entry.get()
        encryption_key_value = self.encryption_key_entry.get()
        udp_port_value = self.udp_port_entry.get()
        ip_address_value = self.ip_address_entry.get()

        # Check if the label_value is empty
        if not label_value.strip():
            tk.messagebox.showwarning("Warning", "Label value cannot be empty.")
            return

        # Remove characters from encryption_key_value that don't fit in the range of ascii value 48-102
        encryption_key_value = ''.join(c for c in encryption_key_value if 48 <= ord(c) <= 102)

        # Check if the encryption_key_value is a hexadecimal string with exactly 64 characters
        if len(encryption_key_value) != 64 or not all(c in string.hexdigits for c in encryption_key_value):
            tk.messagebox.showwarning("Warning", "Encryption key must be a hexadecimal string with exactly 64 characters.")
            return

        # Check if the udp_port_value has exactly 4 characters
        if len(udp_port_value) != 4:
            tk.messagebox.showwarning("Warning", "UDP port value must have exactly 4 characters.")
            return

        # Check if the ip_address_value is a valid IP address
        if not self.parent.is_valid_ip(ip_address_value):
            tk.messagebox.showwarning("Warning", "Invalid IP address.")
            return

        # Add the record to the database
        udp_and_ip_address = construct_udp_and_ip_address(udp_port_value, ip_address_value)
        encrypt_string_with_aes_in_cbc(label_value)
        encrypted_label = string_for_data
        encrypt_hex_str_with_aes_in_cbc(encryption_key_value)
        encrypted_key = string_for_data
        encrypt_byte_arr_with_aes_in_cbc(udp_and_ip_address)
        encrypted_udp_ip = string_for_data
        # Update the record in the database
        cursor.execute("UPDATE ESLs SET label=?, encryption_key=?, udp_port_and_ip_address=? WHERE id=?", (encrypted_label, encrypted_key, encrypted_udp_ip, self.selected_id))
        conn.commit()
        tk.messagebox.showinfo("Success", "Record edited successfully.")
        # Refresh the treeview in the main window
        self.parent.refresh_treeview()
        self.destroy()

    def position_window(self):
        # Center the window on the screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if not content:  # Check if the content is empty
                return None
            return content
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if not content:  # Check if the content is empty
                return None
            return content
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def generate_random_ascii_string(length):
    # Define the pool of characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation
    # Generate a random string by selecting characters from the pool
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

def launch_w_display_manager(root, image):
    db_encryption_key = read_file_content("db_encryption_key")
    if db_encryption_key is None:
        random_hex_string = generate_random_ascii_string(64)
        create_file("db_encryption_key", random_hex_string)
        db_encryption_key = read_file_content("db_encryption_key")
        
    hashed_key = hashlib.sha512(db_encryption_key.encode()).hexdigest()
    #print("Hashed Password:", hashed_key)    
    # Split the hashed password into two halves
    first_half = hashed_key[:64]
    second_half = hashed_key[64:]
    # Update the aes_key with the first half
    global aes_key
    aes_key = bytearray.fromhex(second_half)
    launch_app(root, image)
    
def launch_app(root, image):
    # Create the application instance
    app = App(root, image)
    app.pack(fill="both", expand=True)

    # Set the geometry of the root window
    root.geometry("1060x800")
    
    root.update()
    # Set the minimum size of the root window
    root.minsize(root.winfo_width(), root.winfo_height())

    # Start the main event loop
    root.mainloop()
    
def create_file(file_path, content):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error occurred while creating the file: {e}")
        return False

def about_eslms():
    custom_form = tk.Tk()
    custom_form.title("About Wireless Display Handler Part")
    custom_form.configure(bg="#7B08A5")

    label = tk.Label(custom_form,
                     text="This software is a part of the ESL Management System V2.0\n"
                          "You are free to modify and distribute copies of this software.\n"
                          "You can use this software, as well as firmware for ESP8266\n"
                          "in commercial applications.\n\n"
                          "The firmware for the ESP8266 and the ESL management software are available at:\n\n"
                          "SourceForge",
                     fg="#E4E3DF",
                     font=("Segoe UI", 12, "bold"),
                     wraplength=700,
                     justify="center",
                     bg="#7B08A5")
    label.grid(row=0, column=0, padx=10, pady=10)

    text_field = tk.Entry(custom_form,
                          width=80,
                          font=("Segoe UI", 14, "bold"),
                          bg="#7B08A5",
                          fg="#E4E3DF",
                          readonlybackground="#7B08A5")
    text_field.insert(0, "sourceforge.net/projects/esl-management-system/")
    text_field.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    text_field.config(state='readonly')

    label1 = tk.Label(custom_form,
                      text="Github",
                      fg="#E4E3DF",
                      font=("Segoe UI", 12, "bold"),
                      bg="#7B08A5")
    label1.grid(row=2, column=0, padx=10, pady=10)

    text_field1 = tk.Entry(custom_form,
                           width=80,
                           font=("Segoe UI", 14, "bold"),
                           bg="#7B08A5",
                           fg="#E4E3DF",
                           readonlybackground="#7B08A5")
    text_field1.insert(0, "github.com/Northstrix/Electronic-Shelf-Label-Management-System")
    text_field1.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
    text_field1.config(state='readonly')

    label2 = tk.Label(custom_form,
                      text="Copyright \u00a9 2024 Maxim Bortnikov",
                      fg="#E4E3DF",
                      font=("Segoe UI", 12, "bold"),
                      bg="#7B08A5")
    label2.grid(row=6, column=0, padx=10, pady=10)

    def close_window():
        custom_form.destroy()

    continue_button = tk.Button(custom_form,
                                text="Got It",
                                width=15,
                                height=2,
                                bg="#4113AA",
                                fg="#E4E3DF",
                                command=close_window,
                                font=("Segoe UI", 12, "bold"),
                                relief="flat")
    continue_button.grid(row=7, column=0, padx=10, pady=10)
    
    custom_form.mainloop()