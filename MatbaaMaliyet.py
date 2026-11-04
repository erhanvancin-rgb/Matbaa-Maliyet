import math

def hesapla_montaj_ve_ebat(net_adet, en_mm, boy_mm):
    """
    Föy ürünler için adet kademelerine ve tabaka ebatlarına göre 
    montaj yerleşimi, fire ve tabaka adeti hesaplama motoru.
    """
    tabakalar = [
        {"kod": "Alternatif A (Düşük Tiraj)", "tab_en": 32, "tab_boy": 45, "makine": "35x50 Ofset"},
        {"kod": "Alternatif B (Orta Tiraj)", "tab_en": 45, "tab_boy": 64, "makine": "50x70 Ofset"},
        {"kod": "Alternatif C (Yüksek Tiraj)", "tab_en": 64, "tab_boy": 90, "makine": "70x100 Ofset"}
    ]
    
    alternatifler = []
    
    # Ürün ölçülerini cm'ye çeviriyoruz
    u_en = en_mm / 10.0
    u_boy = boy_mm / 10.0
    
    for tab in tabakalar:
        t_en = tab["tab_en"]
        t_boy = tab["tab_boy"]
        
        # Bıçak ve kenar boşlukları hesaba katılarak tabakaya sığma (fit) hesaplaması
        fit_h1 = math.floor((t_en - 1.0) / (u_en + 0.5)) * math.floor((t_boy - 1.0) / (u_boy + 0.5))
        fit_h2 = math.floor((t_en - 1.0) / (u_boy + 0.5)) * math.floor((t_boy - 1.0) / (u_en + 0.5))
        montaj_adedi = max(1, fit_h1, fit_h2)
        
        # Adete göre fire oranı kademeleri
        if net_adet <= 1500:
            fire_pct = 10.0
        elif net_adet <= 3000:
            fire_pct = 7.0
        else:
            fire_pct = 5.0
            
        brut_adet = int(math.ceil(net_adet * (1 + fire_pct / 100.0)))
        tabaka_adeti = math.ceil(brut_adet / montaj_adedi)
        if tabaka_adeti < 100:
            tabaka_adeti = 100  # Minimum tabaka tabanı
            
        toplam_m2 = round(tabaka_adeti * (t_en / 100.0) * (t_boy / 100.0), 2)
        
        alternatifler.append({
            "Secenek": tab["kod"],
            "Makine Parkı": tab["makine"],
            "Basılacak Ebat": f"{t_en}x{t_boy} cm",
            "1 Tabakadaki İmalat (Montaj)": f"{montaj_adedi} adet",
            "Fire Oranı": f"%{fire_pct:.1f}",
            "Brüt Adet": f"{brut_adet:,} adet",
            "Gereken Tabaka Adedi": f"{tabaka_adeti:,} tabaka",
            "Toplam Metrekare": f"{toplam_m2:,.2f} m²"
        })
        
    return alternatifler

# --- TEST ÇALIŞTIRMASI (Örn: A4 Broşür / 1.000 Adet) ---
sonuc_listesi = hesapla_montaj_ve_ebat(net_adet=1000, en_mm=210, boy_mm=297)

for alt in sonuc_listesi:
    print(f"--- {alt['Secenek']} ---")
    for k, v in alt.items():
        if k != 'Secenek':
            print(f"  {k}: {v}")
    print()
