<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Matbaam - Ambalaj ve Matbaa Maliyet Hesaplama</title>
    <script src="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1f2c; color: #e2e8f0; }
        .top-nav { background-color: #242b3b; border-bottom: 1px solid #2d3748; }
        .card-box { background-color: #242b3b; border: 1px solid #2d3748; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
        .step-title { color: #f59e0b; font-weight: bold; font-size: 15px; display: flex; align-items: center; gap: 8px; margin-bottom: 15px; border-bottom: 1px solid #2d3748; padding-bottom: 8px; }
        .step-number { background-color: #f59e0b; color: #1a1f2c; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: bold; }
        .type-card { background-color: #1a1f2c; border: 2px solid #2d3748; border-radius: 8px; padding: 15px; text-align: center; cursor: pointer; transition: all 0.2s; }
        .type-card:hover, .type-card.active { border-color: #f59e0b; background-color: #242b3b; }
        .material-card { background-color: #1a1f2c; border: 2px solid #2d3748; border-radius: 8px; padding: 12px; cursor: pointer; transition: all 0.2s; }
        .material-card:hover, .material-card.active { border-color: #f59e0b; background-color: #242b3b; }
        input, select { background-color: #1a1f2c !important; color: #ffffff !important; border: 1px solid #3f4656 !important; padding: 8px 12px; border-radius: 6px; width: 100%; font-size: 14px; }
        input:focus, select:focus { outline: none; border-color: #f59e0b !important; }
        .summary-card { background-color: #242b3b; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; }
        .btn-primary { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #1a1f2c; font-weight: bold; padding: 12px; border-radius: 6px; width: 100%; transition: opacity 0.2s; text-align: center; display: block; cursor: pointer; }
        .btn-primary:hover { opacity: 0.9; }
    </style>
</head>
<body class="pb-12">

    <!-- Üst Menü -->
    <div class="top-nav px-8 py-4 flex justify-between items-center">
        <div class="flex items-center space-x-3">
            <div class="bg-gradient-to-r from-yellow-500 to-yellow-600 text-gray-900 font-extrabold px-3 py-1.5 rounded-lg text-lg">M</div>
            <span class="text-xl font-bold tracking-wider text-white">MATBAAM</span>
        </div>
        <div class="hidden md:flex space-x-8 text-sm font-medium text-gray-300">
            <a href="#" class="hover:text-yellow-500">Ana Sayfa</a>
            <a href="#" class="text-yellow-500 font-bold">Hemen Hesapla</a>
            <a href="#" class="hover:text-yellow-500">Siparişlerim</a>
            <a href="#" class="hover:text-yellow-500">Parkurumuz</a>
            <a href="#" class="hover:text-yellow-500">İletişim</a>
        </div>
        <div>
            <span class="bg-gray-800 text-gray-300 px-4 py-2 rounded-lg text-sm font-semibold border border-gray-700">Erhan Ticaret</span>
        </div>
    </div>

    <div class="max-w-7xl mx-auto px-6 mt-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        <!-- Sol Alan: Ürün ve Detaylar Formu -->
        <div class="lg:col-span-8 space-y-6">
            
            <!-- 1. Adım: Ürün Tipi -->
            <div class="card-box">
                <div class="step-title"><div class="step-number">1</div> Ürün Tipi</div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="type-card active" onclick="selectType(this, 'Kutu')">
                        <div class="text-yellow-500 font-bold mb-1">📦 Kutu</div>
                        <span class="text-xs text-gray-400">Özel Ambalaj</span>
                    </div>
                    <div class="type-card" onclick="selectType(this, 'Etiket')">
                        <div class="text-yellow-500 font-bold mb-1">🏷️ Etiket</div>
                        <span class="text-xs text-gray-400">Sallantı & Barkod</span>
                    </div>
                    <div class="type-card" onclick="selectType(this, 'Katalog')">
                        <div class="text-yellow-500 font-bold mb-1">📖 Katalog</div>
                        <span class="text-xs text-gray-400">Broşür & Set</span>
                    </div>
                    <div class="type-card" onclick="selectType(this, 'Poşet')">
                        <div class="text-yellow-500 font-bold mb-1">🛍️ Poşet</div>
                        <span class="text-xs text-gray-400">Karton Çanta</span>
                    </div>
                </div>
            </div>

            <!-- 2. Adım: Kutu Özellikleri -->
            <div class="card-box">
                <div class="step-title"><div class="step-number">2</div> Kutu Özellikleri</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Kutu Modeli</label>
                        <select id="kutu_modeli" onchange="hesapla()">
                            <option value="kilitli">Kilitli Dip Kutu</option>
                            <option value="omega">Omega Yapıştırma</option>
                            <option value="seperatörlü">Seperatörlü Kutu</option>
                            <option value="sivama">Sıvama Sert Kutu</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Ölçüler (En x Boy x Yükseklik)</label>
                        <div class="grid grid-cols-3 gap-1">
                            <input type="number" id="ebat_x" value="200" placeholder="En" oninput="hesapla()">
                            <input type="number" id="ebat_y" value="150" placeholder="Boy" oninput="hesapla()">
                            <input type="number" id="ebat_z" value="50" placeholder="Yükseklik" oninput="hesapla()">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-400 mb-1">Adet (Tiraj)</label>
                        <input type="number" id="adet" value="5000" step="500" oninput="hesapla()">
                    </div>
                </div>
            </div>

            <!-- 3. Adım: Malzeme Seçimi -->
            <div class="card-box">
                <div class="step-title"><div class="step-number">3</div> Malzeme Seçimi (Cins ve Gramaj)</div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="material-card active" onclick="selectMaterial(this, 'bristol')">
                        <div class="font-bold text-white text-sm">Amerikan Bristol</div>
                        <div class="text-xs text-yellow-500 mt-1">300 gr / 350 gr</div>
                    </div>
                    <div class="material-card" onclick="selectMaterial(this, 'krome')">
                        <div class="font-bold text-white text-sm">Krome Karton</div>
                        <div class="text-xs text-yellow-500 mt-1">300 gr / 350 gr</div>
                    </div>
                    <div class="material-card" onclick="selectMaterial(this, 'kuse')">
                        <div class="font-bold text-white text-sm">Kuşe Kağıt</div>
                        <div class="text-xs text-yellow-500 mt-1">250 gr / 300 gr</div>
                    </div>
                    <div class="material-card" onclick="selectMaterial(this, 'kraft')">
                        <div class="font-bold text-white text-sm">Kraft Karton</div>
                        <div class="text-xs text-yellow-500 mt-1">350 gr / 400 gr</div>
                    </div>
                </div>
            </div>

            <!-- 4. Adım: Baskı Detayları -->
            <div class="card-box">
                <div class="step-title"><div class="step-number">4</div> Baskı Detayları</div>
                <div class="grid grid-cols-1 md:grid
