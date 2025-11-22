import os
from gtts import gTTS
from pydub import AudioSegment

# Definisi struktur data, kata, dan path
KATEGORI = {
    'buah': {
        'path': 'data_audio/buah',
        'id_words': ['apel', 'jeruk', 'pisang', 'mangga', 'semangka'],
        'en_words': ['strawberry', 'grape', 'papaya', 'kiwi', 'pineapple']
    },
    'kendaraan': {
        'path': 'data_audio/kendaraan',
        'id_words': ['mobil', 'motor', 'sepeda', 'bus', 'kereta'],
        'en_words': ['airplane', 'boat', 'helicopter', 'scooter', 'truck']
    },
    'hewan': {
        'path': 'data_audio/hewan',
        'id_words': ['kucing', 'anjing', 'gajah', 'harimau', 'singa'],
        'en_words': ['monkey', 'horse', 'dolphin', 'giraffe', 'rabbit']
    }
}

def buat_audio_wav(teks, bahasa, file_path_wav):

    # Path sementara untuk file .mp3
    file_path_mp3 = file_path_wav.replace('.wav', '.mp3')
    
    try:
        # Buat audio .mp3 dengan gTTS
        tts = gTTS(text=teks, lang=bahasa, slow=False)
        tts.save(file_path_mp3)
        
        # Konversi .mp3 ke .wav menggunakan pydub
        audio = AudioSegment.from_mp3(file_path_mp3)
        audio.export(file_path_wav, format="wav")
        
        # Hapus file .mp3 sementara
        os.remove(file_path_mp3)
        
        print(f"  > Berhasil membuat: {file_path_wav}")
        
    except FileNotFoundError:
        print("\n[ERROR] FFmpeg tidak ditemukan!")
        print("Pastikan FFmpeg sudah terinstal dan ada di PATH sistem Anda.")
        # Hentikan eksekusi jika FFmpeg tidak ada
        exit()
    except Exception as e:
        print(f"  > Gagal membuat {file_path_wav}: {e}")
        # Hapus file mp3 jika ada error
        if os.path.exists(file_path_mp3):
            os.remove(file_path_mp3)


print("Memulai proses pembuatan audio...")

for nama_kategori, data in KATEGORI.items():
    
    output_dir = data['path']
    print(f"\nMemproses kategori: '{nama_kategori}' -> (di folder: {output_dir})")
    
    # Buat direktori jika belum ada
    os.makedirs(output_dir, exist_ok=True)
    
    # Buat audio untuk NAMA KATEGORI (kata representasi)
    # Ini untuk "satu kata yang merepresentasikan dari kategori tersebut"
    file_wav = os.path.join(output_dir, f"_{nama_kategori}.wav") # Diberi prefix _ agar mudah dibedakan
    buat_audio_wav(nama_kategori, 'id', file_wav)

    # Buat audio untuk kata-kata Bahasa Indonesia
    print("  --- Bahasa Indonesia ---")
    for kata in data['id_words']:
        file_wav = os.path.join(output_dir, f"{kata}.wav")
        buat_audio_wav(kata, 'id', file_wav)
        
    # 4. Buat audio untuk kata-kata Bahasa Inggris
    print("  --- Bahasa Inggris ---")
    for kata in data['en_words']:
        file_wav = os.path.join(output_dir, f"{kata}.wav")
        buat_audio_wav(kata, 'en', file_wav)

print("\n==================================")
print("✅ Selesai! Semua file audio telah dibuat.")
print("==================================")