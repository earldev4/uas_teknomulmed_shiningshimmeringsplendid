import os
import librosa
import soundfile as sf
import numpy as np

# Path
input_root = os.path.join(os.getcwd(), 'data_audio')
output_root = os.path.join(os.getcwd(), 'pitch_audio')

PITCH_STEPS = 7        # Nilai pitch shift
NOISE_FACTOR = 0.02    # Seberapa keras noise-nya

print(f"Memulai pemrosesan audio dari: {input_root}")
print("-" * 50)

# Berjalan menelusuri semua folder dan file di dalam input_root
for root, dirs, files in os.walk(input_root):
    for filename in files:
        if filename.lower().endswith('.wav'):
            
            # Tentukan Path Input Lengkap
            input_path = os.path.join(root, filename)
            
            # Tentukan Struktur Folder Output
            # (Mencari tahu file ini ada di folder kategori mana, misal: 'buah')
            relative_path = os.path.relpath(root, input_root) 
            output_dir = os.path.join(output_root, relative_path)
            
            # Buat folder output jika belum ada
            os.makedirs(output_dir, exist_ok=True)
            
            # Tentukan Path Output Lengkap
            output_filename = filename.replace('.wav', '_pitch.wav') # Opsional: ganti nama file
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                
                # Load Audio
                # sr=None agar sample rate mengikuti file asli
                y, sr = librosa.load(input_path, sr=None)
                
                # Pitch Shift (Naikkan Nada)
                y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=PITCH_STEPS)
                
                # Beri Noise (White Noise)
                # Generate noise acak sepanjang durasi audio
                noise = np.random.randn(len(y_shifted))
                # Gabungkan audio hasil pitch dengan noise
                y_final = y_shifted + (NOISE_FACTOR * noise)
                
                # Simpan
                sf.write(output_path, y_final, sr)
                
                print(f"[BERHASIL] {relative_path}/{filename} -> {relative_path}/{output_filename}")
                
            except Exception as e:
                print(f"[GAGAL]    {relative_path}/{filename}: {e}")

print("-" * 50)
print("Proses selesai. Semua file tersimpan di folder 'pitch_audio'.")