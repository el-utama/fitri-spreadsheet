/**
 * VALIDASI KARYAWAN - Spreadsheet PC 01..PC 12
 * ------------------------------------------------------------------
 * SKEMA 13 KOLOM:
 *   A Worker ID, B Update Date, C Song ID YT, D Judul, E Aggregator,
 *   F Genre, G Nama Channel, H Link Channel YT, I Link Video YT,
 *   J Tanggal Video Dibuat, K Tanggal Video Dipublish,
 *   L Status Upload, M PIC channel.
 *
 * CARA PAKAI (ringkas):
 *   1. Buka file PC / master -> Extensions -> Apps Script.
 *   2. Paste file ini, simpan.
 *   3. Jalankan installAll()  -> izinkan akses saat diminta.
 *      (harus dijalankan oleh akun yang punya akses EDIT ke 12 file PC)
 *   4. Selesai. Setiap kali karyawan mengubah baris data, trigger onEdit
 *      otomatis memeriksa dan memberi catatan (note) + warna merah muda.
 *
 * FUNGSI:
 *   installAll()        : pasang catatan header + tab VALIDASI + trigger onEdit
 *                         untuk 12 file PC sekaligus (sekali jalan).
 *   validateAll()       : scan ulang SEMUA baris di 12 file (untuk data lama).
 *   uninstallAll()      : lepas trigger + hapus tab VALIDASI + catatan header.
 *   installThisSheet()  : pasang hanya untuk file yang sedang dibuka.
 *   validateThisSheet() : scan hanya file yang sedang dibuka.
 *
 * CATATAN PENTING:
 *   - "Komentar" di sini = CATATAN SEL (cell note), bukan komentar Google Docs.
 *   - Nama tab data boleh "PC 01" atau "PC 1" - script mendeteksi otomatis.
 *   - Tab VALIDASI diisi NILAI oleh script (bukan formula), sehingga aman
 *     untuk spreadsheet locale Indonesia (pemisah formula titik-koma).
 *   - Script harus dijalankan dari akun pemilik/edit file PC. Jika akun hanya
 *     punya akses "Comment only"/"Viewer", pemasangan akan gagal (ini normal).
 */

const AGGREGATOR_LIST = [
  "TuneCore", "DistroKid", "TooLost", "SoundOn", "Ditto", "Believe", "CD Baby",
  "Amuse", "Symphonic Distribution", "ONErpm", "RouteNote", "LANDR",
  "Horus Music", "Indie"
];
const GENRE_LIST = [
  "Pop", "Jazz", "Hip-Hop", "Soul", "Indie", "Dangdut", "Rock", "R&B",
  "Electronic", "K-Pop", "Nasional", "Daerah", "Alternative", "Folk", "Country",
  "Metal", "Reggae", "Latin", "Classical", "Soundtrack", "Gospel", "Blues",
  "Funk", "EDM"
];
const STATUS_LIST = [
  "Draft", "Menunggu Review", "Revisi", "Terjadwal", "Upload", "Publish",
  "Published", "Batal"
];
const MAX_GENRE = 2;
// Ejaan lama yang tetap diterima saat validasi baris; dropdown memakai nama baku.
const AGGREGATOR_ALIASES = { "tuncore": "TuneCore" };

const PC_CONFIG = [
  { pc: "PC 01", id: "1zyh70PK5RKhZU1ncTr5yDBIitVcT-d6aS71qqRR2hd0", tab: "PC 01" },
  { pc: "PC 02", id: "11rrPrMVpvnXkzCf3Eyr18SJ3vIGbYtarFEk9AqKiOl8", tab: "PC 02" },
  { pc: "PC 03", id: "1tf-vi6Eo4c1UMvKI0ddYbYgYg_dIC33IHmI1Cwx9hvs", tab: "PC 03" },
  { pc: "PC 04", id: "1UrefG8uOVvi3h1Vm8k4MzCN3vrlVVrmGGOo9cqTUQLM", tab: "PC 04" },
  { pc: "PC 05", id: "1WC4V1NNldEs7uS_Xld51393uiRI5p7eKxYgC5BlC5MY", tab: "PC 05" },
  { pc: "PC 06", id: "168OJEbH7e1qnqa81nyyUy0ZTJYft4Y50cYUyEqubs48", tab: "PC 06" },
  { pc: "PC 07", id: "1wwz_1KFb9PpJW47tzZqoOqb2LaYl6JRvko5-WiommwM", tab: "PC 07" },
  { pc: "PC 08", id: "1GlKsgFKe7JGm9lgOKt-4tH2DRZA0r_Xfxf89dpb1Sac", tab: "PC 08" },
  { pc: "PC 09", id: "1VwYa2VUseoVskqWsBmMoHp-Hqshnay2q11Bvwm2Tuzk", tab: "PC 09" },
  { pc: "PC 10", id: "1pUaz4vPmOKyplO5LHm7nRLLcjDRFRgYLNC0lsRuxT1U", tab: "PC 10" },
  { pc: "PC 11", id: "1W3ajRQiHjL4rqDQYWfkyYqAOQE_O7D42FQ5CWb6avMs", tab: "PC 11" },
  { pc: "PC 12", id: "13ZTrmU9eZ0ltVSNirEcBuqq017_b-TB85qZEqfPPF5Q", tab: "PC 12" }
];

const HEADER_NOTES = {
  1: "Worker ID - unik di dalam PC. Format disarankan 'PC07-0001' (prefix PC + nomor urut).",
  2: "Update Date - format tanggal-jam YYYY-MM-DD HH:MM. Isi waktu entri terakhir diubah.",
  3: "Song ID YT - ID video YouTube (bukan URL). Contoh: x7pB0nE1g4M.",
  4: "Judul Lagu Kompilasi - judul bebas; jangan pakai pindah baris (Alt+Enter) di dalam sel.",
  5: "Aggregator - pilih dari daftar baku: " + AGGREGATOR_LIST.join(" / ") + ".",
  6: "Genre - pilih 1 atau 2 genre, pisahkan dengan koma. Daftar: " + GENRE_LIST.join(" / ") + ".",
  7: "Nama Channel - nama channel YouTube yang persis dipakai di baris ini.",
  8: "Link Channel YT - URL channel (bukan link video); boleh youtube.com atau youtu.be.",
  9: "Link Video YT - URL video YouTube (bukan link channel); wajib; boleh youtube.com atau youtu.be.",
  10: "Tanggal Video Dibuat - format tanggal YYYY-MM-DD, harus bertipe tanggal (bukan teks).",
  11: "Tanggal Video Dipublish - format tanggal YYYY-MM-DD; boleh kosong bila belum tayang.",
  12: "Status Upload - pilih dari: " + STATUS_LIST.join(" / ") + ".",
  13: "PIC channel - nama PIC channel; boleh kosong."
};

/** ---------------- MENU ---------------- */
function onOpen() {
  try {
    SpreadsheetApp.getUi().createMenu("Validasi Karyawan")
      .addItem("Pasang ulang semua PC (setelah trigger lama dihapus)", "installAll")
      .addItem("Scan semua PC sekarang", "validateAll")
      .addItem("Pasang ulang PC ini (setelah trigger lama dihapus)", "installThisSheet")
      .addItem("Scan PC ini sekarang", "validateThisSheet")
      .addItem("Perbaiki VALIDASI semua PC (tanpa trigger)", "repairAll")
      .addSeparator()
      .addItem("Hapus semua trigger validasi (admin)", "removeTriggers")
      .addToUi();
  } catch (err) { /* diabaikan bila bukan script terikat spreadsheet */ }
}

function installThisSheet() { installForFile(SpreadsheetApp.getActive().getId()); }
function validateThisSheet() { validateOne(SpreadsheetApp.getActive().getId()); }

/** ---------------- INSTALASI ---------------- */
function installAll() {
  const ok = [], fail = [];
  PC_CONFIG.forEach(cfg => {
    try {
      installForFile(cfg.id);
      ok.push(cfg.pc);
    } catch (err) {
      fail.push(cfg.pc + " (" + err.message + ")");
    }
  });
  const msg =
    "Berhasil dipasang: " + (ok.join(", ") || "-") +
    (fail.length ? "\n\nGAGAL (biasanya karena akun ini bukan Editor file PC):\n" + fail.join("\n") : "");
  Logger.log(msg);
  try { SpreadsheetApp.getUi().alert(msg); } catch (err) { /* standalone */ }
}

function installForFile(id) {
  const cfg = cfgById(id);
  if (!cfg) throw new Error("ID file tidak terdaftar di PC_CONFIG");
  const ss = SpreadsheetApp.openById(id);
  const sheet = resolveSheet(ss, cfg);
  if (!sheet) throw new Error("tab data tidak ditemukan (dicoba: " + candidateTabs(cfg).join(", ") + ")");
  noteHeaders(sheet);
  buildValidasiTab(sheet);
  applyLists(sheet);
  ensureTrigger(id);
  try {
    validateOne(id);          // isi tab VALIDASI + note untuk data yang sudah ada
  } catch (err) {
    Logger.log("validateOne " + cfg.pc + ": " + err.message);
  }
  Logger.log("installed: " + cfg.pc + " | tab: " + sheet.getName());
}

function noteHeaders(sheet) {
  for (const [col, text] of Object.entries(HEADER_NOTES)) {
    sheet.getRange(1, Number(col)).setNote(text);
  }
}

/** Pasang dropdown aggregator/status + validasi custom genre 1-2 nilai. */
function applyLists(sheet) {
  const ss = sheet.getParent();
  const vs = ss.getSheetByName("VALIDASI");
  if (vs) {
    vs.getRange(1, 7).setValue("Daftar Genre");
    vs.getRange(2, 7, GENRE_LIST.length, 1).setValues(GENRE_LIST.map(g => [g]));
  }
  // Bersihkan validasi lama di K (status sebelum kolom Link Video disisipkan).
  sheet.getRange("K2:K1000").clearDataValidations();
  applyRuleSet(sheet, "E2", 5, "F2", 6, "L2", 12, ";");
}

/** Pasang daftar validasi di MASTER live (G/H/N) dan TEMPLET_PC (E/F/L). */
function applyMasterLists() {
  const ss = SpreadsheetApp.openById("19cPX4jWZ-kh12T6NgP8tECCemz0iN2zPc1HcFKfeDdg");
  const locale = ss.getSpreadsheetLocale();
  const sep = /^(id|in)_/i.test(locale) ? ";" : ",";
  const master = ss.getSheetByName("MASTER");
  if (!master) throw new Error("Tab MASTER tidak ditemukan");
  applyRuleSet(master, "G2", 7, "H2", 8, "N2", 14, sep);
  const tpl = ss.getSheetByName("TEMPLET_PC");
  if (tpl) {
    tpl.getRange("K2:K1000").clearDataValidations();
    applyRuleSet(tpl, "E2", 5, "F2", 6, "L2", 12, sep);
  }
  Logger.log("Daftar validasi master OK | locale=" + locale);
}

function applyRuleSet(sheet, aggCell, aggCol, genreCell, genreCol, statusCell, statusCol, sep) {
  const last = Math.min(Math.max(sheet.getMaxRows(), 2), 1000);
  const n = last - 1;

  const agg = SpreadsheetApp.newDataValidation()
    .requireValueInList(AGGREGATOR_LIST, true)
    .setAllowInvalid(false)
    .setHelpText("Pilih aggregator dari daftar baku. Kosongkan bila belum ada.")
    .build();
  sheet.getRange(2, aggCol, n, 1).setDataValidation(agg);

  const status = SpreadsheetApp.newDataValidation()
    .requireValueInList(STATUS_LIST, true)
    .setAllowInvalid(false)
    .setHelpText("Pilih status dari daftar baku.")
    .build();
  sheet.getRange(2, statusCol, n, 1).setDataValidation(status);

  const genre = SpreadsheetApp.newDataValidation()
    .requireFormulaSatisfied(genreFormulaFor(genreCell, sep))
    .setAllowInvalid(false)
    .setHelpText("Pilih 1-2 genre dari daftar baku; pisahkan dengan koma. Contoh: Pop, Jazz.")
    .build();
  sheet.getRange(2, genreCol, n, 1).setDataValidation(genre);
}

function genreFormulaFor(cell, sep) {
  const norm = 'SUBSTITUTE(' + cell + sep + '" "' + sep + '""' + ')';
  const count = '(LEN(' + norm + ')-LEN(SUBSTITUTE(' + norm + sep + '","' + sep + '""))+1)';
  const choices = GENRE_LIST.map(g => g.toLowerCase()).join("|");
  const pattern = "^(" + choices + ")(,(" + choices + "))?$";
  return '=OR(TRIM(' + cell + ')=""' + sep + 'AND(' + count + '<=' + MAX_GENRE + sep + 'REGEXMATCH(LOWER(' + norm + ')' + sep + '"' + pattern + '")))';
}

function splitGenres(value) {
  return String(value || "").trim().split(/\s*[,;\/]\s*/).filter(x => x !== "");
}

function canonicalAggregator(value) {
  const v = String(value || "").trim();
  return AGGREGATOR_ALIASES[v.toLowerCase()] || v;
}

function clearHeaderNotes() {
  PC_CONFIG.forEach(cfg => {
    try {
      const ss = SpreadsheetApp.openById(cfg.id);
      const sheet = resolveSheet(ss, cfg);
      if (sheet) sheet.getRange(1, 1, 1, 13).clearNote();
    } catch (err) { Logger.log("clearHeaderNotes " + cfg.pc + ": " + err.message); }
  });
}

/** Buat/segarkan tab VALIDASI di satu file PC.
 *  Tab ini diisi NILAI oleh script (bukan formula) agar aman untuk
 *  spreadsheet dengan locale Indonesia (pemisah formula titik-koma).
 */
function buildValidasiTab(srcSheet) {
  const ss = srcSheet.getParent();
  let vs = ss.getSheetByName("VALIDASI");
  if (!vs) vs = ss.insertSheet("VALIDASI", 1);
  vs.clear();

  vs.getRange("A1").setValue("Baris");
  vs.getRange("B1").setValue("Worker ID");
  vs.getRange("C1").setValue("Masalah Ditemukan");
  vs.getRange("D1").setValue("Status Baris");
  vs.getRange("E1").setValue("Diisi otomatis oleh script (bukan formula).");
  vs.getRange(1, 1, 1, 5).setFontWeight("bold").setBackground("#1F77B4").setFontColor("#FFFFFF");
  vs.setFrozenRows(1);

  const LAST = 500;
  const rows = [];
  for (let r = 2; r <= LAST; r++) rows.push([r]);
  vs.getRange(2, 1, LAST - 1, 1).setValues(rows);

  const rule = SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied('=$D2="ADA MASALAH"')
    .setBackground("#FFCDD2")
    .setRanges([vs.getRange(2, 1, LAST - 1, 4)])
    .build();
  vs.setConditionalFormatRules([rule]);
  vs.autoResizeColumns(1, 5);
}

function ensureTrigger(id) {
  const exists = ScriptApp.getProjectTriggers().some(t =>
    t.getHandlerFunction() === "handleEdit" &&
    String(t.getTriggerSourceId()) === String(id));
  if (!exists) {
    ScriptApp.newTrigger("handleEdit").forSpreadsheet(id).onEdit().create();
  }
}

function uninstallAll() {
  removeTriggers();
  const fail = [];
  PC_CONFIG.forEach(cfg => {
    try {
      const ss = SpreadsheetApp.openById(cfg.id);
      const sh = ss.getSheetByName("VALIDASI");
      if (sh) ss.deleteSheet(sh);
      const data = resolveSheet(ss, cfg);
      if (data) data.getRange(1, 1, 1, 13).clearNote();
    } catch (err) { fail.push(cfg.pc + " (" + err.message + ")"); }
  });
  if (fail.length) Logger.log("gagal uninstall: " + fail.join(", "));
}

function removeTriggers() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === "handleEdit")
    .forEach(t => ScriptApp.deleteTrigger(t));
}

/** Diagnostik: daftar trigger project ini (untuk audit instalasi). */
function listTriggers() {
  return ScriptApp.getProjectTriggers().map(t => ({
    handler: t.getHandlerFunction(),
    sourceId: t.getTriggerSourceId(),
    eventType: String(t.getEventType())
  }));
}

/** ---------------- VALIDASI SAAT EDIT ---------------- */
function handleEdit(e) {
  try {
    const ss = e.source;
    const cfg = PC_CONFIG.find(c => String(c.id) === String(ss.getId()));
    if (!cfg) return;                                    // bukan salah satu file PC
    const sh = e.range.getSheet();
    if (sh.getName() === "VALIDASI") return;
    const dataSheet = resolveSheet(ss, cfg);
    if (!dataSheet || sh.getName() !== dataSheet.getName()) return;  // hanya tab data

    const row = e.range.getRow();
    if (row < 2) return;
    if (e.range.getColumn() > 13) return;

    const target = sh.getRange(row, 1, 1, 13);
    const vals = target.getValues()[0];

    if (!isDataRowJS(vals)) {                             // baris kosong / sampah
      target.clearNote();
      target.setBackground(null);
      clearValidasiRow(ss, row);
      return;
    }
    applyValidation(target, vals);
  } catch (err) {
    Logger.log("handleEdit error: " + err);
  }
}

/** Tulis note + warna per sel bermasalah, lalu update baris VALIDASI. */
function applyValidation(range13, vals) {
  const issues = rowIssuesJS(vals);
  writeNotesAndColors(range13, issues);
  updateValidasiRow(range13.getSheet().getParent(), range13.getRow(), vals, issues);
}

function writeNotesAndColors(range13, issues) {
  range13.clearNote();
  range13.setBackground(null);
  const notes = new Array(13).fill("");
  for (let c = 1; c <= 13; c++) {
    if (issues.byCol[c]) notes[c - 1] = issues.byCol[c];
  }
  range13.setNotes([notes]);                              // "" = hapus note
  Object.keys(issues.byCol).forEach(c => {
    range13.getSheet().getRange(range13.getRow(), Number(c)).setBackground("#FFCDD2");
  });
}

function updateValidasiRow(ss, row, vals, issues) {
  if (row < 2 || row > 500) return;
  const vs = ss.getSheetByName("VALIDASI");
  if (!vs) return;
  const worker = !isBlank(vals[0]) ? String(vals[0]).trim() : "";
  const text = issues && issues.text ? issues.text : "";
  const status = issues && issues.count > 0 ? "ADA MASALAH" : "OK";
  vs.getRange(row, 2, 1, 3).setValues([[worker, text, status]]);
}

function clearValidasiRow(ss, row) {
  if (row < 2 || row > 500) return;
  const vs = ss.getSheetByName("VALIDASI");
  if (vs) vs.getRange(row, 2, 1, 3).setValues([["", "", ""]]);
}

function writeValidasiRows(ss, startRow, rows) {
  if (!rows.length) return;
  const vs = ss.getSheetByName("VALIDASI");
  if (!vs) return;
  const start = Math.max(2, startRow);
  const count = Math.min(rows.length, 500 - start + 1);
  if (count <= 0) return;
  vs.getRange(start, 2, count, 3).setValues(rows.slice(0, count));
}

/** ---------------- SCAN SEMUA ---------------- */
function validateAll() {
  const fail = [];
  PC_CONFIG.forEach(cfg => {
    try { validateOne(cfg.id); }
    catch (err) { fail.push(cfg.pc + " (" + err.message + ")"); }
  });
  const msg = "Scan selesai." + (fail.length ? "\nGagal: " + fail.join(", ") : "");
  Logger.log(msg);
  try { SpreadsheetApp.getUi().alert(msg); } catch (err) { /* standalone */ }
}

/** Perbaiki header/VALIDASI/note/warna di 12 file tanpa membuat trigger baru.
 *  Dipakai saat trigger lama sudah ada dan dimiliki akun lain (tidak bisa dihapus editor).
 */
function repairAll() {
  const ok = [], fail = [];
  PC_CONFIG.forEach(cfg => {
    try {
      const ss = SpreadsheetApp.openById(cfg.id);
      const sh = resolveSheet(ss, cfg);
      if (!sh) throw new Error("tab data tidak ditemukan");
      noteHeaders(sh);
      buildValidasiTab(sh);
      applyLists(sh);
      validateOne(cfg.id);
      ok.push(cfg.pc);
    } catch (err) {
      fail.push(cfg.pc + " (" + err.message + ")");
    }
  });
  const msg = "Perbaikan selesai. OK: " + (ok.join(", ") || "-") +
    (fail.length ? "\nGAGAL: " + fail.join(", ") : "");
  Logger.log(msg);
  try { SpreadsheetApp.getUi().alert(msg); } catch (err) { /* standalone */ }
  return msg;
}

function validateOne(id) {
  const cfg = cfgById(id);
  if (!cfg) return;
  const ss = SpreadsheetApp.openById(id);
  const sh = resolveSheet(ss, cfg);
  if (!sh) return;
  const last = sh.getLastRow();
  if (last < 2) return;
  const data = sh.getRange(2, 1, last - 1, 13).getValues();

  // baris data terakhir (abaikan baris "sampah" yang hanya berisi Aggregator)
  let lastData = 1;
  for (let i = 0; i < data.length; i++) {
    if (isDataRowJS(data[i])) lastData = i + 2;
  }
  // bersihkan note/warna di bawah baris data terakhir (sisa isi-bawah)
  if (lastData < last) {
    sh.getRange(lastData + 1, 1, last - lastData, 13).clearNote().setBackground(null);
  }

  const out = [];
  for (let i = 0; i < data.length; i++) {
    const row = i + 2;
    if (row > lastData) break;
    const vals = data[i];
    const rng = sh.getRange(row, 1, 1, 13);
    if (!isDataRowJS(vals)) {
      rng.clearNote();
      rng.setBackground(null);
      out.push(["", "", ""]);
      continue;
    }
    const issues = rowIssuesJS(vals);
    writeNotesAndColors(rng, issues);
    out.push([
      !isBlank(vals[0]) ? String(vals[0]).trim() : "",
      issues.text || "",
      issues.count > 0 ? "ADA MASALAH" : "OK"
    ]);
  }
  writeValidasiRows(ss, 2, out);

  // bersihkan sisa baris VALIDASI lama (mis. formula #ERROR! dari versi sebelumnya)
  const vs = ss.getSheetByName("VALIDASI");
  if (vs && out.length < 499) {
    vs.getRange(2 + out.length, 2, 499 - out.length, 3).clearContent();
  }
}

/** Logika validasi per baris (JS) */
function rowIssuesJS(vals) {
  const byCol = {};
  let count = 0;
  const add = (col, msg) => {
    byCol[col] = (byCol[col] ? byCol[col] + " | " : "") + msg;
    count++;
  };
  if (isBlank(vals[0])) add(1, "Worker ID kosong");
  if (isBlank(vals[1])) add(2, "Update Date kosong");
  else if (!(vals[1] instanceof Date)) add(2, "Update Date harus tanggal (format YYYY-MM-DD HH:MM)");
  if (isBlank(vals[2])) add(3, "Song ID YT kosong");
  if (isBlank(vals[3])) add(4, "Judul kosong");
  const aggregator = canonicalAggregator(vals[4]);
  if (aggregator !== "" && !inListCI(aggregator, AGGREGATOR_LIST)) {
    add(5, "Aggregator di luar daftar (" + AGGREGATOR_LIST.join("/") + ")");
  }
  const genre = String(vals[5] || "").trim();
  const genres = splitGenres(genre);
  if (genres.length === 0) add(6, "Genre kosong (pakai dropdown daftar baku)");
  else if (genres.length > MAX_GENRE) add(6, "Genre maksimal " + MAX_GENRE + " (pisahkan dengan koma)");
  else {
    const badGenres = genres.filter(g => !inListCI(g, GENRE_LIST));
    if (badGenres.length) add(6, "Genre di luar daftar: " + badGenres.join(", "));
  }
  if (isBlank(vals[6])) add(7, "Nama Channel kosong");
  if (isBlank(vals[7])) add(8, "Link Channel kosong");
  else if (String(vals[7]).toLowerCase().indexOf("youtu") === -1) add(8, "Link Channel bukan youtube");
  if (isBlank(vals[8])) add(9, "Link Video kosong");
  else if (String(vals[8]).toLowerCase().indexOf("youtu") === -1) add(9, "Link Video bukan youtube");
  if (isBlank(vals[9])) add(10, "Tgl Dibuat kosong");
  else if (!(vals[9] instanceof Date)) add(10, "Tgl Dibuat harus tanggal (format YYYY-MM-DD)");
  if (!isBlank(vals[10]) && !(vals[10] instanceof Date)) add(11, "Tgl Publish harus tanggal (format YYYY-MM-DD)");
  else if (vals[9] instanceof Date && vals[10] instanceof Date && vals[10] < vals[9]) add(11, "Tgl Publish < Tgl Dibuat");
  const status = String(vals[11] || "").trim();
  if (status === "") add(12, "Status kosong (pilih dari daftar)");
  else if (!inListCI(status, STATUS_LIST)) add(12, "Status di luar daftar (" + STATUS_LIST.join("/") + ")");

  const parts = [];
  for (let c = 1; c <= 13; c++) {
    if (byCol[c]) parts.push(byCol[c]);
  }
  return { byCol: byCol, count: count, text: parts.join(" | ") };
}

function isBlank(v) { return v === null || v === undefined || String(v).trim() === ""; }

/** Baris dianggap data hanya jika punya Worker ID (A), Song ID (C), atau Judul (D). */
function isDataRowJS(vals) {
  return !isBlank(vals[0]) || !isBlank(vals[2]) || !isBlank(vals[3]);
}

function inListCI(value, list) {
  const v = String(value).trim().toLowerCase();
  return list.some(x => x.toLowerCase() === v);
}

/** ---------------- UTIL ---------------- */
function cfgById(id) {
  return PC_CONFIG.find(c => String(c.id) === String(id));
}

function candidateTabs(cfg) {
  const digits = String(cfg.pc).replace(/\D/g, "");   // "01"
  const n = Number(digits);                           // 1
  const list = [];
  const push = x => { if (x && !list.some(y => y.toLowerCase() === x.toLowerCase())) list.push(x); };
  push(cfg.tab);
  push("PC " + digits);
  push("PC " + n);
  push("PC" + digits);
  push("PC" + n);
  return list;
}

/** Cari sheet data meski nama tab beda (PC 01 vs PC 1 vs PC01). */
function resolveSheet(ss, cfg) {
  for (const name of candidateTabs(cfg)) {
    const sh = ss.getSheetByName(name);
    if (sh) return sh;
  }
  // fallback: cari sheet yang baris pertamanya punya "Worker ID"
  for (const sh of ss.getSheets()) {
    if (sh.getName() === "VALIDASI") continue;
    try {
      const head = sh.getRange(1, 1, 1, 13).getDisplayValues()[0].join("|").toLowerCase();
      if (head.indexOf("worker id") !== -1) return sh;
    } catch (err) { /* range kosong / sheet aneh */ }
  }
  return null;
}
