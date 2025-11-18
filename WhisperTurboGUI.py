import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import whisper
import os

class WhisperTranscriptionApp:
	def copy_transcription(self):
		text = self.text_area.get("1.0", tk.END).strip()
		if text:
			self.root.clipboard_clear()
			self.root.clipboard_append(text)
			self.copy_btn.config(text="Copied!", bg="#22d3ee")
			self.root.after(1200, lambda: self.copy_btn.config(text="Copy", bg="#06b6d4"))
	def __init__(self, root):
		self.root = root
		self.root.title("Whisper Turbo Transcription")
		self.root.geometry("900x650")
		self.root.configure(bg="#181824")
        
		self.model = None
		self.device = tk.StringVar(value="auto")
		self.audio_file = None
		self.transcription = ""
        
		self.setup_ui()
		# Reload model if device changes
		self.device.trace_add('write', self.reload_model)
		self.model_loading = False
		self.load_model()
        
	def setup_ui(self):
		# Title
		title = tk.Label(
			self.root,
			text="Whisper Turbo Transcription",
			font=("Segoe UI", 28, "bold"),
			bg="#181824",
			fg="#f8fafc"
		)
		title.pack(pady=(30, 10))

		# Device selection
		import torch
		device_frame = tk.Frame(self.root, bg="#181824")
		device_frame.pack(pady=(0, 10))
		tk.Label(device_frame, text="Device:", font=("Segoe UI", 12), bg="#181824", fg="#f8fafc").pack(side="left", padx=(0, 5))
		available_devices = ["auto", "cpu"]
		if torch.cuda.is_available():
			available_devices.append("cuda")
		self.device_menu = tk.OptionMenu(device_frame, self.device, *available_devices)
		self.device_menu.config(font=("Segoe UI", 12), bg="#23263a", fg="#f8fafc", highlightthickness=0, bd=0, relief="flat")
		self.device_menu.pack(side="left")
        
		# File selection frame
		file_frame = tk.Frame(self.root, bg="#181824")
		file_frame.pack(pady=10, padx=40, fill="x")

		self.file_label = tk.Label(
			file_frame,
			text="No file selected",
			font=("Segoe UI", 12),
			bg="#181824",
			fg="#f8fafc"
		)
		self.file_label.pack(side="left", padx=10)

		def on_enter(e):
			select_btn.config(bg="#7c3aed")
		def on_leave(e):
			select_btn.config(bg="#6366f1")

		select_btn = tk.Button(
			file_frame,
			text="Select Audio File",
			command=self.select_file,
			bg="#6366f1",
			fg="white",
			font=("Segoe UI", 13, "bold"),
			padx=28,
			pady=12,
			relief="flat",
			cursor="hand2",
			activebackground="#7c3aed",
			activeforeground="white",
			bd=0,
			highlightthickness=0
		)
		select_btn.pack(side="right")
		select_btn.bind("<Enter>", on_enter)
		select_btn.bind("<Leave>", on_leave)
        
		# Transcribe button
		def on_transcribe_enter(e):
			self.transcribe_btn.config(bg="#a78bfa")
		def on_transcribe_leave(e):
			self.transcribe_btn.config(bg="#8b5cf6")
		self.transcribe_btn = tk.Button(
			self.root,
			text="Transcribe",
			command=self.transcribe,
			bg="#8b5cf6",
			fg="white",
			font=("Segoe UI", 16, "bold"),
			padx=50,
			pady=18,
			relief="flat",
			cursor="hand2",
			state="disabled",
			activebackground="#a78bfa",
			activeforeground="white",
			bd=0,
			highlightthickness=0
		)
		self.transcribe_btn.pack(pady=25)
		self.transcribe_btn.bind("<Enter>", on_transcribe_enter)
		self.transcribe_btn.bind("<Leave>", on_transcribe_leave)
        
		# Status label
		self.status_label = tk.Label(
			self.root,
			text="Loading Whisper Turbo model...",
			font=("Segoe UI", 12, "italic"),
			bg="#181824",
			fg="#fbbf24"
		)
		self.status_label.pack(pady=(0, 10))

		# Progress bar
		import tkinter.ttk as ttk
		style = ttk.Style()
		style.theme_use('default')
		style.configure("TProgressbar", thickness=18, troughcolor="#23263a", background="#22d3ee", bordercolor="#23263a", lightcolor="#22d3ee", darkcolor="#22d3ee")
		self.progress_var = tk.DoubleVar()
		self.progress_bar = ttk.Progressbar(
			self.root,
			variable=self.progress_var,
			maximum=100,
			length=520,
			mode="determinate",
			style="TProgressbar"
		)
		self.progress_bar.pack(pady=(0, 18))
        
		# Transcription text area
		text_frame = tk.Frame(self.root, bg="#181824")
		text_frame.pack(pady=10, padx=40, fill="both", expand=True)

		tk.Label(
			text_frame,
			text="Transcription:",
			font=("Segoe UI", 15, "bold"),
			bg="#181824",
			fg="#f8fafc"
		).pack(anchor="w", pady=(0, 5))

		# Transcription text area with lighter background and brighter text
		self.text_area = scrolledtext.ScrolledText(
			text_frame,
			wrap=tk.WORD,
			font=("Segoe UI", 12),
			padx=12,
			pady=12,
			relief="flat",
			borderwidth=0,
			bg="#23263a",
			fg="#f8fafc",
			insertbackground="#22d3ee"
		)
		self.text_area.pack(fill="both", expand=True, pady=5, side="left")

		# Copy button at top-right of transcription area
		def on_copy_enter(e):
			self.copy_btn.config(bg="#22d3ee")
		def on_copy_leave(e):
			self.copy_btn.config(bg="#06b6d4")
		self.copy_btn = tk.Button(
			text_frame,
			text="Copy",
			command=self.copy_transcription,
			bg="#06b6d4",
			fg="white",
			font=("Segoe UI", 11, "bold"),
			padx=18,
			pady=6,
			relief="flat",
			cursor="hand2",
			state="normal",
			activebackground="#22d3ee",
			activeforeground="white",
			bd=0,
			highlightthickness=0
		)
		self.copy_btn.pack(anchor="ne", padx=0, pady=(0, 5), side="top")
		self.copy_btn.bind("<Enter>", on_copy_enter)
		self.copy_btn.bind("<Leave>", on_copy_leave)
        
		# Export button
		def on_export_enter(e):
			self.export_btn.config(bg="#38bdf8")
		def on_export_leave(e):
			self.export_btn.config(bg="#3b82f6")
		self.export_btn = tk.Button(
			self.root,
			text="Export Transcription",
			command=self.export_transcription,
			bg="#3b82f6",
			fg="white",
			font=("Segoe UI", 13, "bold"),
			padx=36,
			pady=12,
			relief="flat",
			cursor="hand2",
			state="disabled",
			activebackground="#38bdf8",
			activeforeground="white",
			bd=0,
			highlightthickness=0
		)
		self.export_btn.pack(pady=12)
		self.export_btn.bind("<Enter>", on_export_enter)
		self.export_btn.bind("<Leave>", on_export_leave)
        
	def load_model(self):
		"""Load Whisper Turbo model in background, show loading indicator"""
		def load():
			try:
				import torch
				device = self.device.get()
				orig_device = device
				if device == "auto":
					device = "cuda" if torch.cuda.is_available() else "cpu"
				elif device == "cuda" and not torch.cuda.is_available():
					device = "cpu"
					self.root.after(0, lambda: messagebox.showinfo("Device fallback", "CUDA is not available. Falling back to CPU."))
				self.model = whisper.load_model("turbo", device=device)
				self.model_loading = False
				self.root.after(0, lambda: self.status_label.config(text=f"Ready to transcribe ({device})", fg="#10b981"))
				self.root.after(0, lambda: self.transcribe_btn.config(state="normal"))
				# If fallback occurred, update dropdown
				if orig_device != device:
					self.root.after(0, lambda: self.device.set(device))
			except Exception as e:
				self.model_loading = False
				self.root.after(0, lambda err=str(e): self.status_label.config(text=f"Error loading model: {err}", fg="#ef4444"))
				self.root.after(0, lambda err=str(e): messagebox.showerror("Error", f"Failed to load Whisper model:\n{err}"))
				self.root.after(0, lambda: self.transcribe_btn.config(state="disabled"))

		self.model_loading = True
		self.status_label.config(text="Loading Whisper Turbo model...", fg="#666")
		self.transcribe_btn.config(state="disabled")
		thread = threading.Thread(target=load, daemon=True)
		thread.start()

	def reload_model(self, *_):
		self.status_label.config(text="Reloading model...", fg="#666")
		self.model = None
		self.load_model()
        
	def select_file(self):
		"""Open file dialog to select audio file"""
		filetypes = (
			("Audio files", "*.mp3 *.wav *.m4a *.ogg *.flac *.webm *.mp4"),
			("All files", "*.*")
		)
        
		filename = filedialog.askopenfilename(
			title="Select an audio file",
			filetypes=filetypes
		)
        
		if filename:
			self.audio_file = filename
			self.file_label.config(text=os.path.basename(filename), fg="#f8fafc")
			self.transcribe_btn.config(state="normal")
			self.text_area.delete(1.0, tk.END)
			self.export_btn.config(state="disabled")
            
	def transcribe(self):
		"""Transcribe the selected audio file with progress"""
		if not self.audio_file or self.model_loading:
			return
		if not self.model:
			self.status_label.config(text="Model not loaded yet. Please wait...", fg="#ef4444")
			return

		self.transcribe_btn.config(state="disabled")
		self.status_label.config(text="Transcribing... This may take a moment", fg="#f59e0b")
		self.text_area.delete(1.0, tk.END)
		self.progress_var.set(0)

		def run_transcription():
			try:
				import numpy as np
				import math
				import whisper.audio

				# Load audio using whisper's loader (ffmpeg backend)
				audio = whisper.audio.load_audio(self.audio_file)
				sr = whisper.audio.SAMPLE_RATE
				total_samples = len(audio)
				chunk_duration = 30  # seconds
				samples_per_chunk = int(sr * chunk_duration)
				num_chunks = math.ceil(total_samples / samples_per_chunk)
				segments = []

				for i in range(num_chunks):
					start = i * samples_per_chunk
					end = min((i + 1) * samples_per_chunk, total_samples)
					chunk_audio = audio[start:end]
					# Save chunk to temp file (as wav)
					import tempfile
					import soundfile as sf
					with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
						sf.write(tmp.name, chunk_audio, sr)
						temp_path = tmp.name
					result = self.model.transcribe(temp_path)
					os.remove(temp_path)
					segments.append(result["text"])
					percent = ((i + 1) / num_chunks) * 100
					self.root.after(0, lambda p=percent: self.progress_var.set(p))
					self.root.after(0, lambda p=percent: self.status_label.config(text=f"Transcribing... {p:.0f}%", fg="#f59e0b"))
				self.transcription = " ".join(segments)
				self.root.after(0, self.update_transcription_ui)
			except Exception as e:
				self.root.after(0, lambda err=str(e): self.show_error(err))

		thread = threading.Thread(target=run_transcription, daemon=True)
		thread.start()
        
	def update_transcription_ui(self):
		"""Update UI after transcription completes"""
		self.text_area.insert(1.0, self.transcription)
		self.status_label.config(text="Transcription complete!", fg="#10b981")
		self.transcribe_btn.config(state="normal")
		self.export_btn.config(state="normal")
		self.progress_var.set(100)
        
	def show_error(self, error_msg):
		"""Show error message"""
		self.status_label.config(text="Transcription failed", fg="#ef4444")
		self.transcribe_btn.config(state="normal")
		messagebox.showerror("Error", f"Transcription failed:\n{error_msg}")
        
	def export_transcription(self):
		"""Export transcription to a text file"""
		if not self.transcription:
			return
            
		filename = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
			initialfile=f"transcription_{os.path.splitext(os.path.basename(self.audio_file))[0]}.txt"
		)
        
		if filename:
			try:
				with open(filename, "w", encoding="utf-8") as f:
					f.write(self.transcription)
				messagebox.showinfo("Success", f"Transcription saved to:\n{filename}")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

def main():
	root = tk.Tk()
	app = WhisperTranscriptionApp(root)
	root.mainloop()

if __name__ == "__main__":
	main()
