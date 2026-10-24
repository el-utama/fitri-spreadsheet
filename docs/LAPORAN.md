# LAPORAN — Master Gabungan Spreadsheet Karyawan (PC 01–12)

**Tanggal:** 2026-10-24  
**Akun browser otomatisasi:** `your.el.utama@gmail.com` (Chrome profil `FlowAutomationChrome`)  
**Master live:** https://docs.google.com/spreadsheets/d/19cPX4jWZ-kh12T6NgP8tECCemz0iN2zPc1HcFKfeDdg

---

## 1. Ringkasan Hasil

| Komponen | Status | Lokasi |
|---|---|---|
| Master lokal (.xlsx) | Selesai | `output/master_karyawan.xlsx` |
| Master live (Google Sheet) | Selesai | link di atas (judul **MASTER_KARYAWAN_PC01-12**) |
| Gabung otomatis | Selesai | `scripts/merge_data.py` |
| RINGKASAN real-time | Selesai & terverifikasi | tab `RINGKASAN` |
| Tab `Kumpulan Video` | Selesai (lokal + live) | 33 baris unik, 9 kolom |
| Apps Script 13 kolom | **Terpasang & terverifikasi di 12 file PC** | `apps_script/karyawan_validasi.gs` |
| Backup | Tersimpan | `output/backup/` |

**Snapshot data per 2026-10-24:**

- PC 01: **20 baris**, 16 baris punya `Link Video YT`, 4 baris hanya judul, 0 link channel.
- PC 09: **24 baris**, 24 link video, 24 link channel.
- PC 02–08 dan PC 10–12: belum ada baris data.
- **MASTER: 44 baris data** (baris 2–45).
- **Kumpulan Video: 33 baris data unik** (PC 01 = 9, PC 09 = 24). PC 01 memiliki 16 baris berlink, tetapi 7 di antaranya memakai link yang sama; duplikat dihapus dan hanya kemunculan pertama yang ditampilkan.
- 975 baris sampah PC 09 (baris 26–1000, hanya `Tuncore`) diabaikan.

---

## 2. Skema Sumber (13 kolom)

Berlaku untuk 12 file PC, `TEMPLET_PC`, dan `RAW_PC01`–`RAW_PC12`.

| Kol | Header | Catatan |
|---|---|---|
| A | Worker ID | kunci bersama PC |
| B | Update Date | tanggal-jam |
| C | Song ID YT | ID video, bukan URL |
| D | Judul Lagu Kompilasi | wajib |
| E | Aggregator | dropdown daftar baku; opsional |
| F | Genre | 1–2 genre dari daftar baku; pisahkan koma |
| G | Nama Channel | satu PC boleh >1 channel |
| H | Link Channel YT | URL channel; `youtube.com` atau `youtu.be` |
| I | Link Video YT | URL video; **wajib**; `youtube.com` atau `youtu.be` |
| J | Tanggal Video Dibuat | tanggal |
| K | Tanggal Video Dipublish | tanggal; boleh kosong |
| L | Status Upload | dropdown daftar baku |
| M | PIC channel | boleh kosong |

Catatan: header sumber memiliki spasi ekor (`Song ID YT `, `Genre `, `PIC channel `); master menormalkannya.

### 2.1 Daftar Validasi Baku

Sumber tunggal daftar: `config/validation_lists.json`. File ini dipakai oleh `build_master.py`, `merge_data.py`, dan `apps_script/karyawan_validasi.gs` agar master, file PC, dan panduan tidak berbeda.

- **Aggregator (14):** `TuneCore`, `DistroKid`, `TooLost`, `SoundOn`, `Ditto`, `Believe`, `CD Baby`, `Amuse`, `Symphonic Distribution`, `ONErpm`, `RouteNote`, `LANDR`, `Horus Music`, `Indie`. Opsional; jika diisi harus dari daftar.
- **Genre (24):** `Pop`, `Jazz`, `Hip-Hop`, `Soul`, `Indie`, `Dangdut`, `Rock`, `R&B`, `Electronic`, `K-Pop`, `Nasional`, `Daerah`, `Alternative`, `Folk`, `Country`, `Metal`, `Reggae`, `Latin`, `Classical`, `Soundtrack`, `Gospel`, `Blues`, `Funk`, `EDM`. Wajib; maksimal 2 pilihan, dipisahkan koma. Script juga menerima `/` dan `;` saat membaca data lama.
- **Status (8):** `Draft`, `Menunggu Review`, `Revisi`, `Terjadwal`, `Upload`, `Publish`, `Published`, `Batal`. Wajib.

Pencocokan tidak peka huruf besar/kecil. Ejaan lama `Distrokid` dan `Toolost` diterima; `Tuncore` dipetakan ke `TuneCore`. Master lokal menormalkan nilai aggregator/genre/status ke nama baku, sedangkan sumber mentah tidak diubah.

---

## 3. Skema MASTER (19 kolom A–S)

| Kol | Header | Keterangan |
|---|---|---|
| A | PC | label baku `PC 01`–`PC 12` |
| B | Nama Karyawan | diisi manual; tidak ada di sumber |
| C | Worker ID | dari sumber |
| D | Update Date | tanggal-jam |
| E | Song ID YT | dari sumber |
| F | Judul Lagu Kompilasi | dari sumber |
| G | Aggregator | dari sumber; dinormalkan ke nama baku |
| H | Genre | 1–2 genre; dropdown/validasi daftar baku |
| I | Nama Channel | dari sumber |
| J | Link Channel YT | dari sumber H |
| K | **Link Video YT** | dari sumber I |
| L | Tanggal Video Dibuat | dari sumber J |
| M | Tanggal Video Dipublish | dari sumber K |
| N | Status Upload | dari sumber L; dinormalkan dan dropdown |
| O | PIC channel | dari sumber M |
| P | Masa Produksi (hari) | `=M-L` otomatis |
| Q | Umur Data (hari) | `=TODAY()-D` otomatis |
| R | Validasi Master | daftar masalah per baris |
| S | Duplikat? | `DUPLICAT` bila (PC, Worker ID) berulang |

Formula penting:

- P: `=IF(AND(ISNUMBER($L2),ISNUMBER($M2)),MAX(0,$M2-$L2),"")`
- Q: `=IF(ISNUMBER($D2),MAX(0,TODAY()-$D2),"")`
- R: memeriksa kolom wajib, aggregator (jika diisi), genre 1–2, link channel/video, tipe tanggal, publish < dibuat, dan status di luar daftar.
- S: `COUNTIFS` berdasarkan (PC, Worker ID).

Tab master: `PETUNJUK`, `DAFTAR_SUMBER`, `MASTER`, `Kumpulan Video`, `KAMUS_KOLOM`, `RINGKASAN`, `VALIDASI_TEMPLATE`, `TEMUAN_STRUKTUR`, `TEMPLET_PC`, `RAW_PC01`–`RAW_PC12`.

---

## 4. Tab `Kumpulan Video` (9 kolom)

| Kol | Header | Sumber MASTER |
|---|---|---|
| A | PC | A |
| B | Worker ID | C |
| C | Song ID YT | E |
| D | Judul Lagu Kompilasi | F |
| E | Nama Channel | I |
| F | Link Video YT | K |
| G | Status Upload | N |
| H | Tanggal Video Dibuat | L |
| I | Tanggal Video Dipublish | M |

Ketentuan:

- Hanya baris yang `Link Video YT` (K) terisi.
- **Hanya link unik:** jika beberapa baris memakai link video yang sama, hanya kemunculan pertama yang ditampilkan.
- Master lokal: diisi **nilai** oleh `merge_data.py` dengan deduplikasi link.
- Master live: formula `LET` + `QUERY` + `FILTER` + `MATCH` dari MASTER:
  `=IFERROR(LET(q,QUERY(MASTER!A2:O,"select A,C,E,F,I,K,N,L,M where K is not null",0),FILTER(q,MATCH(INDEX(q,0,6),INDEX(q,0,6),0)=SEQUENCE(ROWS(q)))),"")`
- Baris tanpa link tidak muncul; kekurangannya terlihat di RINGKASAN `Link Video Kosong`.
- Urutan mengikuti MASTER: PC 01 → PC 12, lalu urutan baris sumber.

---

## 5. RINGKASAN Live (minimal, 10 kolom A–J)

| Kol | Header | Sumber |
|---|---|---|
| A | PC | label |
| B | Spreadsheet ID | manifest |
| C | Baris Data | sumber D |
| D | Link Video Kosong | sumber I kosong |
| E | Genre Kosong | sumber F kosong |
| F | Status Kosong | sumber L kosong |
| G | Status Invalid | status di luar daftar |
| H | Duplikat | Worker ID berulang |
| I | Link Video Bukan YouTube | sumber I tidak mengandung `youtu` |
| J | Rata-rata Masa Produksi | rata-rata K−J yang valid |

- `Link Channel YT` (H) tetap dicek di `Validasi Master`, tetapi tidak diringkas di RINGKASAN.
- Helper daftar status ada di `N2:N9` (8 status).
- Formula PC 01 memakai fallback dua nama tab: `PC 01` lalu `PC 1`.

**Hasil verifikasi live terakhir:**

| PC | Baris Data | Link Video Kosong | Genre Kosong | Status Kosong | Status Invalid | Duplikat | Link Video Bukan YouTube | Rata-rata |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PC 01 | 20 | 4 | 4 | 17 | 0 | 0 | 0 | 0 |
| PC 09 | 24 | 0 | 0 | 0 | 0 | 0 | 0 | 11,20833333 |
| PC 02–08, 10–12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |

Catatan: PC 01 `Status Invalid` = 0 karena status `Upload` sudah masuk daftar baku dan genre `JAZZ` dicocokkan tanpa membedakan huruf besar/kecil. Rata-rata PC 01 = 0 karena 2 baris yang punya pasangan tanggal J/K memiliki masa produksi 0 hari; baris lain belum lengkap.

---

## 6. Verifikasi

### 6.1 Master lokal

- 19 kolom A–S.
- 44 baris data (baris 2–45).
- Header K = `Link Video YT`.
- Formula P–S ada di setiap baris.
- `Kumpulan Video` 33 baris unik, 9 kolom.
- RAW_PC01–12 memiliki 13 kolom.
- Tidak ada sample row kuning yang tersisa.

### 6.2 MASTER live

- 19 kolom, 44 baris data.
- K1 = `Link Video YT`; R1 = `Validasi Master`.
- Tidak ada `#ERROR!` di kolom R.
- Formula P–S terpasang sampai baris 1000.
- RINGKASAN C–J terisi.
- `Kumpulan Video` 33 baris unik, 9 kolom, tanggal H/I tampil sebagai tanggal.
- Data validation MASTER live: A (PC), G (14 aggregator), H (custom 1–2 genre), N (8 status); `TEMPLET_PC` E/F/L juga dipasang lewat `applyMasterLists()`.
- Tab `PETUNJUK` live dibersihkan dari 246 sel merah dan 258 note validasi lama; conditional formatting lama dihapus. Audit master: tidak ada sel merah tersisa; note hanya ada di `MASTER` (18) dan `TEMPLET_PC` (11).

### 6.3 Apps Script

- Kode 13 kolom terpasang di 12 project bound (satu project per file PC).
- `HEADER_NOTES` 1–13; note I = `Link Video YT`.
- `handleEdit` membaca 13 kolom; `rowIssuesJS` memakai `vals[8]` = link video, `vals[9]`/`vals[10]` = tanggal, `vals[11]` = status, `vals[12]` = PIC.
- `applyLists()` memasang dropdown aggregator/status dan validasi genre 1–2 pada file PC; daftar genre juga ditulis ke `VALIDASI!G1:G25` sebagai rujukan.
- `applyMasterLists()` memasang daftar yang sama di MASTER live (G/H/N) dan `TEMPLET_PC` live (E/F/L); sudah dijalankan dengan locale `en_US`.
- `repairAll()` sudah dijalankan: 12/12 file OK. Hasil `verify_install.py` (24 Okt 2026):
  - semua file punya tab `VALIDASI`, 13 header note, note I benar;
  - tidak ada `#ERROR!`; `Status Invalid` PC 01 = 0;
  - PC 01: 20 baris bernote (data belum lengkap), 8 baris tercatat di tab `VALIDASI`, 111 note/111 sel merah;
  - PC 09: 0 masalah; 975 baris sampah diabaikan;
  - PC 02–08, 10–12: 0 baris data, 0 masalah.
- 12 trigger lama (`handleEdit`, deployment `Head`) masih ada dan **dimiliki akun owner `Srijapar`**. Akun editor tidak bisa menghapus trigger milik akun lain. Trigger lama sudah mencakup 12 file dan sekarang menjalankan kode 13 kolom, jadi tetap dipakai. Jika owner menghapusnya, pasang ulang per file dengan `installThisSheet()`.

---

## 7. Akses & Trigger

- Akun browser `your.el.utama@gmail.com` sudah punya akses **Editor**; `clasp` memakai named user `your.el.utama` dengan client Google-provided yang sudah ada (tidak membuat OAuth client baru).
- Project PC 01: `1GVL9mkfcArpWZ_hdCtBqFHgaxfijPy__pyNHEAu4oGcgumzTLZHhzADT`.
- Project bound PC 02–12 tercatat di `data/script_ids.json`.
- Trigger lama tidak dapat dihapus oleh editor; solusi yang dipakai: update kode project PC 01 dan jalankan `repairAll()` tanpa membuat trigger baru. Ini menghindari duplikasi trigger.

---

## 8. Cara Memperbarui

```powershell
# 1. Tarik snapshot terbaru 12 file PC -> data/raw/src01..12.xlsx
python scripts/fetch_sheets.py

# 2. Bangun ulang master lokal + template + Kumpulan Video
python scripts/build_master.py

# 3. Gabung data ke MASTER, RAW_PC*, dan Kumpulan Video lokal
python scripts/merge_data.py

# 4. (opsional) segarkan snapshot MASTER live
python scripts/live_master_data.py

# 5. (opsional) pasang ulang formula P–S + RINGKASAN live
python scripts/fix_live_sheet.py

# 5b. (opsional) pasang dropdown daftar baku di MASTER/TEMPLET_PC live
#     Jalankan applyMasterLists() dari editor Apps Script project PC 01.

# 6. (opsional) segarkan tab Kumpulan Video live
python scripts/live_kumpulan_video.py

# 7. (opsional) segarkan tab dokumentasi live
python scripts/live_docs_tabs.py
```

- `fetch_sheets.py` tidak mengubah file sumber; hanya mengekspor XLSX.
- `merge_data.py` tidak mengubah file sumber; hanya menulis master lokal.
- RINGKASAN live selalu real-time via `IMPORTRANGE`.
- `Kumpulan Video` live memakai `LET` + `QUERY` dari MASTER dan hanya memuat link video unik (kemunculan pertama); segarkan MASTER untuk memperbarui.

---

## 9. Catatan Data & Risiko

1. **PC 01 link channel kosong 20/20.** Tidak diisi fiktif; validasi menandai kolom H.
2. **PC 01 Worker ID kosong 19/20.** Hanya baris 2 yang berisi `W01`; baris lain tidak diisi fiktif agar tidak menciptakan duplikat.
3. **PC 01 tanggal/status/Song ID belum lengkap.** Update Date kosong 18, Tgl Dibuat kosong 17, status kosong 17, Song ID kosong 8, link video kosong 4. Tidak diisi fiktif.
4. **Status `Upload` (3 baris) dan genre `JAZZ` (5 baris) di PC 01 sekarang valid.** Keduanya sudah masuk daftar baku; pencocokan genre tidak peka huruf besar/kecil. Daftar final ada di `config/validation_lists.json` dan bagian 2.1. Sisa 4 genre kosong dan 17 status kosong adalah data entry yang belum tersedia, bukan error daftar.
5. **PC 09 punya 975 baris sampah** (baris 26–1000, hanya `Tuncore`). Script mengabaikannya; `repairAll` sudah membersihkan note/warna di baris sampah.
6. **PC 09 link video sudah 24/24.** Saat audit sempat kosong; backup tetap ada di `output/backup/pc09_link_lama.csv`.
7. **Nama tab PC 01 = `PC 1`.** Script dan RINGKASAN mendukung `PC 01`, `PC 1`, dan `PC01`.
8. **Tab `Kumpulan Video` hanya memuat baris dengan link video unik.** Ini by design; kekurangan data terlihat di RINGKASAN.
9. **12 trigger lama dimiliki akun owner `Srijapar`.** Editor tidak bisa menghapus; trigger tetap dipakai karena sudah mencakup 12 file dan kode project PC 01 sudah 13 kolom.

---

## 10. Backup

- `output/backup/master_karyawan_pre_linkvideo.xlsx`
- `output/backup/master_live_pre_linkvideo.xlsx`
- `output/backup/pc01_link_lama.csv`
- `output/backup/pc09_link_lama.csv`
- `output/apps_script_v3_backup.gs`
- `output/apps_script_old_backup.gs`

Jangan hapus backup sampai user menyatakan aman.

---

## 11. Penutup

- File sumber **tidak diubah** oleh proses master; catatan/warna dipasang oleh Apps Script 13 kolom.
- Master lokal = snapshot lengkap (template + data + formula).
- Master live = pusat pemantauan real-time (RINGKASAN) + snapshot MASTER + `Kumpulan Video`.
- Langkah berikutnya: lengkapi data PC 01 yang masih kosong (link channel, Worker ID, tanggal, status, Song ID, link video). Status `Upload` dan genre `Jazz` sudah masuk daftar baku, jadi tidak perlu dikoreksi. Jalankan `verify_install.py` dan `verify_live.py` setelah perubahan data.
