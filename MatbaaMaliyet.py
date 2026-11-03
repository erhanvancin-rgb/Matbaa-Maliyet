<!DOCTYPE html>
<html lang="tr" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matbaa ve Ambalaj Maliyet & Fiyatlandırma Sistemi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0b0f19; color: #f3f4f6; }
        .glass-card { background: rgba(17, 24, 39, 0.75); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1); }
        .tab-btn { transition: all 0.3s ease; }
        .section-header { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #fff; font-weight: bold; padding: 10px 15px; border-radius: 6px 6px 0 0; text-transform: uppercase; font-size: 13px; letter-spacing: 0.5px; }
        input, select { background-color: #0d1117 !important; color: #ffffff !important; border: 1px solid #30363d !important; padding: 6px 10px; border-radius: 6px; width: 100%; font-size: 13px; }
        input:focus, select:focus { outline: none; border-color: #f59e0b !important; }
        table th, table td { padding: 6px 8px; border-bottom: 1px solid #21262d; font-size: 12px; }
    </style>
</head>
<body class="h-full flex flex-col">

    <!-- Top Navigation / Header -->
    <header class="border-b border-slate-800 bg-slate-950/80 sticky top-0 z-50 px-6 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
        <div class="flex items-center space-x-3">
            <div class="bg-amber-500 text-slate-950 p-2.5 rounded-xl font-black text-xl shadow-lg shadow-amber-500/20">
                <i class="fa-solid fa-print"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-tight text-white">MATBAAM <span class="text-amber-500">PRO</span></h1>
                <p class="text-xs text-slate-400">Ambalaj & Matbaa Parametrik Maliyet ve Teklif Sistemi</p>
            </div>
        </div>
        <div class="text-xs text-slate-400 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl flex items-center space-x-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Güncel Kur: USD: <span id="lblUsd">49.97</span> TL | EUR: <span id="lblEur">56.00</span> TL</span>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col justify-center items-center">

        <!-- Welcome Banner & Two Main Action Buttons (Opening Home Screen ONLY with 2 buttons) -->
        <section id="welcomeSection" class="glass-card rounded-3xl p-8 lg:p-14 text-center relative overflow-hidden shadow-2xl max-w-2xl w-full">
            <div class="absolute -right-20 -top-20 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
            <div class="absolute -left-20 -bottom-20 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
            
            <span class="bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold px-4 py-1.5 rounded-full uppercase tracking-widest inline-block mb-4">
                Yönetim & Hesaplama Modülü
            </span>
            <h2 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-4">
                Matbaa Ambalaj Maliyet Sistemi
            </h2>
            <p class="text-slate-400 text-sm sm:text-base mb-8">
                Lütfen işlem yapmak istediğiniz modülü seçiniz.
            </p>

            <div class="flex flex-col gap-4">
                <button onclick="switchTab('params')" class="tab-btn w-full px-8 py-5 rounded-2xl font-bold bg-slate-900 border border-slate-700 text-slate-200 hover:border-amber-500/50 flex items-center justify-between group shadow-lg">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center group-hover:scale-110 transition-transform text-xl">
                            <i class="fa-solid fa-sliders"></i>
                        </div>
                        <div class="text-left">
                            <div class="text-xs text-slate-400 font-normal">Modül 1</div>
                            <div class="text-lg text-white">1. Parametreler (Fiyat Listesi)</div>
                        </div>
                    </div>
                    <i class="fa-solid fa-chevron-right text-slate-500 group-hover:text-amber-400 transition-colors"></i>
                </button>

                <button onclick="switchTab('calculator')" class="tab-btn w-full px-8 py-5 rounded-2xl font-bold bg-slate-900 border border-amber-500/50 text-white hover:border-amber-400 flex items-center justify-between group shadow-lg">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 rounded-xl bg-amber-500 text-slate-950 flex items-center justify-center group-hover:scale-110 transition-transform text-xl">
                            <i class="fa-solid fa-calculator"></i>
                        </div>
                        <div class="text-left">
                            <div class="text-xs text-amber-400 font-normal">Modül 2</div>
                            <div class="text-lg text-white">2. Fiyat Çıkart (Maliyet Hesaplama Formu)</div>
                        </div>
                    </div>
                    <i class="fa-solid fa-chevron-right text-amber-400 group-hover:translate-x-1 transition-transform"></i>
                </button>
            </div>
        </section>

        <!-- MODULE 1: PARAMETERS MANAGEMENT -->
        <div id="moduleParams" class="hidden w-full space-y-6">
            <div class="flex justify-between items-center bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
                <div class="flex items-center space-x-3">
                    <button onclick="goHome()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-xl border border-slate-700 text-xs font-semibold">
                        <i class="fa-solid fa-arrow-left mr-1"></i> Ana Menü
                    </button>
                    <div>
                        <h3 class="text-lg font-bold text-white">Matbaa Maliyet Parametreleri Fiyat Listesi</h3>
                        <p class="text-xs text-slate-400">Tüm hesaplamalarda baz alınacak güncel kur ve proses maliyetleri.</p>
                    </div>
                </div>
                <div class="flex items-center space-x-4 text-xs font-semibold">
                    <div class="bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700">Dolar Kuru: <input type="number" id="curUsd" value="49.97" step="0.01" class="w-20 inline-block text-right ml-1 bg-slate-950 text-amber-400" oninput="syncKur()"> TL</div>
                    <div class="bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700">Euro Kuru: <input type="number" id="curEur" value="56.00" step="0.01" class="w-20 inline-block text-right ml-1 bg-slate-950 text-amber-400" oninput="syncKur()"> TL</div>
                </div>
            </div>

            <!-- Parametreler Tabloları -->
            <div class="space-y-6">
                
                <!-- 1. Kağıt ve Karton Grubu -->
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="section-header">1. Kağıt ve Karton Grubu (Ton Maliyetleri)</div>
                    <table class="w-full text-left bg-slate-900 rounded-b">
                        <tr class="text-slate-400 border-b border-slate-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-36">Ton Fiyat</th><th class="w-28">Para Birimi</th></tr>
                        <tr><td>Amerikan Bristol Ton</td><td>Ton</td><td><input type="number" id="p_bristol" value="825.00"></td><td>$ USD</td></tr>
                        <tr><td>Krome Karton Ton</td><td>Ton</td><td><input type="number" id="p_krome" value="40000.00"></td><td>TRY TL</td></tr>
                        <tr><td>Kuşe Ton</td><td>Ton</td><td><input type="number" id="p_kuse" value="850.00"></td><td>€ EUR</td></tr>
                        <tr><td>1. Hamur Ton</td><td>Ton</td><td><input type="number" id="p_hamur" value="1200.00"></td><td>$ USD</td></tr>
                    </table>
                </div>

                <!-- 2. Baskı Grubu -->
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="section-header">2. Baskı Grubu (Ebat, Renk ve Tiraj)</div>
                    <table class="w-full text-left bg-slate-900 rounded-b">
                        <tr class="text-slate-400 border-b border-slate-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-32">Tiraj Adet Sınırı</th><th class="w-36">Proses & Birim Fiyat</th><th class="w-28">Para Birimi</th></tr>
                        <tr><td>35x50 Cmyk</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" value="1800.00"></td><td>TRY TL</td></tr>
                        <tr><td>35x50 Pantone 1 Renk</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" value="900.00"></td><td>TRY TL</td></tr>
                        <tr><td>35x50 Tiraj</td><td>Adet</td><td><input type="number" value="1000"></td><td><input type="number" value="400.00"></td><td>TRY TL</td></tr>
                        <tr><td>50x70 Cmyk</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" id="p_5070_cmyk" value="3500.00"></td><td>TRY TL</td></tr>
                        <tr><td>50x70 Pantone 1 Renk</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" value="1750.00"></td><td>TRY TL</td></tr>
                        <tr><td>50x70 Tiraj</td><td>Adet</td><td><input type="number" value="1000"></td><td><input type="number" id="p_5070_tiraj" value="800.00"></td><td>TRY TL</td></tr>
                        <tr><td>70x100 Cmyk</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" id="p_70100_cmyk" value="5000.00"></td><td>TRY TL</td></tr>
                        <tr><td>70x100 Pantone 1 Renk</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" value="1750.00"></td><td>TRY TL</td></tr>
                        <tr><td>70x100 Tiraj</td><td>Adet</td><td><input type="number" value="1000"></td><td><input type="number" id="p_70100_tiraj" value="1400.00"></td><td>TRY TL</td></tr>
                    </table>
                </div>

                <!-- 3. Yüzey İşlemleri ve Lak Grubu -->
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="section-header">3. Yüzey İşlemleri ve Lak Grubu</div>
                    <table class="w-full text-left bg-slate-900 rounded-b">
                        <tr class="text-slate-400 border-b border-slate-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-32">Tiraj Adet Sınırı</th><th class="w-36">Proses & Birim Fiyat</th><th class="w-28">Para Birimi</th></tr>
                        <tr><td>50x70 Dispresiyon Lak</td><td>Baskı</td><td><input type="number" value="1000"></td><td><input type="number" value="1500.00"></td><td>TRY TL</td></tr>
                        <tr><td>50x70 Dispresiyon Lak Tiraj</td><td>Adet</td><td><input type="number" value="1000"></td><td><input type="number" value="800.00"></td><td>TRY TL</td></tr>
                        <tr><td>70x100 Dispresiyon Lak</td><td>Baskı</td><td><input type="number" value="2000"></td><td><input type="number" value="2000.00"></td><td>TRY TL</td></tr>
                        <tr><td>70x100 Dispresiyon Lak Tiraj</td><td>Adet</td><td><input type="number" value="1000"></td><td><input type="number" value="1000.00"></td><td>TRY TL</td></tr>
                        <tr><td>Mat Selofan M2</td><td>m2</td><td>-</td><td><input type="number" id="p_mat_sel" value="4.70"></td><td>TRY TL</td></tr>
                        <tr><td>Parlak Selofan M2</td><td>m2</td><td>-</td><td><input type="number" id="p_par_sel" value="4.50"></td><td>TRY TL</td></tr>
                        <tr><td>Lokal Lak Fiyatı 50x70</td><td>Tabaka</td><td><input type="number" value="1000"></td><td><input type="number" value="1500.00"></td><td>TRY TL</td></tr>
                        <tr><td>Lokal Lak Fiyatı 50x70 Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="1.50"></td><td>TRY TL</td></tr>
                        <tr><td>Lokal Lak Fiyatı 70x100</td><td>Tabaka</td><td><input type="number" value="1000"></td><td><input type="number" value="1800.00"></td><td>TRY TL</td></tr>
                        <tr><td>Lokal Lak Fiyatı 70x100 Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="1.50"></td><td>TRY TL</td></tr>
                        <tr><td>Kabartma Lak Fiyatı 50x70</td><td>Tabaka</td><td><input type="number" value="1000"></td><td><input type="number" value="1600.00"></td><td>TRY TL</td></tr>
                        <tr><td>Kabartma Lak Fiyatı 50x70 Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="1.60"></td><td>TRY TL</td></tr>
                        <tr><td>Kabartma Lak Fiyatı 70x100</td><td>Tabaka</td><td><input type="number" value="1000"></td><td><input type="number" value="1900.00"></td><td>TRY TL</td></tr>
                        <tr><td>Kabartma Lak Fiyatı 70x100 Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="1.90"></td><td>TRY TL</td></tr>
                    </table>
                </div>

                <!-- 4. Kesim ve Mücellit Grubu -->
                <div class="glass-card rounded-2xl p-6 space-y-4">
                    <div class="section-header">4. Kesim ve Mücellit Grubu (Çember ve Tiraj)</div>
                    <table class="w-full text-left bg-slate-900 rounded-b">
                        <tr class="text-slate-400 border-b border-slate-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-32">Tiraj Adet Sınırı</th><th class="w-36">Proses & Birim Fiyat</th><th class="w-28">Para Birimi</th></tr>
                        <tr><td>Kazanlı Kesim</td><td>Çember</td><td><input type="number" value="1000"></td><td><input type="number" value="1800.00"></td><td>TRY TL</td></tr>
                        <tr><td>Kazanlı Kesim Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="0.75"></td><td>TRY TL</td></tr>
                        <tr><td>Pedal Kesim</td><td>Çember</td><td><input type="number" value="1000"></td><td><input type="number" value="2500.00"></td><td>TRY TL</td></tr>
                        <tr><td>Pedal Kesim Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="1.00"></td><td>TRY TL</td></tr>
                        <tr><td>Bobts Kesim</td><td>Çember</td><td><input type="number" value="1000"></td><td><input type="number" id="p_bobst" value="3000.00"></td><td>TRY TL</td></tr>
                        <tr><td>Bobts Kesim Tiraj</td><td>Adet</td><td>-</td><td><input type="number" id="p_bobst_tiraj" value="1.50"></td><td>TRY TL</td></tr>
                        <tr><td>Omega Tek Kulak</td><td>Çember</td><td><input type="number" value="10000"></td><td><input type="number" value="2000.00"></td><td>TRY TL</td></tr>
                        <tr><td>Omega Tek Kulak Tiraj</td><td>Adet</td><td>-</td><td><input type="number" value="0.20"></td><td>TRY TL</td></tr>
                        <tr><td>Omega Dip Yapıştırma</td><td>Çember</td><td><input type="number" value="10000"></td><td><input type="number" value="2500.00"></td><td>TRY TL</td></tr>
                        <tr><td>Omega Dip Yapıştırma Tiraj</td><td>Adet</td><td>-</td><td><input type="number" id="p_yap_tiraj" value="0.25"></td><td>TRY TL</td></tr>
                    </table>
                </div>

            </div>
        </div>

        <!-- MODULE 2: PRICE CALCULATOR (MALİYET HESAPLAMA FORMU) -->
        <div id="moduleCalculator" class="hidden w-full space-y-6">
            <div class="flex justify-between items-center bg-slate-900/60 p-4 rounded-2xl border border-slate-800">
                <div class="flex items-center space-x-3">
                    <button onclick="goHome()" class="bg-slate-800 hover:bg-slate-700 text-slate-300 px-4 py-2 rounded-xl border border-slate-700 text-xs font-semibold">
                        <i class="fa-solid fa-arrow-left mr-1"></i> Ana Menü
                    </button>
                    <div>
                        <h3 class="text-lg font-bold text-white">Maliyet Hesaplama Formu</h3>
                        <p class="text-xs text-slate-400">Ürün özelliklerini, kağıt cinsini ve gramajını seçerek anlık fiyat çıkartın.</p>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            <!-- Sol Form Alanı -->
            <div class="lg:col-span-7 space-y-6">
                
                <!-- Tanımlama Bilgileri -->
                <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
                    <div class="flex items-center space-x-3 border-b border-slate-800 pb-4">
                        <div class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">1</div>
                        <h3 class="text-lg font-bold text-white">Ürün Tanımlama Bilgileri</h3>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Firma Adı</label>
                            <input type="text" id="inpFirma" value="Erhan Ticaret" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Ürün Adı / Modeli</label>
                            <input type="text" id="inpUrunAdi" value="Lüks Kutu Ambalaj" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Adet (Tiraj)</label>
                            <input type="number" id="inpAdet" value="5000" step="100" min="1" oninput="calculateCost()" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Baskı Ebadı ve Türü</label>
                            <select id="inpBaskiTuru" onchange="calculateCost()" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                                <option value="5070">50x70 CMYK</option>
                                <option value="70100">70x100 CMYK</option>
                                <option value="3550">35x50 CMYK</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Malzeme Seçimi (Kağıt Cinsi ve Gramajı Ayrı) -->
                <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
                    <div class="flex items-center space-x-3 border-b border-slate-800 pb-4">
                        <div class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">2</div>
                        <h3 class="text-lg font-bold text-white">Kağıt ve Malzeme Seçimi</h3>
                    </div>

                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Kağıt Cinsi</label>
                            <select id="inpKagitCinsi" onchange="calculateCost()" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                                <option value="bristol">Amerikan Bristol</option>
                                <option value="krome">Krome Karton</option>
                                <option value="kuse">Kuşe Kağıt</option>
                                <option value="hamur">1. Hamur</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Kağıt Gramajı (gr/m²)</label>
                            <select id="inpKagitGramaj" onchange="calculateCost()" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                                <option value="200">200 gr</option>
                                <option value="250">250 gr</option>
                                <option value="300" selected>300 gr</option>
                                <option value="350">350 gr</option>
                                <option value="400">400 gr</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Baskı ve Prosesler -->
                <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-6 shadow-xl">
                    <div class="flex items-center space-x-3 border-b border-slate-800 pb-4">
                        <div class="w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">3</div>
                        <h3 class="text-lg font-bold text-white">Ebat, Baskı ve Proses Detayları</h3>
                    </div>

                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs font-semibold text-slate-400 mb-1.5">Ebat (mm x mm x mm)</label>
                            <div class="grid grid-cols-3 gap-3">
                                <input type="number" id="inpEbatX" value="200" oninput="calculateCost()" class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white text-center">
                                <input type="number" id="inpEbatY" value="150" oninput="calculateCost()" class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white text-center">
                                <input type="number" id="inpEbatZ" value="50" oninput="calculateCost()" class="bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white text-center">
                            </div>
                        </div>

                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div>
                                <label class="block text-xs font-semibold text-slate-400 mb-1.5">Laminasyon</label>
                                <select id="inpLaminasyon" onchange="calculateCost()" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                                    <option value="mat">Mat Selofan</option>
                                    <option value="parlak">Parlak Selofan</option>
                                    <option value="yok">Yok</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-400 mb-1.5">Kesim Türü</label>
                                <select id="inpKesim" onchange="calculateCost()" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white">
                                    <option value="bobst">Bobst Kesim</option>
                                    <option value="kazanli">Kazanlı / Pedal Kesim</option>
                                    <option value="yok">Yok</option>
                                </select>
                            </div>
                        </div>

                        <div class="flex items-center space-x-6 pt-3">
                            <label class="flex items-center space-x-2 cursor-pointer">
                                <input type="checkbox" id="inpYapistirma" checked onchange="calculateCost()" class="w-4 h-4 accent-amber-500 rounded bg-slate-900 border-slate-700">
                                <span class="text-sm text-slate-300">Omega Yapıştırma</span>
                            </label>
                            <label class="flex items-center space-x-2 cursor-pointer">
                                <input type="checkbox" id="inpNakliye" checked onchange="calculateCost()" class="w-4 h-4 accent-amber-500 rounded bg-slate-900 border-slate-700">
                                <span class="text-sm text-slate-300">Nakliye Dahil</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Sağ Özet ve Hesaplama Sonuçları -->
            <div class="lg:col-span-5 space-y-6">
                
                <!-- Planlama ve Proses Bilgileri -->
                <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-4 shadow-xl">
                    <h3 class="text-base font-bold text-white border-b border-slate-800 pb-3 flex items-center justify-between">
                        <span>Planlama & Proses Dökümü</span>
                        <i class="fa-solid fa-file-invoice text-amber-500"></i>
                    </h3>
                    <div class="space-y-3 text-sm">
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Kağıt Miktarı:</span>
                            <span id="resKg" class="font-semibold">-</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Tabaka Adedi:</span>
                            <span id="resTabaka" class="font-semibold">-</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Baskı Maliyeti:</span>
                            <span id="resBaski" class="font-semibold">-</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Selofan Maliyeti:</span>
                            <span id="resSelofan" class="font-semibold">-</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Kesim Maliyeti:</span>
                            <span id="resKesim" class="font-semibold">-</span>
                        </div>
                        <div class="flex justify-between text-slate-300">
                            <span class="text-slate-400">Yapıştırma & Nakliye:</span>
                            <span id="resEkIslem" class="font-semibold">-</span>
                        </div>
                    </div>
                </div>

                <!-- Maliyet ve Fiyatlandırma Kartı -->
                <div class="glass-card rounded-3xl p-6 sm:p-8 space-y-6 border-2 border-amber-500/40 bg-gradient-to-br from-slate-900/90 to-amber-950/20 shadow-2xl">
                    <div class="flex justify-between items-center border-b border-slate-800 pb-4">
                        <h3 class="text-lg font-bold text-white">Maliyet & Karlı Teklif</h3>
                        <div class="flex items-center space-x-2">
                            <span class="text-xs text-slate-400 font-medium">Kar %:</span>
                            <input type="number" id="inpKarOrani" value="30" min="0" max="100" oninput="calculateCost()" class="w-16 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-center text-amber-400 font-bold text-sm focus:outline-none">
                        </div>
                    </div>

                    <div class="grid grid-cols-2 gap-4">
                        <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
                            <div class="text-xs text-slate-400 mb-1">Toplam Maliyet</div>
                            <div id="resToplamMaliyet" class="text-lg font-bold text-white">₺0.00</div>
                        </div>
                        <div class="bg-slate-900/80 p-4 rounded-2xl border border-slate-800">
                            <div class="text-xs text-slate-400 mb-1">Net Kar Toplamı</div>
                            <div id="resNetKar" class="text-lg font-bold text-emerald-400">₺0.00</div>
                        </div>
                    </div>

                    <div class="bg-amber-500/10 border border-amber-500/30 p-5 rounded-2xl flex justify-between items-center">
                        <div>
                            <div class="text-xs text-amber-300 font-medium uppercase tracking-wider">Toplam Karlı Satış Fiyatı</div>
                            <div id="resToplamKarliFiyat" class="text-2xl font-black text-amber-400 mt-0.5">₺0.00</div>
                        </div>
                        <div class="text-right">
                            <div class="text-xs text-slate-400">Birim Maliyet</div>
                            <div id="resBirimMaliyet" class="text-sm font-bold text-slate-300">₺0.00</div>
                        </div>
                    </div>

                    <div class="pt-2">
                        <div class="flex justify-between items-center bg-slate-900 px-5 py-4 rounded-2xl border border-slate-800">
                            <span class="text-sm font-semibold text-slate-200">Karlı Birim Satış Fiyatı:</span>
                            <span id="resKarliBirimFiyat" class="text-2xl font-black text-emerald-400">₺0.00</span>
                        </div>
                    </div>

                    <button onclick="alert('Teklif başarıyla PDF olarak hazırlandı.')" class="w-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-950 font-bold py-3.5 rounded-xl shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center space-x-2">
                        <i class="fa-solid fa-file-pdf"></i>
                        <span>Teklif PDF İndir</span>
                    </button>
                </div>

            </div>

        </div>
        </div>

    </main>

    <script>
        function switchTab(tab) {
            const welcome = document.getElementById('welcomeSection');
            const modParams = document.getElementById('moduleParams');
            const modCalc = document.getElementById('moduleCalculator');

            welcome.classList.add('hidden');
            if (tab === 'params') {
                modParams.classList.remove('hidden');
                modCalc.classList.add('hidden');
            } else {
                modCalc.classList.remove('hidden');
                modParams.classList.add('hidden');
                calculateCost();
            }
        }

        function goHome() {
            document.getElementById('welcomeSection').classList.remove('hidden');
            document.getElementById('moduleParams').classList.add('hidden');
            document.getElementById('moduleCalculator').classList.add('hidden');
        }

        function syncKur() {
            let u = document.getElementById('curUsd').value;
            let e = document.getElementById('curEur').value;
            document.getElementById('lblUsd').innerText = u;
            document.getElementById('lblEur').innerText = e;
            calculateCost();
        }

        function calculateCost() {
            let usdKur = parseFloat(document.getElementById('curUsd').value) || 49.97;
            let eurKur = parseFloat(document.getElementById('curEur').value) || 56.00;

            const adet = parseFloat(document.getElementById('inpAdet').value) || 0;
            const kagitCinsi = document.getElementById('inpKagitCinsi').value;
            const gramaj = parseFloat(document.getElementById('inpKagitGramaj').value) || 300;
            const baskiTuru = document.getElementById('inpBaskiTuru').value;
            const laminasyon = document.getElementById('inpLaminasyon').value;
            const kesimTuru = document.getElementById('inpKesim').value;
            const yapistirmaVar = document.getElementById('inpYapistirma').checked;
            const nakliyeVar = document.getElementById('inpNakliye').checked;
            const karOrani = parseFloat(document.getElementById('inpKarOrani').value) || 0;

            const x = (parseFloat(document.getElementById('inpEbatX').value) || 200) / 1000;
            const y = (parseFloat(document.getElementById('inpEbatY').value) || 150) / 1000;

            let tonFiyat = 825.0;
            let paraBirim = 'USD';
            if(kagitCinsi === 'bristol') { tonFiyat = parseFloat(document.getElementById('p_bristol').value) || 825.0; paraBirim = 'USD'; }
            else if(kagitCinsi === 'krome') { tonFiyat = parseFloat(document.getElementById('p_krome').value) || 40000.0; paraBirim = 'TL'; }
            else if(kagitCinsi === 'kuse') { tonFiyat = parseFloat(document.getElementById('p_kuse').value) || 850.0; paraBirim = 'EUR'; }
            else if(kagitCinsi === 'hamur') { tonFiyat = parseFloat(document.getElementById('p_hamur').value) || 1200.0; paraBirim = 'USD'; }

            let tonFiyatTL = tonFiyat;
            if(paraBirim === 'USD') tonFiyatTL = tonFiyat * usdKur;
            else if(paraBirim === 'EUR') tonFiyatTL = tonFiyat * eurKur;

            let tabakaAdeti = Math.max(1, Math.ceil(adet / 2));
            let kgKagit = Math.round((tabakaAdeti * x * y * gramaj) / 2);
            let kagitMaliyeti = (kgKagit / 1000) * tonFiyatTL;

            let baskiMaliyeti = parseFloat(document.getElementById('p_5070_cmyk').value) + (adet * (parseFloat(document.getElementById('p_5070_tiraj').value) / 1000));
            if(baskiTuru === '70100') {
                baskiMaliyeti = parseFloat(document.getElementById('p_70100_cmyk').value) + (adet * (parseFloat(document.getElementById('p_70100_tiraj').value) / 1000));
            }

            let selofanM2 = tabakaAdeti * 0.35;
            let selofanBirim = laminasyon === 'mat' ? parseFloat(document.getElementById('p_mat_sel').value) : parseFloat(document.getElementById('p_par_sel').value);
            let selofanMaliyeti = laminasyon !== 'yok' ? selofanM2 * selofanBirim : 0;

            let kesimMaliyeti = 0;
            if(kesimTuru === 'bobst') {
                kesimMaliyeti = parseFloat(document.getElementById('p_bobst').value) + (adet * parseFloat(document.getElementById('p_bobst_tiraj').value));
            } else if(kesimTuru === 'kazanli') {
                kesimMaliyeti = 1800.0 + (adet * 0.75);
            }

            let yapistirmaMaliyeti = yapistirmaVar ? (2500.0 + (adet * parseFloat(document.getElementById('p_yap_tiraj').value))) : 0;
            let nakliyeMaliyeti = nakliyeVar ? 4000.0 : 0;
            let toplamEkIslem = yapistirmaMaliyeti + nakliyeMaliyeti;

            let toplamMaliyet = kagitMaliyeti + baskiMaliyeti + selofanMaliyeti + kesimMaliyeti + toplamEkIslem;
            let netKar = toplamMaliyet * (karOrani / 100);
            let toplamKarliFiyat = toplamMaliyet + netKar;

            let birimMaliyet = adet > 0 ? toplamMaliyet / adet : 0;
            let karliBirimFiyat = adet > 0 ? toplamKarliFiyat / adet : 0;

            document.getElementById('resKg').innerText = kgKagit + " kg";
            document.getElementById('resTabaka').innerText = tabakaAdeti.toLocaleString('tr-TR') + " tabaka";
            document.getElementById('resBaski').innerText = "₺" + baskiMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2});
            document.getElementById('resSelofan').innerText = "₺" + selofanMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2});
            document.getElementById('resKesim').innerText = "₺" + kesimMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2});
            document.getElementById('resEkIslem').innerText = "₺" + toplamEkIslem.toLocaleString('tr-TR', {minimumFractionDigits: 2});

            document.getElementById('resToplamMaliyet').innerText = "₺" + toplamMaliyet.toLocaleString('tr-TR', {minimumFractionDigits: 2});
            document.getElementById('resNetKar').innerText = "₺" + netKar.toLocaleString('tr-TR', {minimumFractionDigits: 2});
            document.getElementById('resToplamKarliFiyat').innerText = "₺" + toplamKarliFiyat.toLocaleString('tr-TR', {minimumFractionDigits: 2});
            document.getElementById('resBirimMaliyet').innerText = "₺" + birimMaliyet.toLocaleString('tr-TR', {minimumFractionDigits: 4});
            document.getElementById('resKarliBirimFiyat').innerText = "₺" + karliBirimFiyat.toLocaleString('tr-TR', {minimumFractionDigits: 4});
        }
    </script>
</body>
</html>
