import streamlit as st

st.set_page_config(
    page_title="Merkez Bankası Kriz Yönetimi Oyunu",
    layout="wide",
)

# --------------------------------------------------
# Yardımcı fonksiyonlar
# --------------------------------------------------
def init_state() -> None:
    if "step" not in st.session_state:
        st.session_state.step = 1

    if "score" not in st.session_state:
        st.session_state.score = 0

    if "history" not in st.session_state:
        st.session_state.history = []

    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "Rezerv Değişimi (Milyar $)": -15,
            "CDS": 600,
            "Enflasyon (%)": 45,
            "Güven Düzeyi": 35,  # 0-100
            "Kur Baskısı": 80,   # 0-100
        }

    if "round1_choice" not in st.session_state:
        st.session_state.round1_choice = None

    if "round2_choice" not in st.session_state:
        st.session_state.round2_choice = None


def reset_game() -> None:
    for key in [
        "step",
        "score",
        "history",
        "metrics",
        "round1_choice",
        "round2_choice",
    ]:
        if key in st.session_state:
            del st.session_state[key]
    init_state()


def apply_round1(choice: str) -> dict:
    """
    1. tur kararının etkilerini uygular.
    """
    metrics = st.session_state.metrics.copy()
    result = {
        "title": "",
        "summary": "",
        "score_delta": 0,
        "effects": {},
    }

    if choice == "A":
        # Faizi düşür
        result["title"] = "Faiz indirildi"
        result["summary"] = (
            "Faiz indirimi, mevcut kırılgan ortamda piyasa tarafından "
            "gevşeme sinyali olarak algılandı. CDS yükseldi, kur baskısı arttı, "
            "güven zayıfladı."
        )
        result["score_delta"] = -25
        result["effects"] = {
            "CDS": +70,
            "Güven Düzeyi": -10,
            "Kur Baskısı": +10,
        }

    elif choice == "B":
        # Faizi artır
        result["title"] = "Faiz artırıldı"
        result["summary"] = (
            "Faiz artışı piyasalara sıkılaşma mesajı verdi. Kur baskısı azaldı, "
            "güven bir miktar toparlandı. Ancak tek başına CDS üzerinde sınırlı etki yaptı."
        )
        result["score_delta"] = 20
        result["effects"] = {
            "CDS": -20,
            "Güven Düzeyi": +8,
            "Kur Baskısı": -12,
        }

    elif choice == "C":
        # Rezerv sat
        result["title"] = "Rezerv satıldı"
        result["summary"] = (
            "Rezerv satışı kısa vadede kur baskısını hafifletti. Ancak rezerv kaybı "
            "sürdürülebilir bulunmadığı için güven sınırlı kaldı ve risk algısı tam düzelmedi."
        )
        result["score_delta"] = -5
        result["effects"] = {
            "Rezerv Değişimi (Milyar $)": -5,
            "CDS": +15,
            "Güven Düzeyi": -3,
            "Kur Baskısı": -8,
        }

    elif choice == "D":
        # Hiçbir şey yapma
        result["title"] = "Hiçbir adım atılmadı"
        result["summary"] = (
            "Politika tepkisi verilmemesi, belirsizliği artırdı. Piyasa bunu zayıf bir sinyal "
            "olarak gördü; CDS yükseldi ve güven geriledi."
        )
        result["score_delta"] = -20
        result["effects"] = {
            "CDS": +50,
            "Güven Düzeyi": -8,
            "Kur Baskısı": +8,
        }

    # Etkileri uygula
    for key, delta in result["effects"].items():
        metrics[key] += delta

    # Sınırlandırmalar
    metrics["Güven Düzeyi"] = max(0, min(100, metrics["Güven Düzeyi"]))
    metrics["Kur Baskısı"] = max(0, min(100, metrics["Kur Baskısı"]))

    st.session_state.metrics = metrics
    st.session_state.score += result["score_delta"]
    st.session_state.history.append(
        {
            "tur": 1,
            "karar": choice,
            "başlık": result["title"],
            "özet": result["summary"],
            "puan": result["score_delta"],
            "metrikler": metrics.copy(),
        }
    )
    return result


def apply_round2(choice: str) -> dict:
    """
    2. tur kombinasyon kararının etkilerini uygular.
    """
    metrics = st.session_state.metrics.copy()
    result = {
        "title": "",
        "summary": "",
        "score_delta": 0,
        "effects": {},
    }

    if choice == "A":
        # Faiz artır + iletişim güçlendir
        result["title"] = "Faiz artırıldı ve iletişim güçlendirildi"
        result["summary"] = (
            "Bu kombinasyon en güçlü politika tepkisi oldu. Sıkılaşma kararı, "
            "şeffaf iletişimle desteklendiği için güven arttı, CDS geriledi, kur baskısı azaldı."
        )
        result["score_delta"] = 35
        result["effects"] = {
            "CDS": -60,
            "Güven Düzeyi": +18,
            "Kur Baskısı": -18,
        }

    elif choice == "B":
        # Faiz indir + rezerv sat
        result["title"] = "Faiz indirildi, rezerv satıldı"
        result["summary"] = (
            "Bu politika bileşimi piyasa açısından çelişkili ve zayıf bulundu. "
            "Rezerv satışı geçici rahatlama sağlasa da faiz indirimi risk algısını bozdu. "
            "CDS yükseldi, güven geriledi."
        )
        result["score_delta"] = -35
        result["effects"] = {
            "Rezerv Değişimi (Milyar $)": -8,
            "CDS": +80,
            "Güven Düzeyi": -15,
            "Kur Baskısı": +12,
        }

    elif choice == "C":
        # Sadece rezerv sat
        result["title"] = "Sadece rezerv satıldı"
        result["summary"] = (
            "Rezerv satışı kısa süreli dengeleme sağladı; ancak yapısal güveni güçlendirmedi. "
            "Bu nedenle CDS üzerinde kalıcı iyileşme oluşmadı."
        )
        result["score_delta"] = -10
        result["effects"] = {
            "Rezerv Değişimi (Milyar $)": -7,
            "CDS": +10,
            "Güven Düzeyi": -4,
            "Kur Baskısı": -10,
        }

    elif choice == "D":
        # Faiz artır ama iletişim zayıf
        result["title"] = "Faiz artırıldı ama iletişim zayıf kaldı"
        result["summary"] = (
            "Teknik olarak doğru yönde bir adım atıldı; ancak iletişim eksikliği nedeniyle "
            "politikanın güven etkisi sınırlı kaldı. CDS kısmen geriledi fakat beklenen kadar düşmedi."
        )
        result["score_delta"] = 10
        result["effects"] = {
            "CDS": -20,
            "Güven Düzeyi": +4,
            "Kur Baskısı": -8,
        }

    for key, delta in result["effects"].items():
        metrics[key] += delta

    metrics["Güven Düzeyi"] = max(0, min(100, metrics["Güven Düzeyi"]))
    metrics["Kur Baskısı"] = max(0, min(100, metrics["Kur Baskısı"]))

    st.session_state.metrics = metrics
    st.session_state.score += result["score_delta"]
    st.session_state.history.append(
        {
            "tur": 2,
            "karar": choice,
            "başlık": result["title"],
            "özet": result["summary"],
            "puan": result["score_delta"],
            "metrikler": metrics.copy(),
        }
    )
    return result


def score_comment(score: int) -> str:
    if score >= 45:
        return "Çok başarılı politika yönetimi. Araçları birlikte kullanarak güveni ve istikrarı güçlendirdiniz."
    if score >= 20:
        return "Genel olarak doğru yönde adımlar attınız; ancak bazı kararlar daha güçlü iletişimle desteklenebilirdi."
    if score >= 0:
        return "Kısmi başarı sağlandı. Bazı kararlar kısa vadeli rahatlama yarattı ama yapısal güven üretmedi."
    return "Politika bileşimi zayıf kaldı. Piyasa güveni ve risk primi üzerindeki etkiler yeterince yönetilemedi."


def show_metrics(metrics: dict) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Rezerv Değişimi", f'{metrics["Rezerv Değişimi (Milyar $)"]} milyar $')
    col2.metric("CDS", f'{metrics["CDS"]}')
    col3.metric("Enflasyon", f'%{metrics["Enflasyon (%)"]}')
    col4.metric("Güven", f'{metrics["Güven Düzeyi"]}/100')
    col5.metric("Kur Baskısı", f'{metrics["Kur Baskısı"]}/100')


# --------------------------------------------------
# Uygulama
# --------------------------------------------------
init_state()

st.title("🎮 Merkez Bankası Kriz Yönetimi Oyunu")
st.markdown(
    """
Bu oyunda rezerv düşüşü ve CDS artışı karşısında merkez bankasının nasıl tepki vereceğini seçiyorsunuz.
Amaç, **faiz, bilanço ve güven yönetimini birlikte düşünerek** en doğru politika bileşimini oluşturmaktır.
"""
)

with st.sidebar:
    st.header("Oyun Kontrolü")
    st.write(f"**Toplam Puan:** {st.session_state.score}")
    if st.button("🔄 Oyunu Sıfırla", use_container_width=True):
        reset_game()
        st.rerun()

st.subheader("Başlangıç Göstergeleri")
show_metrics(st.session_state.metrics)

st.divider()

# --------------------------------------------------
# TUR 1
# --------------------------------------------------
if st.session_state.step == 1:
    st.header("1. Tur: İlk Politika Tepkisi")
    st.markdown(
        """
**Senaryo:**
- TCMB rezervleri **15 milyar $ düştü**
- CDS **yükseldi**
- Enflasyon yüksek
- Piyasa güveni zayıf

**Siz merkez bankasısınız. İlk adımınız ne olur?**
"""
    )

    choice1 = st.radio(
        "Bir seçenek seçin:",
        options=[
            "A) Faizi düşür",
            "B) Faizi artır",
            "C) Rezerv sat",
            "D) Hiçbir şey yapma",
        ],
        index=None,
    )

    if st.button("1. Tur Kararını Uygula", type="primary", use_container_width=True):
        if choice1 is None:
            st.warning("Lütfen bir seçenek seçin.")
        else:
            selected = choice1[0]  # A/B/C/D
            st.session_state.round1_choice = selected
            result = apply_round1(selected)

            st.success(f"Karar uygulandı: {result['title']}")
            st.write(result["summary"])
            st.write(f"**Puan etkisi:** {result['score_delta']}")

            st.subheader("1. Tur Sonrası Göstergeler")
            show_metrics(st.session_state.metrics)

            st.session_state.step = 2
            st.rerun()

# --------------------------------------------------
# TUR 2
# --------------------------------------------------
elif st.session_state.step == 2:
    st.header("2. Tur: Kombinasyon Politikası")
    st.markdown(
        """
İlk kararın ardından piyasa hâlâ kırılgan. Şimdi daha kapsamlı bir politika bileşimi seçmeniz gerekiyor.

**Soru:** Tek bir araç yeterli mi, yoksa güven ve iletişim de sürece katılmalı mı?
"""
    )

    if st.session_state.history:
        st.info(
            f"1. Tur kararınız: **{st.session_state.history[0]['başlık']}** "
            f"(Puan: {st.session_state.history[0]['puan']})"
        )

    show_metrics(st.session_state.metrics)

    choice2 = st.radio(
        "Kombinasyon politikasını seçin:",
        options=[
            "A) Faiz artır + iletişimi güçlendir",
            "B) Faiz indir + rezerv sat",
            "C) Sadece rezerv sat",
            "D) Faiz artır ama iletişimi zayıf bırak",
        ],
        index=None,
    )

    if st.button("2. Tur Kararını Uygula", type="primary", use_container_width=True):
        if choice2 is None:
            st.warning("Lütfen bir seçenek seçin.")
        else:
            selected = choice2[0]
            st.session_state.round2_choice = selected
            result = apply_round2(selected)

            st.success(f"Karar uygulandı: {result['title']}")
            st.write(result["summary"])
            st.write(f"**Puan etkisi:** {result['score_delta']}")

            st.subheader("2. Tur Sonrası Göstergeler")
            show_metrics(st.session_state.metrics)

            st.session_state.step = 3
            st.rerun()

# --------------------------------------------------
# SONUÇ EKRANI
# --------------------------------------------------
elif st.session_state.step == 3:
    st.header("🏁 Oyun Sonucu")
    st.subheader(f"Toplam Puan: {st.session_state.score}")

    st.success(score_comment(st.session_state.score))

    st.subheader("Final Göstergeler")
    show_metrics(st.session_state.metrics)

    st.divider()

    st.subheader("Karar Geçmişi")
    for item in st.session_state.history:
        with st.expander(f"{item['tur']}. Tur — {item['başlık']}"):
            st.write(f"**Karar kodu:** {item['karar']}")
            st.write(item["özet"])
            st.write(f"**Puan etkisi:** {item['puan']}")
            st.write("**Tur sonu metrikleri:**")
            st.json(item["metrikler"])

    st.divider()

    st.subheader("Ekonomik Değerlendirme")
    st.markdown(
        """
- **Faiz artışı**, tek başına her zaman yeterli değildir.
- **Rezerv kullanımı**, kısa vadeli rahatlama sağlayabilir ama sürdürülebilir olmayabilir.
- **CDS**, piyasanın risk algısını yansıttığı için güven ve iletişim politikası kritik önemdedir.
- En etkili yaklaşım genellikle **faiz + likidite/bilanço yönetimi + güven artırıcı iletişim** bileşimidir.
"""
    )

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔁 Yeniden Oyna", use_container_width=True):
            reset_game()
            st.rerun()
    with col_b:
        st.button("✅ Oyun Tamamlandı", disabled=True, use_container_width=True)
