import streamlit as st

def render_teklif_formu():
    st.subheader("📋 Matbaa Teklif & Maliyet Hesaplama Formu")
    st.markdown("---")

    # 1. Firma ve Ürün Bilgileri
    col1, col2 = st.columns(2)
    with col1:
        firma_adi = st.text_input("Firma Adı", "Erhan Ticaret", key="form_firma")
    with col2:
        urun_adi = st.text_input("Ürün Adı", "Lüks Ambalaj Kutusu", key="form_urun_adi")

    # 2. Ürün Tipi Listesi
    urun_tipleri = [
        "Föy", 
        "Tek Kırımlı Broşür", 
        "İki Kırımlı Broşür", 
        "Kartonet", 
        "Kutu", 
        "Sıvamalı Kutu", 
        "Etiket", 
        "Prospektüs"
    ]
    urun_tipi = st.selectbox("Ürün Tipi", urun_tipleri, key="form_urun_tipi")

    st.markdown("---")

    # 3. Ürün Adedi A, B, C
    st.markdown("##### 🔢 Ürün Adedi (Tiraj Seçenekleri)")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        adet_a = st.number_input("Adet A", value=1000, step=500, key="form_adet_a")
    with col_b:
        adet_b = st.number_input("Adet B", value=3000, step=500, key="form_adet_b")
    with col_c:
        adet_c = st.number_input("Adet C", value=5000, step=500, key="form_adet_c")

    st.markdown("---")

    # 4. Kağıt Gramajı ve Cinsi (Ana ve Alternatif B)
    kagit_listesi = ["Amerikan Bristol", "Krome Karton", "Kuşe Kağıt", "1. Hamur Kağıt"]
    gramaj_listesi = [200, 250, 300, 350, 400]

    st.markdown("##### 📄 Kağıt ve Malzeme Seçimi")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        st.markdown("**Kağıt Cinsi ve Gramajı (Ana)**")
        kagit_a = st.selectbox("Kağıt Cinsi A", kagit_listesi, key="form_kagit_a")
        gramaj_a = st.selectbox("Gramaj A", gramaj_listesi, index=2, key="form_gramaj_a")
    with col_k2:
        st.markdown("**Kağıt Cinsi ve Gramajı Alternatif B**")
        kagit_b = st.selectbox("Kağıt Cinsi B", kagit_listesi, key="form_kagit_b")
        gramaj_b = st.selectbox("Gramaj B", gramaj_listesi, index=2, key="form_gramaj_b")

    st.markdown("---")

    # 5. Baskı CMYK ve Pantone Renk Sayısı
    col_bc1, col_bc2 = st.columns(2)
    with col_bc1:
        baski_cmyk = st.selectbox("Baskı CMYK", ["Tek Yüz", "Çift Yüz", "CMYK Baskı Yok"], key="form_baski_cmyk")
    with col_bc2:
        pantone_sayisi = st.selectbox("Baskı Pantone Renk Sayısı", [
            "Yok",
            "1 renk zemin", "2 renk zemin", "3 renk zemin", "4 renk zemin", 
            "1 renk lokal", "2 renk lokal", "3 renk lokal", "4 renk lokal"
        ], key="form_pantone_sayisi")

    st.markdown("---")

    # 6. Ebat Bilgileri (En x Boy x Yükseklik)
    st.markdown("##### 📐 Bitmiş Ebat (mm)")
    col_e1, col_e2, col_e3 = st.columns(3)
    with col_e1:
        ebat_en = st.number_input("En (mm)", value=200, key="form_ebat_en")
    with col_e2:
        ebat_boy = st.number_input("Boy (mm)", value=150, key="form_ebat_boy")
    with col_e3:
        ebat_yukseklik = st.number_input("Yükseklik (mm)", value=50, key="form_ebat_yukseklik")

    st.markdown("---")

    # 7. Laminasyon ve Özel Baskılar
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        laminasyon = st.selectbox("Laminasyon", ["Parlak Selofan", "Mat Selofan", "Dispresiyon Lak", "Yok"], key="form_laminasyon")
        ozel_baski_1 = st.selectbox("Özel Baskılar 1", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="form_ozel_baski_1")
    with col_l2:
        ozel_baski_2 = st.selectbox("Özel Baskılar 2", ["Yok", "Lokal Lak", "Kabartma Lak", "Gofre", "Varak Yaldız"], key="form_ozel_baski_2")
        baski_sonrasi = st.selectbox("Baskı Sonrası", ["Düz Kesim", "Özel Kesim", "Kutu Kesim + Yapıştırma"], key="form_baski_sonrasi")

    st.markdown("---")

    # 8. Özel İstekler
    ozel_istekler = st.text_area("Özel İstekler", placeholder="Müşteriye özel ek talepler...", key="form_ozel_istekler")

if __name__ == "__main__":
    render_teklif_formu()