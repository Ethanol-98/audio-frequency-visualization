import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import librosa
import librosa.display
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os

def adjust_volume(y, change_dB):
    """Adjust the volume of an audio signal."""
    return librosa.db_to_amplitude(change_dB) * y

def add_metadata_to_image(image_path, metadata):
    """Embed metadata in the top right corner of an image."""
    with Image.open(image_path) as img:
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text = metadata
        
        textwidth, textheight = draw.textsize(text, font)
        width, height = img.size
        x, y = width - textwidth - 10, 10
        
        draw.text((x, y), text, fill="white")
        img.save(image_path)

def process_audio_files(file_paths, dpi_value, save_dir=None, volume_change_dB=0, metadata=""):
    total_files = len(file_paths)
    for index, file_path in enumerate(file_paths, start=1):
        try:
            y, sr = librosa.load(file_path, sr=None)
            if volume_change_dB != 0:
                y = adjust_volume(y, volume_change_dB)
            
            plt.figure(figsize=(10, 4))
            librosa.display.waveshow(y, sr=sr)
            plt.axis('off')
            
            if save_dir:
                temp_image_path = os.path.join(save_dir, "temp_waveform.jpg")
                plt.savefig(temp_image_path, dpi=dpi_value, bbox_inches='tight', pad_inches=0)
                plt.close()
                
                final_image_path = os.path.join(save_dir, os.path.splitext(os.path.basename(file_path))[0] + '_waveform.jpg')
                add_metadata_to_image(temp_image_path, metadata or os.path.basename(file_path))
                os.rename(temp_image_path, final_image_path)
                
                messagebox.showinfo("Success", f"Waveform saved as {final_image_path}")
            else:
                plt.show()
                plt.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            continue
        
        progress_var.set(index / total_files * 100)
        root.update_idletasks()
    if total_files > 1:
        messagebox.showinfo("Completion", "All files have been processed.")

def on_upload_click():
    file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
    if file_paths:
        dpi_value = int(dpi_combobox.get())
        volume_change_dB = volume_slider.get()
        metadata = metadata_entry.get()
        
        if save_var.get():
            save_dir = filedialog.askdirectory(mustexist=True)
            if not save_dir:
                return
        
        threading.Thread(target=process_audio_files, args=(file_paths, dpi_value, save_dir, volume_change_dB, metadata), daemon=True).start()

root = tk.Tk()
root.title("Audio File Analyzer with Volume and Metadata")
root.geometry("500x500")

ttk.Label(root, text="Upload Audio Files", font=("Arial", 12)).pack(pady=20)

save_var = tk.BooleanVar()
ttk.Checkbutton(root, text="Save waveform as JPEG", variable=save_var).pack()

ttk.Label(root, text="Output DPI:").pack()
dpi_options = ['100', '200', '300', '500', '600']
dpi_combobox = ttk.Combobox(root, values=dpi_options, state="readonly")
dpi_combobox.set('300')
dpi_combobox.pack()

ttk.Label(root, text="Volume Adjustment (dB):").pack()
volume_slider = ttk.Scale(root, from_=-10, to=10, orient='horizontal')
volume_slider.pack()

ttk.Label(root, text="Metadata (e.g., title):").pack()
metadata_entry = ttk.Entry(root)
metadata_entry.pack()

ttk.Button(root, text="Upload Files", command=on_upload_click).pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, variable=progress_var, mode="determinate")
progress_bar.pack(pady=20)

root.mainloop()