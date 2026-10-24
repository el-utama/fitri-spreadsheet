# Rencana Penyesuaian Kolom `Link Video YT` + Tab `Kumpulan Video` — PC 01–PC 12

**Status:** Implementasi teknis selesai — 2026-10-24; sisa data PC 01 yang tidak tersedia tetap ditandai, tidak diisi fiktif.  
**Daftar validasi final:** aggregator 14, genre 24 (maksimal 2), status 8; sumber tunggal `config/validation_lists.json`. `Upload` dan `Jazz` sudah valid; master lokal menormalkan nilai dan `Tuncore` dipetakan ke `TuneCore`.  
**Tanggal audit:** 2026-10-23  
**Master live:** `19cPX4jWZ-kh12T6NgP8tECCemz0iN2zPc1HcFKfeDdg`  
**Master lokal:** `output/master_karyawan.xlsx`

> **Catatan:** implementasi teknis sudah dijalankan. Ringkasan hasil ada di `docs/LAPORAN.md`; sisa data PC 01 ada di bagian 9 laporan tersebut.

---

## 0. Ringkasan Eksekutif

1. **12/12 file PC sudah memakai 13 kolom** dengan urutan yang sama.
2. Kolom baru ada di **I = `Link Video YT`**, setelah `Link Channel YT` (H) dan sebelum `Tanggal Video Dibuat` (J).
3. Keputusan yang sudah dikonfirmasi:
   - `Link Video YT` di master: **kolom K**.
   - `Link Video YT`: **wajib**.
   - Validasi link: **bebas**, `youtube.com` maupun `youtu.be` diterima.
   - RINGKASAN: **minimal**, tanpa menambah kolom.
   - Tambahan: tab **`Kumpulan Video`** di Spreadsheet Master berisi link video dari semua PC, **hanya baris yang link videonya terisi**.
4. Secara struktur sudah konsisten, tetapi **isi data belum lengkap** (angka aktual saat verifikasi):
   - PC 01: 20 baris; `Link Video YT` terisi 16/20; `Link Channel YT` kosong 20/20.
   - PC 09: 24 baris; `Link Video YT` terisi 24/24; `Link Channel YT` terisi 24/24.
   - PC 02–08 dan PC 10–12: belum ada baris data.
5. Perubahan ini memutus pipeline lama:
   - `merge_data.py` masih mencari header `Link YT` dan posisi kolom lama.
   - Master masih 18 kolom; harus menjadi **19 kolom**.
   - Apps Script masih membaca 12 kolom; indeks tanggal/status/PIC bergeser.
   - RINGKASAN live masih memakai H sebagai link dan K sebagai status.
   - Header note kolom I saat ini **salah** (masih menyalin note `Link Channel YT`).
6. **Jangan jalankan `installAll` / `validateAll` dengan script lama.**
7. **Jangan jalankan `merge_data.py` sebelum `fetch_sheets.py`.**
8. **Jangan jalankan `live_master_data.py` sebelum kolom K ada di MASTER live.**

---

## 1. Hasil Audit 12 File PC

### 1.1 Header sumber (13 kolom, sama di semua file)

| Kol | Header | Catatan |
|---|---|---|
| A | `Worker ID` | kunci bersama PC |
| B | `Update Date` | tanggal-jam |
| C | `Song ID YT ` | ada spasi ekor |
| D | `Judul Lagu Kompilasi` | |
| E | `Aggregator` | |
| F | `Genre ` | ada spasi ekor |
| G | `Nama Channel` | |
| H | `Link Channel YT` | nama baru; sebelumnya `Link YT` |
| I | `Link Video YT` | **kolom baru** |
| J | `Tanggal Video Dibuat` | bergeser dari I |
| K | `Tanggal Video Dipublish` | bergeser dari J |
| L | `Status Upload` | bergeser dari K |
| M | `PIC channel ` | bergeser dari L; ada spasi ekor |

### 1.2 Kondisi per file

| PC | Nama tab | Baris data | H channel | I video | J tgl dibuat | L status | Catatan |
|---|---|---:|---:|---:|---:|---:|---|
| PC 01 | `PC 1` | 20 | 0 | 16 | 3 | 3 | tab tidak bernama `PC 01`; 4 baris hanya judul, banyak sel belum lengkap |
| PC 02 | `PC 02` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 03 | `PC 03` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 04 | `PC 04` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 05 | `PC 05` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 06 | `PC 06` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 07 | `PC 07` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 08 | `PC 08` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 09 | `PC 09` | 24 | 24 | 24 | 24 | 24 | 975 baris sampah (hanya `Tuncore`) |
| PC 10 | `PC 10` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 11 | `PC 11` | 0 | 0 | 0 | 0 | 0 | header saja |
| PC 12 | `PC 12` | 0 | 0 | 0 | 0 | 0 | header saja |

**Total baris data saat ini:** 44 (PC 01 = 20, PC 09 = 24).

### 1.3 Temuan penting

1. **Header note kolom I salah.** Note I saat ini berisi teks `Link channel YT`, sama seperti H. Note J–M sudah benar karena ikut bergeser. Ini akan diperbaiki oleh `installAll` versi baru.
2. **PC 09 sempat kehilangan link video lama di sumber, kini sudah terisi kembali.**
   - Data lama PC 09: kolom H berisi 24 URL `youtu.be` (link video).
   - Saat audit: kolom H berisi URL channel `https://www.youtube.com/@KadeValen`; kolom I kosong.
   - Saat verifikasi ulang: kolom I sudah berisi 24 link video; backup tetap disimpan di `output/backup/pc09_link_lama.csv` (24 baris).
3. **PC 01 belum punya link channel.** Kolom H kosong 20/20; link video sudah dipindahkan ke I (16/20).
4. **PC 01 masih sangat tidak lengkap.** Hanya 3 baris yang punya tanggal dibuat dan status; 4 baris tanpa link video (baris 18–21).
5. **Status `Upload` dan genre `JAZZ` di PC 01 sudah masuk daftar baku.** Daftar final: status `Draft`, `Menunggu Review`, `Revisi`, `Terjadwal`, `Upload`, `Publish`, `Published`, `Batal`; genre 24 nilai termasuk `Jazz`. Pencocokan tidak peka huruf besar/kecil. Ini bukan masalah data; sisa 4 genre kosong dan 17 status kosong adalah data entry yang belum tersedia.
6. **PC 09 punya 975 baris sampah** (baris 26–1000) yang hanya berisi `Tuncore`; script v3 bisa membersihkannya, tetapi harus dijalankan dengan versi 13 kolom.
7. **PC 01 tab `PC 1`**; script dan RINGKASAN harus tetap mendukung `PC 01` / `PC 1` / `PC01`.

---

## 2. Skema Baru

### 2.1 Skema sumber / TEMPLET_PC / RAW_PC (13 kolom)

| Kol | Header |
|---|---|
| A | Worker ID |
| B | Update Date |
| C | Song ID YT |
| D | Judul Lagu Kompilasi |
| E | Aggregator |
| F | Genre |
| G | Nama Channel |
| H | Link Channel YT |
| I | Link Video YT |
| J | Tanggal Video Dibuat |
| K | Tanggal Video Dipublish |
| L | Status Upload |
| M | PIC channel |

### 2.2 Skema MASTER (19 kolom) — final

| Kol | Header master | Asal | Keterangan |
|---|---|---|---|
| A | PC | konstanta | `PC 01`…`PC 12` |
| B | Nama Karyawan | manual | tidak ada di sumber |
| C | Worker ID | A | |
| D | Update Date | B | tanggal-jam |
| E | Song ID YT | C | |
| F | Judul Lagu Kompilasi | D | |
| G | Aggregator | E | |
| H | Genre | F | |
| I | Nama Channel | G | |
| J | Link Channel YT | H | link channel |
| K | **Link Video YT** | **I** | **kolom baru** |
| L | Tanggal Video Dibuat | J | bergeser |
| M | Tanggal Video Dipublish | K | bergeser |
| N | Status Upload | L | bergeser |
| O | PIC channel | M | bergeser |
| P | Masa Produksi (hari) | formula | `=M−L` |
| Q | Umur Data (hari) | formula | `=TODAY()−D` |
| R | Validasi Master | formula | daftar masalah |
| S | Duplikat? | formula | `DUPLICAT` bila (PC, Worker ID) berulang |

### 2.3 Dampak pergeseran kolom master

| Sebelum | Sesudah |
|---|---|
| O = Masa Produksi | P = Masa Produksi |
| P = Umur Data | Q = Umur Data |
| Q = Validasi Master | R = Validasi Master |
| R = Duplikat? | S = Duplikat? |
| K/L = tanggal | L/M = tanggal |
| M = Status | N = Status |
| N = PIC | O = PIC |
| J = Link Channel | J = Link Channel (tetap) |
| — | **K = Link Video (baru)** |

### 2.4 Tab `Kumpulan Video` (baru, sesuai permintaan)

Tab `Kumpulan Video` ada di **master lokal dan master live**, berisi daftar link video dari seluruh PC.

| Kol | Header | Sumber |
|---|---|---|
| A | PC | MASTER A |
| B | Worker ID | MASTER C |
| C | Song ID YT | MASTER E |
| D | Judul Lagu Kompilasi | MASTER F |
| E | Nama Channel | MASTER I |
| F | Link Video YT | MASTER K |
| G | Status Upload | MASTER N |
| H | Tanggal Video Dibuat | MASTER L |
| I | Tanggal Video Dipublish | MASTER M |

Ketentuan:

- **Hanya baris yang `Link Video YT`-nya terisi** yang ditampilkan. Baris tanpa link tidak masuk karena pekerjaan dihitung dari link video.
- Hanya **link unik** yang ditampilkan; jika beberapa baris memakai link video yang sama, hanya kemunculan pertama yang dipakai.
- Saat ini jumlahnya **33 baris unik** (PC 01 = 9, PC 09 = 24). PC 01 punya 16 baris berlink, tetapi 7 link duplikat; 4 baris tanpa link tidak masuk. Kekurangannya terlihat di RINGKASAN `Link Video Kosong` = 4.
- Urutan: PC 01 → PC 12, lalu urutan baris sumber.
- Master lokal: `Kumpulan Video` diisi **nilai** oleh `merge_data.py`.
- Master live: `Kumpulan Video` memakai formula `QUERY` dari MASTER (snapshot), sehingga ikut berubah saat MASTER disegarkan. Alternatif real-time `IMPORTRANGE` dari 12 PC **tidak disarankan** karena berat dan rawan patah.
- Header, filter, freeze, dan format tanggal H/I dipasang di tab ini.
- Jangan edit manual; anggap sebagai tampilan hasil generate.

Contoh formula live (header baris 1 diisi manual):

```text
=IFERROR(LET(q,QUERY(MASTER!A2:O,"select A,C,E,F,I,K,N,L,M where K is not null",0),FILTER(q,MATCH(INDEX(q,0,6),INDEX(q,0,6),0)=SEQUENCE(ROWS(q)))),"")
```

Baris tanpa link video tidak ditampilkan, dan link yang sama hanya muncul sekali (kemunculan pertama). Jika nanti ingin menampilkan semua baris, ganti `where K is not null` menjadi `where A is not null` — tetapi deduplikasi link tetap disarankan.

---

## 3. Dampak per Komponen

> Tabel ini merekam **kondisi awal sebelum implementasi**. Status terbaru ada di Phase 2–5 dan bagian 8–9.

| Komponen | Kondisi awal | Dampak | Tindakan |
|---|---|---|---|
| `scripts/merge_data.py` | mapping `Link YT` → J; tanggal 11/12; status 13; PIC 14 | header `Link YT` sudah tidak ada; kolom J–N salah | update mapping + preflight 13 header + isi tab Kumpulan Video |
| `scripts/build_master.py` | master 18 kolom; formula O–R; TEMPLET 12 kolom | skema master/template/validasi/RINGKASAN harus berubah | update 19 kolom master, 13 kolom template, buat tab Kumpulan Video |
| `output/master_karyawan.xlsx` | 18 kolom; 42 baris snapshot | harus dibangun ulang | backup lalu rebuild |
| MASTER live | 18 kolom; formula O–R; 42 baris | perlu sisip kolom K; formula pindah ke P–S | migrasi bertahap |
| RINGKASAN live | C–J; link H; status K; helper N | referensi bergeser; metrik video minimal | update formula C–J |
| `Kumpulan Video` lokal/live | belum ada | tab baru | buat + isi |
| `apps_script/karyawan_validasi.gs` | 12 kolom; indeks 8–11 | salah membaca Link Video, tanggal, status, PIC | update 13 kolom + validasi I |
| `scripts/verify_live.py` | cek Q index 16 | harus cek R index 17 + header K + Kumpulan Video | update |
| `scripts/verify_install.py` | scan 1–12 | tidak melihat M dan note I yang salah | update 13 + cek note I |
| `docs/LAPORAN.md` | skema 18 kolom; A1:L1 | dokumentasi usang | update |
| `data/raw/src*.xlsx` | masih 12 kolom lama | belum bisa dipakai pipeline baru | `fetch_sheets.py` |
| `data/manifest.json` | tabs mungkin stale | bukan sumber skema | refresh via fetch |
| Header note file PC | I duplikat H | validasi/petunjuk salah | `installAll` versi baru |
| Trigger Apps Script | 0 terlihat di akun browser | trigger bersifat per-user | cek di akun editor/pemilik |

---

## 4. Keputusan yang Sudah Dikonfirmasi

### D1. Posisi `Link Video YT` di master

**Final: kolom K** (setelah `Link Channel YT`, sebelum tanggal).

- Tanggal/status/PIC bergeser; formula pindah O–R → P–S.
- Live MASTER perlu sisip kolom K.

### D2. Sifat `Link Video YT`

**Final: wajib untuk setiap baris data.**

- Validasi: kosong → `Link Video kosong`; tidak mengandung `youtu` → `Link Video bukan youtube`.
- Dampak data saat ini:
  - PC 09: 0 baris ditandai (24/24 link video sudah terisi).
  - PC 01: 4 baris ditandai (baris 18–21, hanya judul tanpa link video).

### D3. Validasi link — bebas

**Final: `Link Channel YT` dan `Link Video YT` sama-sama menerima `youtube.com` maupun `youtu.be`.**

- Tidak ada aturan khusus “channel harus `youtube.com`”.
- Pesan validasi tetap dibedakan per kolom:
  - H: `Link Channel kosong` / `Link Channel bukan youtube`
  - I: `Link Video kosong` / `Link Video bukan youtube`
- Validasi memakai `SEARCH("youtu", ...)` / `indexOf("youtu")`.

### D4. RINGKASAN — minimal

**Final: tetap 10 kolom A–J, tanpa menambah kolom.**

| Kol | Header | Sumber |
|---|---|---|
| A | PC | label |
| B | Spreadsheet ID | manifest |
| C | Baris Data | RAW D |
| D | **Link Video Kosong** | RAW I |
| E | Genre Kosong | RAW F |
| F | Status Kosong | RAW L |
| G | Status Invalid | diisi script live |
| H | Duplikat | diisi script live |
| I | **Link Video Bukan YouTube** | RAW I |
| J | Rata-rata Masa Produksi | diisi script live |

- `Link Kosong` lama diganti nama menjadi `Link Video Kosong` dan diarahkan ke kolom I (bukan H).
- `Link Bukan YouTube` lama diarahkan ke kolom I.
- Link channel H tetap dicek di `Validasi Master`, tetapi tidak diringkas di RINGKASAN.
- Helper daftar status tetap di `N2:N9` (8 status).

### D5. Tab `Kumpulan Video` — final

- Nama tab: **`Kumpulan Video`**.
- Kolom: **9 kolom** seperti tabel 2.4.
- Isi: **hanya baris yang `Link Video YT`-nya terisi dan link unik**; saat ini 33 baris (PC 01 = 9, PC 09 = 24).
- Live: **`QUERY` dari MASTER** (snapshot), bukan IMPORTRANGE 12 file.
- Lokal: nilai hasil `merge_data.py`.
- Baris tanpa link tidak masuk; kekurangan terlihat di RINGKASAN `Link Video Kosong`.

---

## 5. Rencana Implementasi

### Phase 0 — Backup & pengamanan (sebagian sudah dilakukan)

- [x] Backup master lokal: `output/backup/master_karyawan_pre_linkvideo.xlsx`
- [x] Backup master live: `output/backup/master_live_pre_linkvideo.xlsx`
- [x] Backup link lama PC 01: `output/backup/pc01_link_lama.csv` (18 baris)
- [x] Backup link lama PC 09: `output/backup/pc09_link_lama.csv` (24 baris)
- [x] Backup Apps Script v3: `output/apps_script_v3_backup.gs`
- [x] Backup Apps Script lama: `output/apps_script_old_backup.gs`
- [x] Simpan hasil audit header: `data/header_scan_linkvideo.json`
- [ ] Umumkan ke pengguna: jangan mengedit file PC selama migrasi master/live.
- [ ] Pastikan tidak ada proses lain yang menulis ke `output/master_karyawan.xlsx` atau master live.

> **Penting:** backup link PC 09 harus dibuat **sebelum** `fetch_sheets.py`, karena fetch akan menimpa `data/raw/src09.xlsx` dengan versi baru yang kolom I-nya kosong. Backup sudah dibuat.

### Phase 1 — Update script lokal (sudah dijalankan)

#### 1.1 `scripts/merge_data.py`

- [ ] Ganti `SRC_TO_COL` menjadi:

| Header sumber | Kolom master |
|---|---|
| `Worker ID` | 3 (C) |
| `Update Date` | 4 (D) |
| `Song ID YT` | 5 (E) |
| `Judul Lagu Kompilasi` | 6 (F) |
| `Aggregator` | 7 (G) |
| `Genre` | 8 (H) |
| `Nama Channel` | 9 (I) |
| `Link Channel YT` | 10 (J) |
| `Link Video YT` | 11 (K) |
| `Tanggal Video Dibuat` | 12 (L) |
| `Tanggal Video Dipublish` | 13 (M) |
| `Status Upload` | 14 (N) |
| `PIC channel` | 15 (O) |

- [ ] `DATE_COLS = {4, 12, 13}` (D, L, M).
- [ ] `vals = [None] * 15`; bersihkan data lama `A:O` (jangan sentuh formula P–S).
- [ ] Tambah **preflight**: baca header, trim spasi, pastikan 13 header baru lengkap. Jika masih ada `Link YT` lama / jumlah kolom 12, **hentikan** dengan pesan: jalankan `fetch_sheets.py` dulu.
- [ ] Jangan memetakan `Link YT` lama ke `Link Channel YT`; nilai lama itu adalah link video, bukan channel.
- [ ] Pastikan `RAW_PCxx` menampung 13 kolom.
- [ ] Setelah MASTER diisi, isi tab `Kumpulan Video`:
  - bersihkan `A2:I1000`;
  - tulis kolom A–I sesuai tabel 2.4;
  - hanya baris yang `Link Video YT` (K) tidak kosong dan link belum pernah muncul (dedup); saat ini 33 baris.

#### 1.2 `scripts/build_master.py`

- [ ] `mcols` menjadi 19 kolom sesuai tabel 2.2.
- [ ] `mwidths` dan `mnotes` ditambah untuk K; note J/L/M/N/O disesuaikan.
- [ ] Dropdown status pindah ke `N2:N1000`.
- [ ] Number format tanggal: L dan M.
- [ ] Formula:
  - P = `=IF(AND(ISNUMBER($L2),ISNUMBER($M2)),MAX(0,$M2-$L2),"")`
  - Q = `=IF(ISNUMBER($D2),MAX(0,TODAY()-$D2),"")`
  - R = validasi baru (lihat 1.3)
  - S = duplikat `(PC, Worker ID)`
- [ ] `COUNTA` validasi menjadi `$A2:$O2`.
- [ ] Cek `Link Channel` di J dan `Link Video` di K dengan pesan berbeda; keduanya memakai `SEARCH("youtu", ...)`.
- [ ] Sample row: isi link video di K; tanggal di L/M; status di N; fill 19 kolom.
- [ ] Auto filter `A1:S1001`; freeze `C2`.
- [ ] `KAMUS_KOLOM`: 19 baris; tambah `Link Video YT`; ubah asal `Link Channel YT` menjadi `Link Channel YT sumber`; formula P/Q/R/S.
- [ ] `PETUNJUK`: tambah penjelasan Link Video; perbaiki teks `Link YT` lama; perbaiki typo kecil.
- [ ] `RINGKASAN`: 10 kolom A–J (lihat 1.4).
- [ ] `TEMPLET_PC`: 13 kolom; status di L; date format J/K; link DV H dan I; filter `A1:M1001`.
- [ ] `VALIDASI_TEMPLATE`: formula 13 kolom sumber (lihat 1.5).
- [ ] `TEMUAN_STRUKTUR`: update temuan `Link YT` ambigu → sudah dipecah; tambah temuan note I duplikat dan data PC09.
- [ ] `DAFTAR_SUMBER`: kolom “Kolom” akan otomatis 13 setelah raw refresh.
- [ ] Buat tab **`Kumpulan Video`**:
  - header A–I tabel 2.4;
  - freeze `A2`, filter `A1:I1000`, format tanggal H/I;
  - tab color berbeda;
  - isi awalnya kosong (diisi `merge_data.py`).

#### 1.3 Formula `Validasi Master` (R)

Formula R aktual dibuat oleh `build_master.py` dan memakai helper `aggregator_issue`, `genre_issue`, dan `status_issue`:

- `G` aggregator: opsional; jika diisi harus ada di daftar 14 nilai.
- `H` genre: wajib; 1–2 nilai dipisahkan koma; pencocokan tidak peka huruf besar/kecil.
- `N` status: wajib; harus ada di daftar 8 nilai.
- Pemeriksaan lain tetap: kolom wajib, link channel/video, tipe tanggal, publish < dibuat, dan duplikat.

Daftar nilai diambil dari `config/validation_lists.json`, bukan ditulis ulang di formula. Detail formula final ada di `scripts/build_master.py`.

#### 1.4 RINGKASAN lokal (10 kolom, minimal)

| Kol | Header | Sumber |
|---|---|---|
| A | PC | label |
| B | Spreadsheet ID | manifest |
| C | Baris Data | RAW D |
| D | Link Video Kosong | RAW I |
| E | Genre Kosong | RAW F |
| F | Status Kosong | RAW L |
| G | Status Invalid | diisi script live |
| H | Duplikat | diisi script live |
| I | Link Video Bukan YouTube | RAW I |
| J | Rata-rata Masa Produksi | diisi script live |

- [ ] Update semua referensi status lama `$K` menjadi `$L`.
- [ ] Update referensi link lama `$H` menjadi `$I` untuk metrik video.
- [ ] Jangan menambah kolom; link channel tidak diringkas di sini.
- [ ] Update merge note `A15:J15`.

#### 1.5 `VALIDASI_TEMPLATE` (13 kolom sumber)

- [ ] Ganti formula lama yang masih memakai kolom master menjadi kolom sumber:
  - A Worker ID
  - C Song ID
  - D Judul
  - F Genre
  - G Nama Channel
  - H Link Channel
  - I Link Video
  - J Tgl Dibuat
  - K Tgl Publish
  - L Status
- [ ] Tambah pemeriksaan `Link Video kosong` / `bukan youtube`.
- [ ] H dan I sama-sama memakai `youtu` (bebas).
- [ ] Pastikan template ini hanya dokumentasi; sumber kebenaran validasi tetap Apps Script.

#### 1.6 Script live

- [ ] `scripts/live_master_data.py`
  - Baca 15 kolom `A:O`.
  - Bersihkan `A2:O1000` (bukan A2:N).
  - Paste ke `A2`.
  - Preflight: header K harus `Link Video YT`; jika belum, hentikan dan minta migrasi kolom K.
  - Update docstring jumlah baris.
- [ ] `scripts/fix_live_sheet.py`
  - `Q2` → `R2`; fill `R2:R1000`.
  - Tulis ulang formula P–S dari master lokal (bukan hanya Q).
  - Pasang ulang dropdown status di `N2:N1000`.
  - Update header/note MASTER: K = Link Video; L–S sesuai pergeseran.
  - Update RINGKASAN header D/I dan formula C2:J13.
  - Update note A15.
  - Buat/segarkan tab `Kumpulan Video`:
    - header A–I tabel 2.4;
    - formula `QUERY` di A2 dengan `where K is not null`;
    - format tanggal H/I, freeze, filter.
- [ ] `scripts/live_ringkasan_v5.py`
  - Source ranges: A, D, F, I, J, K, L.
  - Output tetap 8 kolom C–J (bukan C–L).
  - Formula:
    - C = Baris Data
    - D = Link Video Kosong (I)
    - E = Genre Kosong (F)
    - F = Status Kosong (L)
    - G = Status Invalid (L)
    - H = Duplikat (A)
    - I = Link Video Bukan YouTube (I)
    - J = Rata-rata Masa Produksi (J/K)
  - Pertahankan fallback tab `PC 01` / `PC 1` untuk PC 01.
  - Jangan dijalankan setelah `fix_live_sheet.py` kecuali sudah versi baru; versi lama akan menimpa PC01 dengan formula lama.
- [ ] `scripts/verify_live.py`
  - Cek MASTER 19 kolom, header K `Link Video YT`, 44 baris.
  - Cek `R` (index 17) bukan `#ERROR!`.
  - Cek RINGKASAN C–J.
  - Cek `Kumpulan Video` 33 baris unik, 9 kolom, header benar, hanya baris dengan link video.
- [ ] `scripts/verify_install.py`
  - Scan 13 kolom.
  - Cek 13 header note; note I harus mengandung `Link Video`.
  - Scan note/red sampai baris 1000 untuk memastikan baris sampah PC09 (26–1000) bersih.

### Phase 2 — Refresh raw & rebuild master lokal

Urutan **wajib**:

```powershell
python scripts/fetch_sheets.py
python scripts/build_master.py
python scripts/merge_data.py
```

- [ ] `fetch_sheets.py` selesai; 12 file `data/raw/src*.xlsx` sekarang 13 kolom.
- [ ] Cek `data/raw/src01.xlsx`: tab `PC 1`, 20 baris data, I terisi 16.
- [ ] Cek `data/raw/src09.xlsx`: 24 baris data, I terisi 24, baris 26–1000 sampah.
- [ ] `build_master.py` menghasilkan master 19 kolom + template 13 kolom + tab `Kumpulan Video`.
- [ ] `merge_data.py` mengisi 44 baris; tidak ada warning header tidak dikenal.
- [ ] Cek `output/master_karyawan.xlsx`:
  - 19 kolom A–S.
  - 44 baris data (baris 2–45).
  - Header K = `Link Video YT`.
  - Formula P–S ada di setiap baris.
  - RAW_PC01–12 memiliki 13 kolom.
  - Tab `Kumpulan Video` berisi 33 baris unik, 9 kolom, hanya baris dengan link video.
  - Tidak ada sample row kuning yang tersisa.

### Phase 3 — Migrasi MASTER live

**Prasyarat:** backup live sudah ada; tidak ada pengguna yang mengedit.

- [ ] Buka master live sebagai editor.
- [ ] Di tab `MASTER`, **sisipkan 1 kolom di K**.
- [ ] Verifikasi header setelah sisip:
  - K = `Link Video YT` (baru, kosong)
  - L = `Tanggal Video Dibuat`
  - M = `Tanggal Video Dipublish`
  - N = `Status Upload`
  - O = `PIC channel`
  - P = `Masa Produksi (hari)`
  - Q = `Umur Data (hari)`
  - R = `Validasi Master`
  - S = `Duplikat?`
- [x] Set note K1: `URL video YouTube (bukan link channel). Wajib.`
- [x] Pastikan note L–S ikut bergeser dengan benar.
- [x] Jalankan `python scripts/live_master_data.py` (versi baru) untuk paste 44 baris A:O.
- [x] Jalankan `python scripts/fix_live_sheet.py` (versi baru) untuk formula P–S + RINGKASAN C–J.
- [x] Dropdown status N tetap ada setelah sisip kolom K (dicek lewat export XLSX).
- [x] Jalankan `python scripts/live_kumpulan_video.py` untuk tab `Kumpulan Video`.
- [x] Jalankan `python scripts/live_ringkasan_v5.py` (versi baru) khusus fallback PC01.
- [x] Jalankan `python scripts/live_docs_tabs.py` untuk menyegarkan PETUNJUK/KAMUS/TEMUAN/DAFTAR_SUMBER/TEMPLET_PC live.
- [x] Cek visual: tidak ada `#ERROR!`, `#REF!`, atau kolom bergeser.

**Alternatif jika sisip kolom K bermasalah:** rebuild tab MASTER dari master lokal, tetapi tetap pertahankan file ID live dan tab RINGKASAN. Cara sisip K lebih kecil risikonya.

### Phase 4 — Update & pasang Apps Script

**Prasyarat:** kode 13 kolom sudah selesai dan diuji sintaksnya.

- [x] Update `apps_script/karyawan_validasi.gs`:
  - `HEADER_NOTES`: tambah key 9 = Link Video; geser tanggal/status/PIC ke 10–13.
  - `noteHeaders`: tetap 1–13.
  - `clearHeaderNotes`, `uninstallAll`: range 1–13.
  - `handleEdit`: `e.range.getColumn() > 13`; target 13 kolom.
  - `writeNotesAndColors`: array 13; loop 13.
  - `validateOne`: `getRange(..., 13)`; clear range 13.
  - `resolveSheet`: header scan 13.
  - `rowIssuesJS`:
    - `vals[8]` = Link Video (wajib / youtu)
    - `vals[9]` = Tgl Dibuat
    - `vals[10]` = Tgl Publish
    - `vals[11]` = Status
    - `vals[12]` = PIC
    - `byCol` keys 9–13; loop 1–13.
    - H dan I sama-sama memakai `indexOf("youtu")`.
  - [x] Tambah validasi `Song ID YT` kosong di Apps Script (sudah terpasang).
- [x] Syntax check: salin ke `.js` sementara, jalankan `node --check` (lulus).
- [x] Kode 13 kolom dipasang ke 12 project bound (PC 01: `1GVL9mkfcArpWZ_hdCtBqFHgaxfijPy__pyNHEAu4oGcgumzTLZHhzADT`; PC 02–12 di `data/script_ids.json`).
- [x] `repairAll()` dijalankan dari project PC 01: 12/12 file OK, `VALIDASI`/note/warna bersih, tidak ada `#ERROR!`.
- [x] `applyLists()` memasang dropdown aggregator/status + genre 1–2 di file PC (locale `in_ID`, pemisah formula `;`); validasi lama di K dibersihkan.
- [x] `applyMasterLists()` memasang daftar yang sama di MASTER live G/H/N dan `TEMPLET_PC` live E/F/L (locale `en_US`, pemisah formula `,`); validasi lama di K `TEMPLET_PC` dibersihkan.
- [x] Cek trigger: 12 trigger `handleEdit` lama (milik owner `Srijapar`) mencakup 12 file; karena editor tidak bisa menghapus trigger milik akun lain, trigger lama dipakai dan kode project PC 01 sudah 13 kolom.

> **Akses (24 Okt 2026):** akun browser `your.el.utama@gmail.com` sudah **Editor**; `clasp` memakai named user `your.el.utama`. Trigger lama tidak dapat dihapus oleh editor, tetapi sudah mencakup 12 file dan menjalankan kode baru. Jika owner menghapusnya, pasang ulang per file dengan `installThisSheet()`.

### Phase 5 — Verifikasi

```powershell
python scripts/verify_live.py
python scripts/verify_install.py
```

- [x] `verify_live.py`: MASTER 19 kolom, 44 baris, K `Link Video YT`, R bukan `#ERROR!`.
- [x] `verify_live.py`: RINGKASAN C–J terisi; PC01/PC09 sesuai harapan.
- [x] `verify_live.py`: `Kumpulan Video` 33 baris unik, 9 kolom, header benar, hanya baris dengan link video.
- [x] `verify_install.py` dijalankan: 12/12 file punya tab `VALIDASI`, **versi 13 kolom**, tidak ada `#ERROR!`, note I = `Link Video YT`.
- [x] PC09: 0 baris VALIDASI bermasalah karena Link Video sudah 24/24; note/red di baris 26–1000 sudah bersih.
- [x] PC01: note/red sesuai data (H kosong 20, I kosong 4, tanggal/status tidak lengkap).
- [x] Cek manual: note I muncul, note H tidak salah; 13 header note terpasang.
- [x] Cek RINGKASAN live: PC01 `Link Video Kosong` = 4, `Status Invalid` = 0; PC09 `Link Video Kosong` = 0. `Upload` dan `Jazz` sudah valid.
- [x] Cek `Kumpulan Video`: PC01 9 link unik, PC09 24 link, total 33 baris (7 duplikat link PC01 dihapus).
- [x] Cek master lokal dan live MASTER sama-sama 44 baris.
- [x] Audit format live: `PETUNJUK` dibersihkan dari 246 sel merah + 258 note lama; tidak ada sel merah tersisa (note hanya di `MASTER` dan `TEMPLET_PC`).

### Phase 6 — Dokumentasi & penutupan

- [x] Update `docs/LAPORAN.md`:
  - 13 kolom sumber; 19 kolom master.
  - Tabel skema dan mapping baru.
  - RINGKASAN C–J (minimal).
  - Tab `Kumpulan Video` (9 kolom, hanya baris dengan link video) dan cara refresh.
  - Apps Script 13 kolom; note A1:M1; validasi Link Video.
  - Hasil verifikasi terbaru (PC01/PC09).
  - Catatan data PC09 link video sudah terisi kembali (24/24) dan backup CSV tetap disimpan.
- [x] Update `plan.md`: tandai checklist yang selesai; Apps Script sudah terpasang dan `repairAll()` berhasil 12/12.
- [x] Simpan screenshot/verification JSON terbaru (`output/master_insert_k.png`, `output/kumpulan_video_live.png`, `output/ringkasan_v6.png`).
- [x] Jangan hapus backup sampai user menyatakan aman.

---

## 6. Matriks Verifikasi

| Yang dicek | Alat | Hasil yang diharapkan |
|---|---|---|
| 12 header sumber | `fetch_sheets.py` / audit | 13 kolom; H `Link Channel YT`; I `Link Video YT` |
| Master lokal | openpyxl / Excel | 19 kolom A–S; 44 baris; K video |
| Formula master | Excel / Google Sheets | P–S tidak `#ERROR!`; R memuat pesan Link Video |
| MASTER live | `verify_live.py` | 19 kolom; 44 baris; K video; R bersih |
| RINGKASAN live | `verify_live.py` | C–J; PC01/PC09 sesuai |
| `Kumpulan Video` | `verify_live.py` | 33 baris unik; 9 kolom; hanya baris dengan link video |
| VALIDASI tabs | `verify_install.py` | 12/12 ada; 24 baris PC09; note I benar |
| Note header | `verify_install.py` | 13 note; I = Link Video |
| Baris sampah PC09 | `verify_install.py` | tidak ada note/red di 26–1000 |
| Trigger | Apps Script UI | 12 `handleEdit` |
| Sumber tidak berubah | manual | hanya note/warna validasi; data tidak diubah merge |

---

## 7. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|---|---|---|
| Link video lama PC09 hilang | data 24 video tidak kembali | backup `output/backup/pc09_link_lama.csv`; saat verifikasi I sudah terisi 24/24 |
| Live MASTER salah sisip kolom | formula/kolom bergeser | backup live; sisip K; verifikasi header; tulis ulang P–S |
| Script lama dijalankan | note I salah; validasi kacau | jangan `installAll` sebelum update; cek versi kode |
| `merge_data.py` jalan sebelum fetch | mapping 12 kolom error | preflight 13 header; urutan fetch → build → merge |
| `live_master_data.py` jalan sebelum K ada | formula O–R tertimpa | preflight header K |
| PC01 tab `PC 1` | formula/script gagal | `candidateTabs` + fallback RINGKASAN |
| Locale Indonesia | formula VALIDASI `#ERROR!` | Apps Script tetap menulis nilai, bukan formula |
| Akun bukan editor | installAll gagal | **selesai**: akun browser sudah Editor; `repairAll` berhasil 12/12 |
| Trigger 0 di akun browser | dikira gagal | trigger lama milik owner `Srijapar`; 12 trigger tetap ada dan mencakup 12 file |
| Data PC01 tidak lengkap | banyak note/red | komunikasikan sebagai data entry, bukan bug |
| Status `Upload` / genre `Jazz` tidak baku | status/genre invalid | **selesai**: keduanya masuk daftar final; pencocokan case-insensitive; master lokal dinormalkan |
| `Kumpulan Video` snapshot | tidak real-time dari PC | refresh MASTER; atau ubah ke IMPORTRANGE bila benar-benar perlu |
| `Kumpulan Video` hanya link | PC01 4 baris tidak muncul | memang by design; kekurangan terlihat di RINGKASAN `Link Video Kosong` = 4 |
| `QUERY` error saat MASTER kosong | tab Kumpulan Video `#N/A` | bungkus `IFERROR`; isi MASTER dulu |

---

## 8. Definition of Done

- [ ] 12 file sumber tetap 13 kolom; tidak ada perubahan data oleh merge.
- [x] `output/master_karyawan.xlsx` 19 kolom, 44 baris, formula P–S benar.
- [x] MASTER live 19 kolom, 44 baris, K `Link Video YT`.
- [x] RINGKASAN live C–J; `Link Video Kosong` dan `Link Video Bukan YouTube` benar.
- [x] Tab `Kumpulan Video` ada di master lokal dan live; 33 baris unik, 9 kolom, hanya baris dengan link video.
- [ ] Apps Script 13 kolom; `installAll` sukses 12/12 dari akun editor.
- [ ] Header note I = Link Video; J–M benar.
- [ ] PC09 tidak lagi punya note/red di baris sampah 26–1000.
- [ ] `verify_live.py` dan `verify_install.py` lulus.
- [ ] `docs/LAPORAN.md` dan `plan.md` diperbarui.
- [ ] Backup tetap tersimpan.

---

## 9. Langkah Berikutnya

Semua keputusan sudah final:

1. **Kolom `Kumpulan Video`:** 9 kolom seperti tabel 2.4.
2. **Isi:** hanya baris yang `Link Video YT`-nya terisi dan link unik; saat ini 33 baris (PC 01 = 9, PC 09 = 24).
3. **Sumber live:** `QUERY` dari MASTER (snapshot), dengan `where K is not null`.
4. **Nama tab:** `Kumpulan Video`.

Plan sudah final. Implementasi teknis **selesai**: lokal + live MASTER/RINGKASAN/`Kumpulan Video`, daftar validasi terpusat di `config/validation_lists.json`, Apps Script 13 kolom di 12 file, dan dokumentasi. Yang tersisa hanya data PC 01 yang memang tidak tersedia di sumber. Urutan eksekusi:

```text
Phase 0 (backup) → Phase 1 (update script) → Phase 2 (fetch + rebuild lokal)
→ Phase 3 (migrasi live + Kumpulan Video) → Phase 4 (Apps Script) → Phase 5 (verifikasi)
→ Phase 6 (dokumentasi)
```

**Jangan lupa:** PC 01 saat ini punya 4 baris (18–21) yang hanya berisi judul tanpa link video, dan 20 baris tanpa link channel. Ini akan terlihat sebagai masalah validasi sampai data dilengkapi. Itu sinyal data yang benar, bukan error script. PC 09 sudah 24/24 link video.
