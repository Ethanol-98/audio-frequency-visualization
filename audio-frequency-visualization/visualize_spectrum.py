import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import librosa
import librosa.display
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os

class AudioAnalyzerApp:
    def __init__(self, master):
        self.master = master
        self.init_ui()

    def init_ui(self):
        self.master.title("Audio File Analyzer with Volume and Metadata")
        self.master.geometry("500x500")

        ttk.Label(self.master, text="Upload Audio Files", font=("Arial", 12)).pack(pady=20)

        self.save_var = tk.BooleanVar()
        ttk.Checkbutton(self.master, text="Save waveform as JPEG", variable=self.save_var).pack()

        ttk.Label(self.master, text="Output DPI:").pack()
        self.dpi_combobox = ttk.Combobox(self.master, values=['100', '200', '300', '500', '600'], state="readonly")
        self.dpi_combobox.set('300')
        self.dpi_combobox.pack()

        ttk.Label(self.master, text="Volume Adjustment (dB):").pack()
        self.volume_slider = ttk.Scale(self.master, from_=-10, to=10, orient='horizontal')
        self.volume_slider.pack()

        ttk.Label(self.master, text="Metadata (e.g., title):").pack()
        self.metadata_entry = ttk.Entry(self.master)
        self.metadata_entry.pack()

        ttk.Button(self.master, text="Upload Files", command=self.on_upload_click).pack(pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=400, variable=self.progress_var, mode="determinate")
        self.progress_bar.pack(pady=20)

    def on_upload_click(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.wav *.mp3 *.flac")])
        if file_paths:
            dpi_value = int(self.dpi_combobox.get())
            volume_change_dB = self.volume_slider.get()
            metadata = self.metadata_entry.get()
            save_dir = None
            if self.save_var.get():
                save_dir = filedialog.askdirectory(mustexist=True)
                if not save_dir:
                    return
            threading.Thread(target=self.process_audio_files, args=(file_paths, dpi_value, save_dir, volume_change_dB, metadata), daemon=True).start()

    def process_audio_files(self, file_paths, dpi_value, save_dir=None, volume_change_dB=0, metadata=""):
        total_files = len(file_paths)
        for index, file_path in enumerate(file_paths, start=1):
            try:
                y, sr = librosa.load(file_path, sr=None)
                if volume_change_dB != 0:
                    y = self.adjust_volume(y, volume_change_dB)
                
                plt.figure(figsize=(10, 4))
                librosa.display.waveshow(y, sr=sr)
                plt.axis('off')
                
                if save_dir:
                    temp_image_path = os.path.join(save_dir, "temp_waveform.jpg")
                    plt.savefig(temp_image_path, dpi=dpi_value, bbox_inches='tight', pad_inches=0)
                    plt.close()
                    
                    final_image_path = os.path.join(save_dir, os.path.splitext(os.path.basename(file_path))[0] + '_waveform.jpg')
                    self.add_metadata_to_image(temp_image_path, metadata or os.path.basename(file_path))
                    os.rename(temp_image_path, final_image_path)
                    
                    messagebox.showinfo("Success", f"Waveform saved as {final_image_path}")
                else:
                    plt.show()
                    plt.close()
            except Exception as e:
                messagebox.showerror("Error", str(e))
                continue
            
            self.progress_var.set(index / total_files * 100)
            self.master.update_idletasks()
        if total_files > 1:
            messagebox.showinfo("Completion", "All files have been processed.")

    def adjust_volume(self, y, change_dB):
        return librosa.db_to_amplitude(change_dB) * y

    def add_metadata_to_image(self, image_path, metadata):
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            textwidth, textheight = draw.textsize(metadata, font)
            width, height = img.size
            x, y = width - textwidth - 10, 10
            draw.text((x, y), metadata, fill="white")
            img.save(image_path)

if __name__ == "__main__":
    root = tk.T
k()
app = AudioAnalyzerApp(root)
root.mainloop()