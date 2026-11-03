<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matbaa Ambalaj Maliyet & Fiyatlandırma Sistemi</title>
    <script src="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0e1117; color: #c9d1d9; }
        .section-header { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #fff; font-weight: bold; padding: 10px 15px; border-radius: 6px 6px 0 0; text-transform: uppercase; font-size: 13px; letter-spacing: 0.5px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        input, select { background-color: #0d1117 !important; color: #ffffff !important; border: 1px solid #30363d !important; padding: 6px 10px; border-radius: 4px; width: 100%; font-size: 13px; }
        input:focus, select:focus { outline: none; border-color: #f59e0b !important; ring: 1px #f59e0b; }
        table th, table td { padding: 6px 8px; border-bottom: 1px solid #21262d; font-size: 12px; }
    </style>
</head>
<body class="p-6">

    <div class="max-w-7xl mx-auto space-y-6">
        
        <!-- ÜST BAŞLIK VE İKİ ANA BUTON -->
        <div class="card p-6 flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
                <h1 class="text-2xl font-bold text-yellow-500">MATBAAM - Ambalaj & Matbaa Maliyet Sistemi</h1>
                <p class="text-xs text-gray-400">Parametrik Maliyet Analizi ve Teklif Hesaplama Platformu</p>
            </div>
            <div class="flex space-x-3">
                <button onclick="showPage('params')" id="btn-params" class="px-6 py-3 rounded-lg font-bold text-sm bg-yellow-500 text-gray-900 shadow transition hover:bg-yellow-400">1. Parametreler</button>
                <button onclick="showPage('calc')" id="btn-calc" class="px-6 py-3 rounded-lg font-bold text-sm bg-gray-800 text-gray-300 border border-gray-700 transition hover:bg-gray-700">2. Fiyat Çıkart</button>
            </div>
        </div>

        <!-- SAYFA 1: PARAMETRELER (FİYAT LİSTESİ) -->
        <div id="page-params" class="space-y-6">
            <div class="card p-6 space-y-6">
                <div class="flex justify-between items-center border-b border-gray-700 pb-3">
                    <h2 class="text-xl font-bold text-white">Matbaa Maliyet Parametreleri Fiyat Listesi</h2>
                    <div class="flex gap-4 text-sm font-semibold">
                        <div class="bg-gray-800 px-3 py-1.5 rounded border border-gray-700">Dolar Kuru: <input type="number" id="cur_usd" value="49.97" step="0.01" class="w-20 inline-block text-right ml-2" oninput="hesapla()"> TL</div>
                        <div class="bg-gray-800 px-3 py-1.5 rounded border border-gray-700">Euro Kuru: <input type="number" id="cur_eur" value="56.00" step="0.01" class="w-20 inline-block text-right ml-2" oninput="hesapla()"> TL</div>
                    </div>
                </div>

                <!-- 1. Kağıt ve Karton Grubu -->
                <div>
                    <div class="section-header">1. Kağıt ve Karton Grubu (Ton Maliyetleri)</div>
                    <table class="w-full text-left bg-gray-900 rounded-b">
                        <tr class="text-gray-400 border-b border-gray-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-36">Ton Fiyat</th><th class="w-28">Para Birimi</th></tr>
                        <tr><td>Amerikan Bristol Ton</td><td>Ton</td><td><input type="number" id="p_bristol" value="825.00"></td><td>$ USD</td></tr>
                        <tr><td>Krome Karton Ton</td><td>Ton</td><td><input type="number" id="p_krome" value="40000.00"></td><td>TRY TL</td></tr>
                        <tr><td>Kuşe Ton</td><td>Ton</td><td><input type="number" id="p_kuse" value="850.00"></td><td>€ EUR</td></tr>
                        <tr><td>1. Hamur Ton</td><td>Ton</td><td><input type="number" id="p_hamur" value="1200.00"></td><td>$ USD</td></tr>
                    </table>
                </div>

                <!-- 2. Baskı Grubu -->
                <div>
                    <div class="section-header">2. Baskı Grubu (Ebat, Renk ve Tiraj)</div>
                    <table class="w-full text-left bg-gray-900 rounded-b">
                        <tr class="text-gray-400 border-b border-gray-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-32">Tiraj Adet Sınırı</th><th class="w-36">Proses & Birim Fiyat</th><th class="w-28">Para Birimi</th></tr>
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
                <div>
                    <div class="section-header">3. Yüzey İşlemleri ve Lak Grubu</div>
                    <table class="w-full text-left bg-gray-900 rounded-b">
                        <tr class="text-gray-400 border-b border-gray-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-32">Tiraj Adet Sınırı</th><th class="w-36">Proses & Birim Fiyat</th><th class="w-28">Para Birimi</th></tr>
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
                <div>
                    <div class="section-header">4. Kesim ve Mücellit Grubu (Çember ve Tiraj)</div>
                    <table class="w-full text-left bg-gray-900 rounded-b">
                        <tr class="text-gray-400 border-b border-gray-800"><th>Parametre Adı</th><th class="w-24">Birim</th><th class="w-32">Tiraj Adet Sınırı</th><th class="w-36">Proses & Birim Fiyat</th><th class="w-28">Para Birimi</th></tr>
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

        <!-- SAYFA 2: FİYAT ÇIKART (MALİYET HESAPLAMA) -->
        <div id="page-calc" class="hidden grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            <!-- Sol Form -->
            <div class="lg:col-span-7 card p-6 space-y-4">
                <h2 class="text-lg font-bold text-yellow-500 border-b border-gray-700 pb-2">Ürün Tanımlama ve Proses Seçimi</h2>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Firma Adı</label>
                        <input type="text" id="firma" value="Erhan Ticaret">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Ürün Adı / Modeli</label>
                        <input type="text" id="urun_adi" value="Lüks Kutu Ambalaj">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Adet (Tiraj)</label>
                        <input type="number" id="adet" value="5000" oninput="hesapla()">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Kağıt Cinsi</label>
                        <select id="kagit_cinsi" onchange="hesapla()">
                            <option value="bristol">Amerikan Bristol</option>
                            <option value="krome">Krome Karton</option>
                            <option value="kuse">Kuşe Kağıt</option>
                            <option value="hamur">1. Hamur</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Kağıt Gramajı (gr/m²)</label>
                        <select id="kagit_gramaj" onchange="hesapla()">
                            <option value="200">200 gr</option>
                            <option value="250">250 gr</option>
                            <option value="300" selected>300 gr</option>
                            <option value="350">350 gr</option>
                            <option value="400">400 gr</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Baskı Ebadı ve Türü</label>
                        <select id="baski_turu" onchange="hesapla()">
                            <option value="5070">50x70 CMYK</option>
                            <option value="70100">70x100 CMYK</option>
                            <option value="3550">35x50 CMYK</option>
                        </select>
                    </div>
                    <div class="md:col-span-2">
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Ebat (mm x mm x mm)</label>
                        <div class="grid grid-cols-3 gap-2">
                            <input type="number" id="ebat_x" value="200" oninput="hesapla()">
                            <input type="number" id="ebat_y" value="150" oninput="hesapla()">
                            <input type="number" id="ebat_z" value="50" oninput="hesapla()">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Laminasyon</label>
                        <select id="laminasyon" onchange="hesapla()">
                            <option value="mat">Mat Selofan</option>
                            <option value="parlak">Parlak Selofan</option>
                            <option value="yok">Yok</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Kesim Türü</label>
                        <select id="kesim_turu" onchange="hesapla()">
                            <option value="bobst">Bobst Kesim</option>
                            <option value="kazanli">Kazanlı / Pedal Kesim</option>
                            <option value="yok">Yok</option>
                        </select>
                    </div>
                </div>

                <div class="flex items-center space-x-6 pt-2">
                    <label class="flex items-center text-sm"><input type="checkbox" id="yapistirma" checked onchange="hesapla()" class="mr-2"> Omega Yapıştırma</label>
                    <label class="flex items-center text-sm"><input type="checkbox" id="nakliye" checked onchange="hesapla()" class="mr-2"> Nakliye Dahil</label>
                </div>
            </div>

            <!-- Sağ Özet ve Sonuçlar -->
            <div class="lg:col-span-5 space-y-6">
                <!-- Proses Bilgileri -->
                <div class="card p-6 space-y-3">
                    <h3 class="text-md font-bold text-gray-300 border-b border-gray-700 pb-2">Planlama ve Proses Bilgileri</h3>
                    <div class="flex justify-between text-sm"><span class="text-gray-400">Kağıt Miktarı:</span><span class="font-semibold" id
