# 💡 GUESS THE WORD 💡 
### Created By Group: ✨ Shinning Shimmering Splendid ✨

<img align="center" src="assets/image/thumbnail.jpeg" height="700" />

## 📖 Daftar Isi
- [Deskripsi Proyek](#deskripsi-proyek)
- [Anggota Kelompok](#anggota-kelompok)
- [Teknologi Aplikasi](#teknologi-aplikasi)
- [Instruksi Instalasi](#instruksi-instalasi)
- [Logbook Mingguan](#logbook-mingguan)
- [Laporan](#laporan)
- [Demo Program](#demo-program)

## 📋 Deskripsi Proyek 
<i>Guess The Word</i> adalah filter kuis yang dimana user menebak kata dari audio. Nada dari audio tersebut akan dibuat seperti chipmunk dan audio akan menyebutkan satu kata. Kata yang disebutkan dalam Bahasa Indonesia dan/atau Bahasa inggris. Terdapat pilihan ganda yang mana user akan memilih jawaban yang sesuai dengan kata yang disebutkan oleh audio. User akan memilih dengan cara menunjuk atau mengarahkan jari ke jawaban yang dipilih. Kuis ini terdapat 3 kategori tebak-tebakan. Selain itu, jawaban yang benar akan mendapatkan poin dan jawaban yang salah tidak dapat poin. Poin akan ditotalkan diakhir kuis.

Filter akan:
1. Mendeteksi jari tangan dengan kamera dan interaksinya terhadap komponen lain dalam sistem.
2. Memutar suara berdasarkan kategori dengan sudah dinaikan <i>pitch</i>-nya sehingga menjadi tantangan dalam menebak.
3. Menampilkan pilihan-pilihan untuk menjawab dari apa yang disebutkan oleh suara.
4. Memunculkan indikasi jawaban benar atau salah dari suara yang muncul setelah menjawab, seperti "Ting" jika benar dan "Tot" jika salah.
5. Menampilkan skor dari jawaban yang sudah dijawab dan bertambah jika jawaban benar kemudian menampilkan skor diakhir game.

Filter ini cocok untuk melatih pendengaran dan pengucapan terhadap suatu kosakata, sehingga menambah gudang kosakata. 

## 📋 Anggota Kelompok
<table>
  <tr>
    <td align="center">
      <img src="assets/image/deva.jpg" width="180"/><br/>
      <a href="https://github.com/earldev4">Deva Ahmad</a><br/>
      <b>122140015</b>
    </td>
    <td align="center">
      <img src="assets/image/faris.jpeg" width="180"/><br/>
      <a href="https://github.com/FARIS122140021">Faris Pratama</a><br/>
      <b>122140021</b>
    </td>
    <td align="center">
      <img src="assets/image/aliem.jpeg" width="180"/><br/>
      <a href="https://github.com/ArkanHariz">Arkan Hariz Chandrawinata Liem</a><br/>
      <b>122140038</b>
    </td>
  </tr>
</table>

## 📋 Teknologi Aplikasi
<table>
  <tr>
    <th>Name</th>
    <th>Description</th>
  </tr>
  <tr>
    <td><b>Python</b></td>
    <td>Bahasa pemrograman utama yang digunakan dalam pengembangan aplikasi.</td>
  </tr>
  <tr>
    <td><b>gTTS</b></td>
    <td>Library untuk mengubah teks menjadi suara menggunakan layanan text-to-speech Google. Output biasanya berupa file audio seperti.</td>
  </tr>
  <tr>
    <td><b>pydub</b></td>
    <td>Library untuk memanipulasi audio, seperti memotong, menggabungkan, mengubah volume, format audio, konversi .mp3 ke .wav, dan lain-lain.</td>
  </tr>
  <tr>
    <td><b>OpenCV (opencv-python / cv2)</b></td>
    <td>Library untuk pengolahan gambar dan video, seperti deteksi objek, face detection, filtering, drawing, membaca/menyimpan file video, dan pengolahan piksel.</td>
  </tr>
  <tr>
    <td><b>MediaPipe</b></td>
    <td>Library untuk computer vision dan machine learning real-time, seperti deteksi tangan, pose tubuh, wajah, gesture tracking, face mesh, dan lain-lain.</td>
  </tr>
  <tr>
    <td><b>Librosa</b></td>
    <td>Library untuk analisis dan pemrosesan audio dan musik, seperti menghitung spektrogram, MFCC, tempo, pitch, waveform, dan fitur audio lainnya untuk machine learning atau DSP.</td>
  </tr>
  <tr>
    <td><b>SoundFile</b></td>
    <td>Library untuk membaca dan menulis berbagai format file audio (WAV, FLAC, OGG, AIFF) dan bekerja bersama dengan NumPy untuk mengakses data audio dalam bentuk array.</td>
  </tr>
  <tr>
    <td><b>NumPy</b></td>
    <td>Library untuk komputasi numerik berbasis array. Digunakan untuk operasi matematika cepat, manipulasi data berbentuk matriks, dan banyak dipakai sebagai basis data pada pengolahan audio/gambar.</td>
  </tr>
</table>

## 📋 Instruksi Instalasi
1. Buat virtual environtment menggunakan <i>venv</i>
Pada terminal Code Editor, masukan perintah berikut untuk membuat environment:
```
uv venv --python=python3.11
```
Catatan: Gunakan Python versi 3.11 kebawah karena library Mediapipe hanya support versi tersebut.
Setelah itu akan muncul folder <i>.venv</i>, masuk ke folder dengan perintah <i>cd .venv</i>

2. Clone repositori
Pada terminal, setelah masuk ke folder <i>.venv</i>, salin link dari repositori ini dan klon ke direktori lokal dengan perintah:
```
git clone git@github.com:earldev4/uas_teknomulmed_shiningshimmeringsplendid.git
```
Setelah itu akan muncul folder dengan nama seperti nama repositori ini, masuk ke folder dengan perintah <i>cd</i>.

3. Aktivasi Environment
Selanjutnya, pada terminal lakukan aktivasi environment dengan perintah berikut:


a. Linux/MacOS
```
source .venv\bin\activate
```
b. Windows
```
.venv\Scripts\activate
```

## 📋 Instruksi dan Aturan Permainan
## 📋 Logbook Mingguan
## 📋 Laporan
## 📋 Demo Program

