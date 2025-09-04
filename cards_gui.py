import tkinter as tk
from tkinter import Listbox, StringVar, Entry, Button, Frame, Label, messagebox
import sqlite3
from fpdf import FPDF
from pdf2image import convert_from_path
from PIL import ImageTk
import qrcode
import time
import os
import csv
import subprocess
import platform

DB_PATH = 'gobe.db'
PDF_PATH = 'selected_mushrooms.pdf'
# Database search function
def search_mushrooms(query):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = query.strip().lower()  # Convert query to lowercase
    results = []
    seen_ids = set()
    if query:
        fields = ['name', 'name_slo', 'name_old', 'name_slo_old']
        for field in fields:
            # Use LOWER() for case-insensitive search on all fields
            cursor.execute(f"SELECT id, name, name_slo, name_old, name_slo_old, full_name FROM vrste WHERE LOWER({field}) LIKE ? LIMIT 10", (f'%{query}%',))
            found = cursor.fetchall()
            for row in found:
                if row[0] not in seen_ids:
                    results.append((row, field))
                    seen_ids.add(row[0])
    conn.close()
    return results

class GobaOpis:
    def __init__(self, id, ime, latinsko_ime, uzitnost, status, url, slika, staro_ime, staro_latinsko_ime, sgs2020, full_name):
        self.id = id
        self.ime = ime
        self.latinsko_ime = latinsko_ime
        self.staro_ime = staro_ime
        self.staro_latinsko_ime = staro_latinsko_ime
        self.uzitnost = uzitnost
        self.status = status
        self.url = url
        self.slika = slika
        self.sgs2020 = sgs2020
        self.full_name = full_name

def createCard(pdf, x1, y1, x2, y2, opis):
    if (opis.latinsko_ime == "Clitocybe ditopa"):
        opis.full_name = "Clitócybe dítopa"
    a = opis.full_name.split()
    if len(a) > 1:
        full_name = a[0] + " " + a[1]
    else:
        full_name = opis.latinsko_ime
    text1 = opis.ime.upper()
    text2 = full_name
    text3 = opis.uzitnost.upper()
    text4 = opis.status.upper()
    text5 = str(opis.id)
    text6 = ""
    if opis.staro_ime:
        if stara_imena:
            text1 = opis.staro_ime.upper()
            text2 = opis.staro_latinsko_ime
            text6 = opis.ime.upper() + ", " + opis.latinsko_ime
        else:
            text6 = opis.staro_ime.upper() + ", " + opis.staro_latinsko_ime
        print("Staro ime: " + opis.staro_ime.upper() + " " + opis.staro_latinsko_ime + " Novo ime: " + opis.ime.upper() + " " + opis.latinsko_ime)
    url = opis.url

    width = x2 - x1
    height = y2 - y1

    pdf.set_line_width(0.01)
    pdf.rect(x1, y1, width, height)

    image_width = 0.27 * width
    qr_image_width = 0.21 * width
    text1_margin_factor = 0.3
    text1_size_factor = 0.4
    text2_margin_factor = 0.2
    text2_size_factor = 0.3
    text5_size_factor = 0.15
    text1a_y = 0

    text1a = ""
    if (len(text1) > 14):
        t = text1.split()
        text1 = t[0]
        text1a = t[1]
        text1_margin_factor = 0.2
        text2_margin_factor = 0.17
    
    text_x = x1
    text1_y = y1 + text1_margin_factor * height
    text1_h = text1_size_factor * height
    last_y = text1_y

    if text1a:
        text1a_y = last_y + text2_margin_factor * height
        last_y = text1a_y

    text2_y = last_y + text2_margin_factor * height
    text2_h = text2_size_factor * height

    text3_y = text2_y + text2_margin_factor * height
    text3_h = text2_size_factor * height

    text4_y = text3_y + text2_margin_factor * height
    text4_h = text2_size_factor * height

    text5_h = text5_size_factor * height
    text5_y = y2

    if not text4:
        text1_y += 0.05 * height
        text1a_y += 0.05 * height
        text2_y += 0.05 * height
        text3_y += 0.05 * height

    pdf.set_font("ArialUni", '', text1_h)

    text1_width = pdf.get_string_width(text1)
    w = (width - text1_width - qr_image_width) / 2
    
    pdf.text(text_x + w, text1_y, text1)

    if text1a:
        text1a_width = pdf.get_string_width(text1a)
        w = (width - text1a_width - qr_image_width) / 2
        pdf.text(text_x + w, text1a_y, text1a)

    pdf.set_font("Arial", 'I', text2_h)
    text2_width = pdf.get_string_width(text2)
    w = (width - text2_width - qr_image_width) / 2
    pdf.text(text_x + w, text2_y, text2)
   
    pdf.set_font("ArialUni", '', text3_h)
    text3_width = pdf.get_string_width(text3) + 0.2
    w = (width - text3_width - qr_image_width) / 2
    if text3 == "UŽITNA" or text3 == "MLADA UŽITNA":
        pdf.set_fill_color(166, 255, 165)
    elif text3 == "POGOJNO UŽITNA":
        pdf.set_fill_color(255, 255, 150)
    elif text3 == "NEUŽITNA" or text3 == "UŽITNOST NEZNANA":
        pdf.set_fill_color(233, 169, 67)
    elif text3 == "STRUPENA":
        pdf.set_fill_color(255, 110, 110)
    elif text3 == "SMRTNO STRUPENA":
        pdf.set_fill_color(235, 50, 50)
        pdf.set_text_color(255, 255, 0)
    else:
        pdf.set_fill_color(255, 255, 255)

    pdf.rect(text_x + w - 1, text3_y - text3_h * 0.35 + 0.4, text3_width + 2, text3_h * 0.35 + 0.12, 'F')
    pdf.text(text_x + w, text3_y, text3)

    pdf.set_text_color(0, 0, 0)

    pdf.set_font("ArialUni", '', text4_h)
    text4_width = pdf.get_string_width(text4)
    w = (width - text4_width - qr_image_width) / 2
    pdf.text(text_x + w, text4_y, text4)

    # Generate and center QR code vertically on the right side of the card
    if url:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=11,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        qrn = "qr"+ text2.strip() +".png"
        img.save(qrn)
        
        # Center QR code vertically on the right side of the card
        qr_x = x2 - qr_image_width - 0.05 * height
        qr_y = y1 + (height - qr_image_width) / 2  # Center vertically
        
        pdf.image(qrn, qr_x, qr_y, qr_image_width, qr_image_width)
        os.remove(qrn)

    if text6:
        # Calculate maximum allowed width (with small margins)
        max_text_width = width - 4  # 2mm margin on each side
        text6_width = pdf.get_string_width(text6)
        
        # Truncate text6 if it's too wide
        if text6_width > max_text_width:
            # Binary search to find the maximum length that fits
            left, right = 0, len(text6)
            while left < right:
                mid = (left + right + 1) // 2
                test_text = text6[:mid] + "..."
                if pdf.get_string_width(test_text) <= max_text_width:
                    left = mid
                else:
                    right = mid - 1
            text6 = text6[:left] + "..."
            text6_width = pdf.get_string_width(text6)
        
        w = (width - text6_width) / 2  # Center across entire card width
        pdf.text(text_x + w, text5_y - 1, text6)

stara_imena = False
page_width = 210
page_height = 296
n_columns = 2
n_rows = 6
n_pages_per_pdf = 200
card_width = page_width / n_columns
card_height = page_height / n_rows

def generate_pdf(selected_ids, progress_callback=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    opisi = []
    
    total_mushrooms = len(selected_ids)
    for idx, mid in enumerate(selected_ids):
        if progress_callback:
            progress_callback(f"Processing {idx+1}/{total_mushrooms}: Loading mushroom data...")
            
        cursor.execute('''SELECT id,name,name_slo,link,protected,status,edibility,name_old,name_slo_old,sgs2020,full_name FROM vrste WHERE id=?''', (mid,))
        record = cursor.fetchone()
        if record:
            cursor.execute('''SELECT link FROM slike WHERE vrsta_id = ? LIMIT 1''', (record[0],))
            slike = cursor.fetchall()
            url = None
            
            # Get the URL for QR code generation, no image download needed
            for slika in slike:
                url = slika[0]
                break
                
            status = ""
            if record[4]:
                status = "zavarovana vrsta"
            elif record[5] == "E":
                status = "prizadeta vrsta"
            elif record[5] == "V":
                status += "ranljiva vrsta"
            elif record[5] == "R":
                status += "redka vrsta"
            elif record[5] == "K" or record[6] == "I":
                status += "ogrožena vrsta"
            if status and record[5]:
                status += " (" + record[5] + ")"
            opisi.append(GobaOpis(record[0], record[2], record[1], record[6], status, record[3], None, record[8], record[7], record[9], record[10]))
    
    conn.close()

    if progress_callback:
        progress_callback("Creating PDF layout...")

    pdf_time = int(time.time())
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.add_font("ArialUni", "", "arialuni.ttf", uni=True)
    opis_index = 0
    num = len(opisi)
    cards_created = 0
    
    while opis_index < num:
        for i in range(n_columns):
            j = 0
            while j < n_rows and opis_index < num:
                if progress_callback:
                    progress_callback(f"Creating card {cards_created + 1}/{num}: {opisi[opis_index].latinsko_ime}")
                # Generate card for all selected mushrooms, not just those with sgs2020
                createCard(pdf, i * card_width, j * card_height, (i + 1) * card_width, (j + 1) * card_height, opisi[opis_index])
                j += 1
                cards_created += 1
                opis_index += 1
        if opis_index < num:
            pdf.add_page()
            if progress_callback:
                progress_callback(f"Added new page, continuing with cards...")
                
    pdf.output(PDF_PATH, 'F')
    if progress_callback:
        progress_callback(f"✓ PDF completed! Generated {cards_created} mushroom cards")

# GUI Application
class MushroomApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kartice razstave gob")
        self.root.state('zoomed')  # Maximize window on Windows
        self.selected_mushrooms = []  # List of (id, name)
        self.printed_mushrooms = []  # List of (id, name, latin_name) sorted by latin name
        self.csv_file = "printed_mushrooms.csv"
        self.pdf_already_printed = False  # Track if current PDF has been printed
        self.load_printed_mushrooms()
        self.setup_ui()

    def setup_ui(self):
        # Main frame with grid layout for better control
        main_frame = Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights: both sections get equal space
        main_frame.grid_columnconfigure(0, weight=1)  # Left section: 50% of space
        main_frame.grid_columnconfigure(1, weight=1)  # Right section: 50% of space
        main_frame.grid_rowconfigure(0, weight=1)

        # Left section (wider)
        left_frame = Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Make the window larger
        self.root.geometry("1200x800")
        
        Label(left_frame, text="Ime vrste:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.search_var = StringVar()
        self.search_entry = Entry(left_frame, textvariable=self.search_var, width=80, font=("Arial", 12))
        self.search_entry.pack(fill=tk.X)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        suggestion_frame = Frame(left_frame)
        suggestion_frame.pack(fill=tk.X, pady=5)
        self.suggestion_scroll = tk.Scrollbar(suggestion_frame, orient=tk.VERTICAL)
        self.suggestion_list = Listbox(suggestion_frame, height=8, width=80, yscrollcommand=self.suggestion_scroll.set, font=("Arial", 12))
        self.suggestion_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.suggestion_list.bind('<<ListboxSelect>>', self.on_select_suggestion)
        self.suggestion_scroll.config(command=self.suggestion_list.yview)
        self.suggestion_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        Label(left_frame, text="Izbrane gobe:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10,0))

        # Selected mushrooms frame with scrollbar
        selected_frame = Frame(left_frame)
        selected_frame.pack(fill=tk.X, pady=5)
        self.selected_scroll = tk.Scrollbar(selected_frame, orient=tk.VERTICAL)
        self.selected_list = Listbox(selected_frame, height=12, width=80, yscrollcommand=self.selected_scroll.set, font=("Arial", 12))
        self.selected_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.selected_scroll.config(command=self.selected_list.yview)
        self.selected_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        Button(left_frame, text="Odstrani izbrane", command=self.remove_selected, font=("Arial", 12, "bold")).pack(pady=5)

        # Printed mushrooms section
        Label(left_frame, text="Natisnjene vrste:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10,0))
        printed_frame = Frame(left_frame)
        printed_frame.pack(fill=tk.X, pady=5)
        self.printed_scroll = tk.Scrollbar(printed_frame, orient=tk.VERTICAL)
        self.printed_list = Listbox(printed_frame, height=8, width=80, yscrollcommand=self.printed_scroll.set, font=("Arial", 12))
        self.printed_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.printed_scroll.config(command=self.printed_list.yview)
        self.printed_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.update_printed_list()
        
        Button(left_frame, text="Odstrani izbrane", command=self.remove_printed, font=("Arial", 12, "bold")).pack(pady=5)

        # Right section (50% of total width)
        right_frame = Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Button frame for PDF and Print buttons
        button_frame = Frame(right_frame)
        button_frame.pack(pady=10)
        Button(button_frame, text="Generiraj", command=self.generate_and_preview_pdf, bg="lightblue", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        Button(button_frame, text="Natisni", command=self.print_pdf, bg="lightgreen", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)

        Label(right_frame, text="Predogled:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        self.pdf_preview_label = Label(right_frame, text="Predogled še ni generiran", bg="white", relief="sunken")
        self.pdf_preview_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.update_printed_list()

    def fix_slovenian_chars(self, text):
        """Fix incorrectly mapped Slovenian characters from Windows input method"""
        char_map = {
            'è': 'č',  # č incorrectly mapped to è
            'È': 'Č',  # Č incorrectly mapped to È
            '¹': 'š',  # š might be mapped to ¹
            '©': 'Š',  # Š might be mapped to ©
            '¾': 'ž',  # ž might be mapped to ¾
            '®': 'Ž'   # Ž might be mapped to ®
        }
        
        for wrong_char, correct_char in char_map.items():
            text = text.replace(wrong_char, correct_char)
        
        return text

    def on_search(self, event=None):
        query = self.search_var.get()
        # Fix Slovenian characters that might be incorrectly input
        corrected_query = self.fix_slovenian_chars(query)
        
        # If the query was corrected, update the Entry widget
        if corrected_query != query:
            self.search_var.set(corrected_query)
            query = corrected_query
            
        results = search_mushrooms(query)
        self.suggestion_list.delete(0, tk.END)
        for (row, field) in results:
            parts = [row[1], row[2]]
            if row[3]:
                parts.append(row[3])
            if row[4]:
                parts.append(row[4])
            display = " / ".join(parts)
            self.suggestion_list.insert(tk.END, display)

    def on_select_suggestion(self, event=None):
        selection = self.suggestion_list.curselection()
        if selection:
            idx = selection[0]
            # Get the data from the search result
            results = search_mushrooms(self.search_var.get())
            if idx < len(results):
                mushroom = results[idx]
                row = mushroom[0]
                parts = [row[1], row[2]]
                if row[3]:
                    parts.append(row[3])
                if row[4]:
                    parts.append(row[4])
                display = " / ".join(parts)
                if row[0] not in [m[0] for m in self.selected_mushrooms]:
                    self.selected_mushrooms.append((row[0], display))
                    self.update_selected_list()

    def remove_selected(self):
        selection = self.selected_list.curselection()
        if selection:
            idx = selection[0]
            del self.selected_mushrooms[idx]
            self.update_selected_list()
    
    def remove_printed(self):
        selection = self.printed_list.curselection()
        if selection:
            idx = selection[0]
            del self.printed_mushrooms[idx]
            self.update_printed_list()
            self.save_printed_to_csv()  # Update the CSV file

    def generate_and_preview_pdf(self):
        if not self.selected_mushrooms:
            messagebox.showinfo("Ni izbire", "Prosim izberite vsaj eno vrsto.")
            return
        
        # Limit to first 12 mushrooms
        mushrooms_to_print = self.selected_mushrooms[:12]
        ids = [m[0] for m in mushrooms_to_print]
        
        # Reset the printed flag when generating new PDF
        self.pdf_already_printed = False
        
        try:
            generate_pdf(ids)
        except Exception as e:
            messagebox.showerror("PDF Generation Error", f"Error generating PDF: {e}")
            self.pdf_preview_label.config(text=f"Error: {e}", bg="lightcoral")
            return
            
        # Convert first page of PDF to image and display
        try:
            images = convert_from_path(PDF_PATH, first_page=1, last_page=1)
            img = images[0]
            img.thumbnail((500, 700))  # Larger thumbnail
            self.imgtk = ImageTk.PhotoImage(img)
            self.pdf_preview_label.config(image=self.imgtk, text="", bg="white")
        except Exception as e:
            # If poppler is not installed or other PDF preview issues
            self.pdf_preview_label.config(
                text=f"PDF generated successfully!\nFile: {PDF_PATH}\n\nCards generated: {len(ids)}\n\nFor preview, install poppler:\nhttps://github.com/oschwartz10612/poppler-windows/releases/", 
                image="", bg="lightyellow", justify=tk.LEFT
            )

    def print_pdf(self):
        if not os.path.exists(PDF_PATH):
            messagebox.showwarning("Ni PDFja", "Prosim generirajte najprej PDF.")
            return
        
        try:
            # Open PDF file for manual printing
            if platform.system() == "Windows":
                os.startfile(PDF_PATH)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", PDF_PATH])
            else:  # Linux
                subprocess.run(["xdg-open", PDF_PATH])
            
            # Only ask to mark as printed if PDF hasn't been printed yet and there are selected mushrooms
            if not self.pdf_already_printed and self.selected_mushrooms:
                # Check how many mushrooms are actually in the current PDF (up to 12)
                mushrooms_in_pdf = min(12, len(self.selected_mushrooms))
                
                self.move_to_printed()
                self.pdf_already_printed = True
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF file: {e}")

    def move_to_printed(self):
        if not self.selected_mushrooms:
            return
        
        # Get up to 12 mushrooms to move (or fewer if less than 12 available)
        num_to_move = min(12, len(self.selected_mushrooms))
        mushrooms_to_move = self.selected_mushrooms[:num_to_move]
        
        # Get full mushroom data for CSV
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for mushroom_id, display_name in mushrooms_to_move:
            cursor.execute('''SELECT id,name,name_slo,link,protected,status,edibility,name_old,name_slo_old,sgs2020,full_name FROM vrste WHERE id=?''', (mushroom_id,))
            record = cursor.fetchone()
            if record:
                # Add to printed list with latin name for sorting
                self.printed_mushrooms.append((record[0], display_name, record[1]))  # id, display_name, latin_name
        
        conn.close()
        
        # Remove only the mushrooms that were actually moved (not always 12)
        self.selected_mushrooms = self.selected_mushrooms[num_to_move:]
        
        # Sort printed mushrooms by latin name
        self.printed_mushrooms.sort(key=lambda x: x[2])  # Sort by latin_name
        
        # Update UI
        self.update_selected_list()
        self.update_printed_list()
        
        # Save to CSV
        self.save_printed_to_csv()

    def update_selected_list(self):
        self.selected_list.delete(0, tk.END)
        for _, display_name in self.selected_mushrooms:
            self.selected_list.insert(tk.END, display_name)

    def update_printed_list(self):
        self.printed_list.delete(0, tk.END)
        for _, display_name, latin_name in self.printed_mushrooms:
            self.printed_list.insert(tk.END, f"{latin_name} - {display_name}")

    def save_printed_to_csv(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['znanstveno ime', 'slovensko ime', 'užitnost', 'ohranitveni status', 'staro znanstveno ime', 'staro slovensko ime', 'polno ime']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for mushroom_id, _, _ in self.printed_mushrooms:
                    cursor.execute('''SELECT id,name,name_slo,link,protected,status,edibility,name_old,name_slo_old,sgs2020,full_name FROM vrste WHERE id=?''', (mushroom_id,))
                    record = cursor.fetchone()
                    if record:
                        status = ""
                        if record[4]:
                            status = "zavarovana vrsta"
                        elif record[5] == "E":
                            status = "prizadeta vrsta"
                        elif record[5] == "V":
                            status = "ranljiva vrsta"
                        elif record[5] == "R":
                            status = "redka vrsta"
                        elif record[5] == "K" or record[6] == "I":
                            status = "ogrožena vrsta"
                        if status and record[5]:
                            status += " (" + record[5] + ")"
                        
                        writer.writerow({
                            'znanstveno ime': record[1],
                            'slovensko ime': record[2],
                            'užitnost': record[6],
                            'ohranitveni status': status,
                            'staro znanstveno ime': record[7] or '',
                            'staro slovensko ime': record[8] or '',
                            'polno ime': record[10] or ''
                        })
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("CSV Error", f"Error saving to CSV: {e}")

    def load_printed_mushrooms(self):
        if os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        # Create display name from available data
                        parts = [row['latin_name'], row['slovenian_name']]
                        if row['old_latin_name']:
                            parts.append(row['old_latin_name'])
                        if row['old_slovenian_name']:
                            parts.append(row['old_slovenian_name'])
                        display_name = " / ".join(parts)
                        
                        self.printed_mushrooms.append((int(row['id']), display_name, row['latin_name']))
                
                # Sort by latin name
                self.printed_mushrooms.sort(key=lambda x: x[2])
                
            except Exception as e:
                print(f"Error loading printed mushrooms: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MushroomApp(root)
    root.mainloop()
