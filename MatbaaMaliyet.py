<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matbaa Ambalaj ve Maliyet Hesaplama Formu</title>
    <script src="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f3f4f6; }
        .table-header { background-color: #f59e0b; color: #fff; font-weight: bold; }
        input, select { border: 1px solid #d1d5db; padding: 6px 10px; border-radius: 4px; width: 100%; font-size: 14px; }
        input:focus, select:focus { outline: none; ring: 2px; border-color: #f59e0b; }
    </style>
</head>
<body class="p-6">

    <div class="max-w-7xl mx-auto space-y-8">
        
        <!-- Başlık -->
        <div class="bg-white p-6 rounded-lg shadow-md flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-gray-800">Matbaa Ambalaj Maliyet & Fiyatlandırma Sistemi</h1>
                <p class="text-sm text-gray-500">Parametrik Matbaa Maliyet Analizi ve Teklif Formu</p>
            </div>
            <div class="text-right">
                <span class="text-xs bg-yellow-100 text-yellow-800 font-semibold px-3 py-1 rounded-full">Tarih: 28.01.2026</span>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            <!-- SOL TARAF: PARAMETRELER FİYAT LİSTESİ (GÜNCELLENEBİLİR) -->
            <div class="lg:col-span-5 bg-white p-6 rounded-lg shadow-md space-y-6">
                <h2 class="text-lg font-bold text-gray-800 border-b pb-2">Matbaa Maliyet Parametreleri Fiyat Listesi</h2>

                <!-- 1. Kağıt ve Karton Grubu -->
                <div>
                    <div class="table-header p-2 text-sm rounded-t">1. Kağıt ve Karton Grubu (Ton Maliyetleri)</div>
                    <table class="w-full text-xs border-collapse border border-gray-200">
                        <tr class="bg-gray-50 font-semibold border-b">
                            <td class="p-2">Parametre Adı</td>
                            <td class="p-2 w-16">Birim</td>
                            <td class="p-2 w-24">Ton Fiyat</td>
                            <td class="p-2 w-16">Birim</td>
                        </tr>
                        <tr><td class="p-2">Amerikan Bristol Ton</td><td class="p-2">Ton</td><td class="p-2"><input type="number" id="p_bristol" value="1200" class="text-right"></td><td class="p-2 text-center">EUR/USD</td></tr>
                        <tr class="bg-gray-50"><td class="p-2">Krome Karton Ton</td><td class="p-2">Ton</td><td class="p-2"><input type="number" id="p_krome" value="1100" class="text-right"></td><td class="p-2 text-center">EUR/USD</td></tr>
                        <tr><td class="p-2">Kuşe Ton</td><td class="p-2">Ton</td><td class="p-2"><input type="number" id="p_kuse" value="1050" class="text-right"></td><td class="p-2 text-center">EUR/USD</td></tr>
                        <tr class="bg-gray-50"><td class="p-2">1. Hamur Ton</td><td class="p-2">Ton</td><td class="p-2"><input type="number" id="p_hamur" value="1150" class="text-right"></td><td class="p-2 text-center">EUR/USD</td></tr>
                    </table>
                </div>

                <!-- 2. Baskı Grubu -->
                <div>
                    <div class="table-header p-2 text-sm rounded-t">2. Baskı Grubu (Ebat, Renk ve Tiraj)</div>
                    <table class="w-full text-xs border-collapse border border-gray-200">
                        <tr class="bg-gray-50 font-semibold border-b">
                            <td class="p-2">Parametre Adı</td>
                            <td class="p-2 w-14">Birim</td>
                            <td class="p-2 w-16">Tiraj Sınır</td>
                            <td class="p-2 w-20">Proses Fiyat</td>
                        </tr>
                        <tr><td class="p-2">35x50 Cmyk</td><td class="p-2">Baskı</td><td class="p-2"><input type="number" value="1000" class="text-center"></td><td class="p-2"><input type="number" value="1500" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">35x50 Pantone 1 Renk</td><td class="p-2">Baskı</td><td class="p-2"><input type="number" value="1000" class="text-center"></td><td class="p-2"><input type="number" value="1800" class="text-right"></td></tr>
                        <tr><td class="p-2">35x50 Tiraj</td><td class="p-2">Adet</td><td class="p-2">-</td><td class="p-2"><input type="number" value="0.75" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">50x70 Cmyk</td><td class="p-2">Baskı</td><td class="p-2"><input type="number" value="1000" class="text-center"></td><td class="p-2"><input type="number" id="baski_5070_cmyk" value="2500" class="text-right"></td></tr>
                        <tr><td class="p-2">50x70 Pantone 1 Renk</td><td class="p-2">Baskı</td><td class="p-2"><input type="number" value="1000" class="text-center"></td><td class="p-2"><input type="number" value="3000" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">50x70 Tiraj</td><td class="p-2">Adet</td><td class="p-2">-</td><td class="p-2"><input type="number" id="baski_5070_tiraj" value="1.50" class="text-right"></td></tr>
                        <tr><td class="p-2">70x100 Cmyk</td><td class="p-2">Baskı</td><td class="p-2"><input type="number" value="1000" class="text-center"></td><td class="p-2"><input type="number" id="baski_70100_cmyk" value="3500" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">70x100 Pantone 1 Renk</td><td class="p-2">Baskı</td><td class="p-2"><input type="number" value="1000" class="text-center"></td><td class="p-2"><input type="number" value="4200" class="text-right"></td></tr>
                        <tr><td class="p-2">70x100 Tiraj</td><td class="p-2">Adet</td><td class="p-2">-</td><td class="p-2"><input type="number" id="baski_70100_tiraj" value="2.00" class="text-right"></td></tr>
                    </table>
                </div>

                <!-- 3. Yüzey İşlemleri ve Lak Grubu -->
                <div>
                    <div class="table-header p-2 text-sm rounded-t">3. Yüzey İşlemleri ve Lak Grubu</div>
                    <table class="w-full text-xs border-collapse border border-gray-200">
                        <tr class="bg-gray-50 font-semibold border-b">
                            <td class="p-2">Parametre Adı</td>
                            <td class="p-2 w-16">Birim</td>
                            <td class="p-2 w-20">Proses Fiyat</td>
                        </tr>
                        <tr><td class="p-2">Mat Selofan M2</td><td class="p-2">m2</td><td class="p-2"><input type="number" id="p_mat_selofan" value="4.0" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">Parlak Selofan M2</td><td class="p-2">m2</td><td class="p-2"><input type="number" id="p_parlak_selofan" value="3.5" class="text-right"></td></tr>
                        <tr><td class="p-2">Lokal Lak Fiyatı 50x70</td><td class="p-2">Tabaka</td><td class="p-2"><input type="number" value="1.20" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">Kabartma Lak Fiyatı 50x70</td><td class="p-2">Tabaka</td><td class="p-2"><input type="number" value="1.50" class="text-right"></td></tr>
                    </table>
                </div>

                <!-- 4. Kesim ve Mücellit Grubu -->
                <div>
                    <div class="table-header p-2 text-sm rounded-t">4. Kesim ve Mücellit Grubu</div>
                    <table class="w-full text-xs border-collapse border border-gray-200">
                        <tr class="bg-gray-50 font-semibold border-b">
                            <td class="p-2">Parametre Adı</td>
                            <td class="p-2 w-16">Birim</td>
                            <td class="p-2 w-20">Proses Fiyat</td>
                        </tr>
                        <tr><td class="p-2">Kazanlı Veya Pedal Kesim</td><td class="p-2">Çember</td><td class="p-2"><input type="number" value="1500" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">Kazanlı Kesim Tiraj</td><td class="p-2">Adet</td><td class="p-2"><input type="number" value="1.50" class="text-right"></td></tr>
                        <tr><td class="p-2">Bobst Kesim</td><td class="p-2">Çember</td><td class="p-2"><input type="number" value="2500" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">Bobst Kesim Tiraj</td><td class="p-2">Adet</td><td class="p-2"><input type="number" value="0.80" class="text-right"></td></tr>
                        <tr><td class="p-2">Omega Dip Yapıştırma</td><td class="p-2">Çember</td><td class="p-2"><input type="number" value="1500" class="text-right"></td></tr>
                        <tr class="bg-gray-50"><td class="p-2">Omega Yapıştırma Tiraj</td><td class="p-2">Adet</td><td class="p-2"><input type="number" id="p_yapistirma_tiraj" value="0.50" class="text-right"></td></tr>
                    </table>
                </div>
            </div>

            <!-- SAĞ TARAF: TANIMLAMA BİLGİLERİ VE MALİYET HESAPLAMA FORMU -->
            <div class="lg:col-span-7 space-y-6">
                
                <!-- Tanımlama Bilgileri -->
                <div class="bg-white p-6 rounded-lg shadow-md space-y-4">
                    <h2 class="text-lg font-bold text-gray-800 border-b pb-2">Tanımlama Bilgileri</h2>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Firma</label>
                            <input type="text" id="firma" value="Erhan Ticaret">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Ürün Adı</label>
                            <input type="text" id="urun_adi" value="Deneme Ambalaj Kutusu">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Adet (Tiraj)</label>
                            <input type="number" id="adet" value="5000" oninput="hesapla()">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Kağıt Cinsi</label>
                            <select id="kagit_cinsi" onchange="hesapla()">
                                <option value="bristol">300 gr Amerikan Bristol</option>
                                <option value="krome">300 gr Krome Karton</option>
                                <option value="kuse">300 gr Kuşe</option>
                                <option value="hamur">1. Hamur</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Baskı Türü</label>
                            <select id="baski_turu" onchange="hesapla()">
                                <option value="5070_cmyk">50x70 CMYK</option>
                                <option value="70100_cmyk">70x100 CMYK</option>
                                <option value="3550_cmyk">35x50 CMYK</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Ebat (mm x mm x mm)</label>
                            <div class="grid grid-cols-3 gap-2">
                                <input type="number" id="ebat_x" value="200" placeholder="X" oninput="hesapla()">
                                <input type="number" id="ebat_y" value="150" placeholder="Y" oninput="hesapla()">
                                <input type="number" id="ebat_z" value="50" placeholder="Z" oninput="hesapla()">
                            </div>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Laminasyon</label>
                            <select id="laminasyon" onchange="hesapla()">
                                <option value="mat">Mat Selofan</option>
                                <option value="parlak">Parlak Selofan</option>
                                <option value="yok">Yok</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Sıvama / Ondüle</label>
                            <select id="sivama" onchange="hesapla()">
                                <option value="var">Ondüle / Sıvama Var</option>
                                <option value="yok">Yok</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Kesim & Bıçak</label>
                            <select id="kesim" onchange="hesapla()">
                                <option value="bobst">Bobst / Kazanlı Kesim Var</option>
                                <option value="yok">Yok</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Yapıştırma & Nakliye</label>
                            <div class="flex items-center space-x-4 mt-2">
                                <label class="flex items-center text-sm"><input type="checkbox" id="yapistirma" checked onchange="hesapla()" class="mr-2"> Yapıştırma</label>
                                <label class="flex items-center text-sm"><input type="checkbox" id="nakliye" checked onchange="hesapla()" class="mr-2"> Nakliye</label>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Proses Bilgileri (Detaylı Döküm) -->
                <div class="bg-white p-6 rounded-lg shadow-md space-y-4">
                    <h2 class="text-lg font-bold text-gray-800 border-b pb-2">Planlama ve Proses Bilgileri</h2>
                    <table class="w-full text-sm border-collapse">
                        <tr class="border-b"><td class="py-2 text-gray-600">Kaç kilogram kağıt:</td><td class="py-2 font-semibold text-right" id="res_kg">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Kaç tabaka baskı:</td><td class="py-2 font-semibold text-right" id="res_tabaka">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Baskı Ebadı & Maliyeti:</td><td class="py-2 font-semibold text-right" id="res_baski">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Selofan Miktarı & Maliyeti:</td><td class="py-2 font-semibold text-right" id="res_selofan">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Ondüle / Sıvama Maliyeti:</td><td class="py-2 font-semibold text-right" id="res_sivama">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Bıçak & Kesim Maliyeti:</td><td class="py-2 font-semibold text-right" id="res_kesim">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Yapıştırma Maliyeti:</td><td class="py-2 font-semibold text-right" id="res_yapistirma">-</td></tr>
                        <tr class="border-b"><td class="py-2 text-gray-600">Nakliye Maliyeti:</td><td class="py-2 font-semibold text-right" id="res_nakliye">₺4,000.00</td></tr>
                    </table>
                </div>

                <!-- Maliyet ve Fiyatlandırma Özet Kutusu -->
                <div class="bg-gray-900 text-white p-6 rounded-lg shadow-lg space-y-4">
                    <div class="flex justify-between items-center border-b border-gray-700 pb-3">
                        <h2 class="text-lg font-bold text-yellow-400">Maliyet ve Fiyatlandırma Özeti</h2>
                        <div class="flex items-center space-x-2">
                            <span class="text-xs text-gray-300">Kar Marjı (%):</span>
                            <input type="number" id="kar_orani" value="30" class="w-20 bg-gray-800 text-white text-center rounded px-2 py-1" oninput="hesapla()">
                        </div>
                    </div>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p class="text-gray-400 text-xs">Toplam Maliyet</p>
                            <p class="text-xl font-bold" id="toplam_maliyet">₺0.00</p>
                        </div>
                        <div>
                            <p class="text-gray-400 text-xs">Toplam Karlı Fiyat (Satış)</p>
                            <p class="text-xl font-bold text-yellow-400" id="toplam_karli_fiyat">₺0.00</p>
                        </div>
                        <div>
                            <p class="text-gray-400 text-xs">Net Kar Toplamı</p>
                            <p class="text-lg font-semibold text-green-400" id="net_kar">₺0.00</p>
                        </div>
                        <div>
                            <p class="text-gray-400 text-xs">Birim Maliyet</p>
                            <p class="text-lg font-semibold" id="birim_maliyet">₺0.00</p>
                        </div>
                    </div>
                    <div class="pt-3 border-t border-gray-700 flex justify-between items-center">
                        <span class="text-sm font-semibold text-yellow-300">Karlı Birim Fiyat (Adet):</span>
                        <span class="text-2xl font-bold text-yellow-400" id="karli_birim_fiyat">₺0.00</span>
                    </div>
                </div>

            </div>

        </div>
    </div>

    <script>
        function hesapla() {
            let adet = parseFloat(document.getElementById('adet').value) || 0;
            let kagitCinsi = document.getElementById('kagit_cinsi').value;
            let baskiTuru = document.getElementById('baski_turu').value;
            let laminasyon = document.getElementById('laminasyon').value;
            let sivama = document.getElementById('sivama').value;
            let kesim = document.getElementById('kesim').value;
            let yapistirmaVar = document.getElementById('yapistirma').checked;
            let nakliyeVar = document.getElementById('nakliye').checked;
            let karOrani = parseFloat(document.getElementById('kar_orani').value) || 0;

            // Parametre Fiyatları Alınır
            let tonFiyatEUR = 1200;
            if(kagitCinsi === 'bristol') tonFiyatEUR = parseFloat(document.getElementById('p_bristol').value) || 1200;
            if(kagitCinsi === 'krome') tonFiyatEUR = parseFloat(document.getElementById('p_krome').value) || 1100;
            if(kagitCinsi === 'kuse') tonFiyatEUR = parseFloat(document.getElementById('p_kuse').value) || 1050;
            if(kagitCinsi === 'hamur') tonFiyatEUR = parseFloat(document.getElementById('p_hamur').value) || 1150;
            
            let eurKur = 35.0; // Sabit Euro kuru varsayımı veya güncel kur
            let tonFiyatTL = tonFiyatEUR * eurKur;

            // Örnek Hesaplamalar (Tabaka ve Gramaj Simülasyonu)
            let tabakaAdeti = Math.ceil(adet / 2); // Formülasyon simülasyonu
            let kgKağıt = Math.round((tabakaAdeti * 0.3 * 0.5 * 300) / 1000); // Yaklaşık KG
            let kagitMaliyeti = (kgKağıt / 1000) * tonFiyatTL;

            let baskiMaliyeti = 2500 + (adet * 1.5);
            if(baskiTuru === '70100_cmyk') baskiMaliyeti = 3500 + (adet * 2.0);

            let selofanM2 = tabakaAdeti * 0.35;
            let selofanBirim = laminasyon === 'mat' ? 4.0 : 3.5;
            let selofanMaliyeti = laminasyon !== 'yok' ? selofanM2 * selofanBirim : 0;

            let sivamaMaliyeti = sivama === 'var' ? tabakaAdeti * 2.5 : 0;
            let kesimMaliyeti = kesim === 'bobst' ? 2500 + (adet * 0.8) : 0;
            let yapistirmaMaliyeti = yapistirmaVar ? adet * 0.5 : 0;
            let nakliyeMaliyeti = nakliyeVar ? 4000 : 0;

            let toplamMaliyet = kagitMaliyeti + baskiMaliyeti + selofanMaliyeti + sivamaMaliyeti + kesimMaliyeti + yapistirmaMaliyeti + nakliyeMaliyeti;
            let netKar = toplamMaliyet * (karOrani / 100);
            let toplamKarliFiyat = toplamMaliyet + netKar;

            let birimMaliyet = adet > 0 ? toplamMaliyet / adet : 0;
            let karliBirimFiyat = adet > 0 ? toplamKarliFiyat / adet : 0;

            // Alanlara Yazdırma
            document.getElementById('res_kg').innerText = kgKağıt + " kg";
            document.getElementById('res_tabaka').innerText = tabakaAdeti + " adet tabaka";
            document.getElementById('res_baski').innerText = "₺" + baskiMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('res_selofan').innerText = Math.round(selofanM2) + " m² / ₺" + selofanMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('res_sivama').innerText = "₺" + sivamaMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('res_kesim').innerText = "₺" + kesimMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('res_yapistirma').innerText = "₺" + yapistirmaMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('res_nakliye').innerText = "₺" + nakliyeMaliyeti.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            document.getElementById('toplam_maliyet').innerText = "₺" + toplamMaliyet.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('toplam_karli_fiyat').innerText = "₺" + toplamKarliFiyat.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('net_kar').innerText = "₺" + netKar.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('birim_maliyet').innerText = "₺" + birimMaliyet.toLocaleString('tr-TR', {minimumFractionDigits: 4, maximumFractionDigits: 4});
            document.getElementById('karli_birim_fiyat').innerText = "₺" + karliBirimFiyat.toLocaleString('tr-TR', {minimumFractionDigits: 4, maximumFractionDigits: 4});
        }

        window.onload = hesapla;
    </script>
</body>
</html>