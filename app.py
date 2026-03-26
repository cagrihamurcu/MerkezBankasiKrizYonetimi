import time
from typing import Dict, Any, List

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Merkez Bankası Kriz Yönetimi Oyunu",
    layout="wide",
)

WAIT_SECONDS = 60

# --------------------------------------------------
# OYUN VERİLERİ
# --------------------------------------------------
ROUNDS: Dict[int, Dict[str, Any]] = {
    1: {
        "title": "Tur 1: Rezerv Kaybı ve CDS Şoku",
        "scenario": (
            "TCMB rezervleri 15 milyar $ düştü. CDS yükseldi. "
            "Piyasalarda güven zayıf, kur üzerinde baskı var."
        ),
        "options": {
            "A": "Faizi düşür",
            "B": "Faizi artır",
            "C": "Rezerv sat",
            "D": "Hiçbir şey yapma",
        },
        "results": {
            "A": {
                "title": "Faiz indirildi",
                "summary": (
                    "Piyasa bu kararı zamansız gevşeme olarak gördü. "
                    "CDS yükseldi, kur baskısı arttı, güven geriledi."
                ),
                "score": -25,
                "effects": {"CDS": 70, "Güven": -10, "Kur Baskısı": 12},
            },
            "B": {
                "title": "Faiz artırıldı",
                "summary": (
                    "Sıkılaşma mesajı verildi. Kur baskısı azaldı, güven toparlandı, "
                    "CDS'te kısmi düşüş görüldü."
                ),
                "score": 20,
                "effects": {"CDS": -20, "Güven": 8, "Kur Baskısı": -12, "Enflasyon": -1},
            },
            "C": {
                "title": "Rezerv satıldı",
                "summary": (
                    "Kısa vadede kur baskısı hafifledi; ancak rezerv kaybı nedeniyle "
                    "piyasa bunu kalıcı çözüm olarak görmedi."
                ),
                "score": -5,
                "effects": {"Rezerv": -5, "CDS": 15, "Güven": -3, "Kur Baskısı": -8},
            },
            "D": {
                "title": "Politika tepkisi verilmedi",
                "summary": (
                    "Hareketsizlik belirsizliği artırdı. Piyasa bunu zayıf yönetim işareti olarak değerlendirdi."
                ),
                "score": -20,
                "effects": {"CDS": 50, "Güven": -8, "Kur Baskısı": 8},
            },
        },
    },
    2: {
        "title": "Tur 2: Kur Şoku Derinleşiyor",
        "scenario": (
            "Kur hızlı yükseliyor. İthalat maliyetleri artıyor. "
            "Enflasyon beklentileri bozuluyor."
        ),
        "options": {
            "A": "Faiz artır + iletişimi güçlendir",
            "B": "Faiz indir + rezerv sat",
            "C": "Sadece rezerv sat",
            "D": "Faiz artır ama iletişimi zayıf bırak",
        },
        "results": {
            "A": {
                "title": "Faiz artırıldı, iletişim güçlendirildi",
                "summary": (
                    "Sıkılaşma ve güçlü iletişim birlikte kullanıldı. "
                    "Güven arttı, CDS geriledi, kur baskısı azaldı."
                ),
                "score": 35,
                "effects": {"CDS": -60, "Güven": 18, "Kur Baskısı": -18, "Enflasyon": -2},
            },
            "B": {
                "title": "Faiz indirildi, rezerv satıldı",
                "summary": (
                    "Piyasa bu yaklaşımı çelişkili buldu. Rezerv satışı kısa süreli etki yaratsa da "
                    "faiz indirimi risk algısını bozdu."
                ),
                "score": -35,
                "effects": {"Rezerv": -8, "CDS": 80, "Güven": -15, "Kur Baskısı": 12},
            },
            "C": {
                "title": "Sadece rezerv satıldı",
                "summary": (
                    "Geçici rahatlama sağlandı; ancak yapısal güven oluşturulamadı."
                ),
                "score": -10,
                "effects": {"Rezerv": -7, "CDS": 10, "Güven": -4, "Kur Baskısı": -10},
            },
            "D": {
                "title": "Faiz artırıldı ama iletişim zayıf kaldı",
                "summary": (
                    "Teknik olarak doğru yönde adım atıldı; ancak güven etkisi sınırlı kaldı."
                ),
                "score": 10,
                "effects": {"CDS": -20, "Güven": 4, "Kur Baskısı": -8, "Enflasyon": -1},
            },
        },
    },
    3: {
        "title": "Tur 3: Enflasyon Beklentileri Bozuluyor",
        "scenario": (
            "Piyasa gelecek dönemde daha yüksek enflasyon bekliyor. "
            "Kredi büyümesi hâlâ güçlü."
        ),
        "options": {
            "A": "Zorunlu karşılık oranını artır",
            "B": "Faizi indirerek büyümeyi destekle",
            "C": "Likiditeyi artır",
            "D": "Sorunu görmezden gel",
        },
        "results": {
            "A": {
                "title": "Zorunlu karşılık artırıldı",
                "summary": (
                    "Kredi verme kapasitesi sınırlandı. Kredi genişlemesi yavaşladı, "
                    "enflasyon baskısı azaldı."
                ),
                "score": 20,
                "effects": {"Enflasyon": -2, "Güven": 5, "Kur Baskısı": -4},
            },
            "B": {
                "title": "Faiz indirildi",
                "summary": (
                    "Piyasa bunu zamansız gevşeme olarak gördü. "
                    "Enflasyon beklentileri daha da bozuldu."
                ),
                "score": -20,
                "effects": {"Enflasyon": 3, "CDS": 25, "Güven": -8, "Kur Baskısı": 6},
            },
            "C": {
                "title": "Likidite artırıldı",
                "summary": (
                    "Sisteme likidite verildi; ancak bu karar enflasyonist baskıları güçlendirdi."
                ),
                "score": -15,
                "effects": {"Enflasyon": 2, "CDS": 15, "Güven": -5},
            },
            "D": {
                "title": "Tepki verilmedi",
                "summary": (
                    "Beklentiler bozulurken hareketsiz kalınması güven kaybına yol açtı."
                ),
                "score": -18,
                "effects": {"Enflasyon": 2, "CDS": 20, "Güven": -6, "Kur Baskısı": 5},
            },
        },
    },
    4: {
        "title": "Tur 4: Büyüme Yavaşlıyor",
        "scenario": (
            "Sıkılaşma sonrası büyüme ivme kaybetti. İş dünyası daha düşük finansman maliyeti talep ediyor."
        ),
        "options": {
            "A": "Faizi sert artır",
            "B": "Faizi dikkatli indir + iletişimi güçlendir",
            "C": "Rezerv sat",
            "D": "CDS'i yok say, sadece büyümeye odaklan",
        },
        "results": {
            "A": {
                "title": "Faiz sert artırıldı",
                "summary": (
                    "Enflasyon açısından güçlü sinyal verildi; ancak büyüme üzerindeki baskı arttı."
                ),
                "score": 5,
                "effects": {"CDS": -10, "Güven": 2, "Enflasyon": -2, "Büyüme": -2},
            },
            "B": {
                "title": "Faiz dikkatli indirildi, iletişim güçlendirildi",
                "summary": (
                    "Temkinli gevşeme ile büyüme desteklenmeye çalışıldı. "
                    "Güven kaybı sınırlı tutuldu."
                ),
                "score": 18,
                "effects": {"Büyüme": 3, "Güven": 8, "CDS": -5, "Kur Baskısı": 2},
            },
            "C": {
                "title": "Rezerv satıldı",
                "summary": (
                    "Rezerv satışı büyüme sorununu çözmedi, kırılganlığı artırdı."
                ),
                "score": -12,
                "effects": {"Rezerv": -6, "CDS": 10, "Güven": -4},
            },
            "D": {
                "title": "Risk göz ardı edildi",
                "summary": (
                    "Piyasa risk algısı dikkate alınmadı. Güven bozuldu, finansal koşullar kötüleşti."
                ),
                "score": -20,
                "effects": {"CDS": 30, "Güven": -10, "Kur Baskısı": 6, "Büyüme": 1},
            },
        },
    },
    5: {
        "title": "Tur 5: Küresel Finansal Şok",
        "scenario": (
            "Küresel risk iştahı düştü. Sermaye çıkışları hızlandı. "
            "İçeride kırılganlık sürüyor."
        ),
        "options": {
            "A": "Faiz artır + likiditeyi sıkılaştır + güçlü iletişim",
            "B": "Faiz indir + büyüme vurgusu yap",
            "C": "Sadece rezerv kullan",
            "D": "Bekle-gör politikası uygula",
        },
        "results": {
            "A": {
                "title": "Kapsamlı sıkılaşma ve güçlü iletişim",
                "summary": (
                    "Çok araçlı politika yaklaşımı kullanıldı. Güven güçlendi, CDS geriledi, kur baskısı azaldı."
                ),
                "score": 40,
                "effects": {"CDS": -50, "Güven": 20, "Kur Baskısı": -20, "Enflasyon": -1},
            },
            "B": {
                "title": "Faiz indirildi, büyüme öne çıkarıldı",
                "summary": (
                    "Küresel şok ortamında bu karar riskli bulundu. CDS sıçradı, güven sert düştü."
                ),
                "score": -30,
                "effects": {"CDS": 60, "Güven": -15, "Kur Baskısı": 15, "Büyüme": 1},
            },
            "C": {
                "title": "Sadece rezerv kullanıldı",
                "summary": (
                    "Kısa vadeli savunma sağlandı; ancak rezerv kaybı nedeniyle sürdürülebilirlik sorgulandı."
                ),
                "score": -10,
                "effects": {"Rezerv": -10, "CDS": 15, "Güven": -5, "Kur Baskısı": -6},
            },
            "D": {
                "title": "Bekle-gör yaklaşımı",
                "summary": (
                    "Pasif kalınması piyasa güvenini zayıflattı. Risk primi yükseldi."
                ),
                "score": -18,
                "effects": {"CDS": 25, "Güven": -8, "Kur Baskısı": 8},
            },
        },
    },
}


# --------------------------------------------------
# STATE
# --------------------------------------------------
def init_state() -> None:
    if "round" not in st.session_state:
        st.session_state.round = 1
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "history" not in st.session_state:
        st.session_state.history = []
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "Rezerv": 100,
            "CDS": 600,
            "Enflasyon": 45,
            "Güven": 35,
            "Kur Baskısı": 80,
            "Büyüme": 2,
        }
    if "waiting" not in st.session_state:
        st.session_state.waiting = False
    if "wait_until" not in st.session_state:
        st.session_state.wait_until = None
    if "pending_result" not in st.session_state:
        st.session_state.pending_result = None
    if "last_result" not in st.session_state:
        st.session_state.last_result = None


def reset_game() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def clamp_metrics() -> None:
    m = st.session_state.metrics
    m["Güven"] = max(0, min(100, m["Güven"]))
    m["Kur Baskısı"] = max(0, min(100, m["Kur Baskısı"]))
    m["CDS"] = max(100, m["CDS"])
    m["Rezerv"] = max(0, m["Rezerv"])


# --------------------------------------------------
# GAME LOGIC
# --------------------------------------------------
def queue_choice(round_no: int, choice_key: str) -> None:
    result = ROUNDS[round_no]["results"][choice_key]
    st.session_state.pending_result = {
        "Tur": round_no,
        "Karar": choice_key,
        "Başlık": result["title"],
        "Açıklama": result["summary"],
        "Puan Etkisi": result["score"],
        "Etkiler": result["effects"],
        "Önce": st.session_state.metrics.copy(),
    }
    st.session_state.waiting = True
    st.session_state.wait_until = time.time() + WAIT_SECONDS


def finalize_pending_result() -> None:
    item = st.session_state.pending_result
    if not item:
        return

    metrics = st.session_state.metrics.copy()
    for key, delta in item["Etkiler"].items():
        metrics[key] += delta

    st.session_state.metrics = metrics
    clamp_metrics()
    st.session_state.score += item["Puan Etkisi"]

    item["Sonra"] = st.session_state.metrics.copy()
    st.session_state.history.append(item)
    st.session_state.last_result = item
    st.session_state.pending_result = None
    st.session_state.waiting = False
    st.session_state.wait_until = None

    # 5. turdan sonra doğrudan bitir
    if item["Tur"] < 5:
        st.session_state.round = item["Tur"] + 1
    else:
        st.session_state.round = 6


def score_comment(score: int) -> str:
    if score >= 70:
        return "Çok güçlü performans. Politika araçlarını birlikte kullanarak güveni ve istikrarı başarıyla yönettiniz."
    if score >= 35:
        return "İyi performans. Çoğu turda doğru yönde karar verdiniz, ancak bazı adımlar daha güçlü iletişimle desteklenebilirdi."
    if score >= 0:
        return "Orta düzey performans. Bazı kararlar kısa vadeli rahatlama sağladı ama yapısal güven üretmekte yetersiz kaldı."
    return "Zayıf performans. Risk primi, güven ve likidite yönetimi arasında tutarlı bir politika bileşimi kurulamadı."


# --------------------------------------------------
# UI HELPERS
# --------------------------------------------------
def show_metrics() -> None:
    m = st.session_state.metrics
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)

    c1.metric("Rezerv", f"{m['Rezerv']} milyar $")
    c2.metric("CDS", f"{m['CDS']}")
    c3.metric("Enflasyon", f"%{m['Enflasyon']}")
    c4.metric("Güven", f"{m['Güven']}/100")
    c5.metric("Kur Baskısı", f"{m['Kur Baskısı']}/100")
    c6.metric("Büyüme", f"%{m['Büyüme']}")


def build_history_df() -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    # başlangıç noktası
    initial_metrics = {
        "Tur": 0,
        "Rezerv": 100,
        "CDS": 600,
        "Enflasyon": 45,
        "Güven": 35,
        "Kur Baskısı": 80,
        "Büyüme": 2,
        "Toplam Puan": 0,
    }
    rows.append(initial_metrics)

    total_score = 0
    for item in st.session_state.history:
        total_score += item["Puan Etkisi"]
        rows.append(
            {
                "Tur": item["Tur"],
                "Rezerv": item["Sonra"]["Rezerv"],
                "CDS": item["Sonra"]["CDS"],
                "Enflasyon": item["Sonra"]["Enflasyon"],
                "Güven": item["Sonra"]["Güven"],
                "Kur Baskısı": item["Sonra"]["Kur Baskısı"],
                "Büyüme": item["Sonra"]["Büyüme"],
                "Toplam Puan": total_score,
            }
        )

    return pd.DataFrame(rows)


def plot_metrics() -> None:
    df = build_history_df()

    fig1, ax1 = plt.subplots(figsize=(8, 4))
    ax1.plot(df["Tur"], df["CDS"], marker="o", label="CDS")
    ax1.plot(df["Tur"], df["Rezerv"], marker="o", label="Rezerv")
    ax1.set_title("CDS ve Rezerv Gelişimi")
    ax1.set_xlabel("Tur")
    ax1.set_ylabel("Seviye")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.plot(df["Tur"], df["Enflasyon"], marker="o", label="Enflasyon")
    ax2.plot(df["Tur"], df["Güven"], marker="o", label="Güven")
    ax2.plot(df["Tur"], df["Kur Baskısı"], marker="o", label="Kur Baskısı")
    ax2.set_title("Enflasyon, Güven ve Kur Baskısı")
    ax2.set_xlabel("Tur")
    ax2.set_ylabel("Seviye")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    st.pyplot(fig2)


def show_last_result_box() -> None:
    item = st.session_state.last_result
    if not item:
        return

    st.success(f"Karar uygulandı: {item['Başlık']}")
    st.write(item["Açıklama"])
    st.write(f"**Puan etkisi:** {item['Puan Etkisi']}")

    before = item["Önce"]
    after = item["Sonra"]

    deltas = []
    for key in ["Rezerv", "CDS", "Enflasyon", "Güven", "Kur Baskısı", "Büyüme"]:
        change = after[key] - before[key]
        if change != 0:
            sign = "+" if change > 0 else ""
            deltas.append(f"- **{key}:** {sign}{change}")

    if deltas:
        st.markdown("**Piyasa yansımaları:**")
        st.markdown("\n".join(deltas))


# --------------------------------------------------
# APP
# --------------------------------------------------
init_state()

st.title("🎮 Merkez Bankası Kriz Yönetimi Oyunu")
st.markdown(
    """
Bu oyunda merkez bankasının rezerv kaybı, CDS artışı, enflasyon baskısı,
büyüme yavaşlaması ve küresel şoklar karşısında nasıl karar vereceğini seçiyorsunuz.

Amaç, **faiz, bilanço, likidite ve güven yönetimini birlikte düşünerek**
en doğru politika bileşimini oluşturmaktır.
"""
)

with st.sidebar:
    st.header("Oyun Paneli")
    current_round_display = min(st.session_state.round, 5)
    st.write(f"**Mevcut Tur:** {current_round_display}/5")
    st.write(f"**Toplam Puan:** {st.session_state.score}")
    if st.button("🔄 Oyunu Sıfırla", use_container_width=True):
        reset_game()
        st.rerun()

st.subheader("Güncel Göstergeler")
show_metrics()

st.divider()
st.subheader("Grafikler")
plot_metrics()
st.caption("Grafikler yalnızca piyasa etkileri oluştuktan sonra güncellenir.")

st.divider()

# --------------------------------------------------
# WAITING PHASE
# --------------------------------------------------
if st.session_state.waiting and st.session_state.pending_result is not None:
    pending = st.session_state.pending_result
    st.info(f"Seçilen karar: **{pending['Başlık']}**")
    st.write(pending["Açıklama"])
    st.warning("Kararınızın piyasalarda etkilerinin görülmesi için lütfen bekleyiniz.")

    remaining = int(st.session_state.wait_until - time.time())
    progress_text = st.empty()
    progress_bar = st.progress(0)

    while remaining > 0:
        elapsed = WAIT_SECONDS - remaining
        progress = int((elapsed / WAIT_SECONDS) * 100)
        progress_bar.progress(progress)
        progress_text.markdown(f"### Piyasa yansımaları için kalan süre: **{remaining} saniye**")
        time.sleep(1)
        remaining = int(st.session_state.wait_until - time.time())

    progress_bar.progress(100)
    progress_text.markdown("### Süre doldu. Piyasa etkileri şimdi işlendi.")
    finalize_pending_result()
    st.rerun()

# --------------------------------------------------
# ACTIVE GAME
# --------------------------------------------------
elif st.session_state.round <= 5:
    if st.session_state.last_result:
        show_last_result_box()
        st.divider()

    current_round = st.session_state.round
    round_data = ROUNDS[current_round]

    st.header(round_data["title"])
    st.info(round_data["scenario"])

    option_texts = [f"{k}) {v}" for k, v in round_data["options"].items()]
    selected_option = st.radio(
        "Kararınızı seçin:",
        options=option_texts,
        index=None,
        key=f"round_{current_round}_choice",
    )

    if st.button("Kararı Uygula", type="primary", use_container_width=True):
        if selected_option is None:
            st.warning("Lütfen bir karar seçin.")
        else:
            choice_key = selected_option[0]
            queue_choice(current_round, choice_key)
            st.rerun()

# --------------------------------------------------
# GAME OVER
# --------------------------------------------------
else:
    if st.session_state.last_result:
        show_last_result_box()

    st.header("🏁 Oyun Tamamlandı")
    st.subheader(f"Toplam Puan: {st.session_state.score}")
    st.success(score_comment(st.session_state.score))

    st.subheader("Final Göstergeler")
    show_metrics()

    st.divider()
    st.subheader("Final Grafikler")
    plot_metrics()

    st.divider()
    st.subheader("Karar Geçmişi")
    for item in st.session_state.history:
        with st.expander(f"Tur {item['Tur']} — {item['Başlık']}"):
            st.write(f"**Karar kodu:** {item['Karar']}")
            st.write(item["Açıklama"])
            st.write(f"**Puan etkisi:** {item['Puan Etkisi']}")
            comparison_df = pd.DataFrame(
                {
                    "Önce": item["Önce"],
                    "Sonra": item["Sonra"],
                }
            )
            st.dataframe(comparison_df)

    st.divider()
    st.subheader("Genel Değerlendirme")
    st.markdown(
        """
- **Faiz artışı**, özellikle güven veren iletişimle desteklendiğinde daha etkili olur.
- **Rezerv kullanımı**, kısa vadeli rahatlama sağlayabilir ancak sürekli kullanımı sürdürülebilir değildir.
- **CDS**, piyasanın risk algısını yansıttığı için sadece teknik araçlar değil, güven ve beklenti yönetimi de kritik önemdedir.
- En etkili yaklaşım çoğu zaman **faiz + bilanço/likidite yönetimi + iletişim/güven politikası** bileşimidir.
"""
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Yeniden Oyna", use_container_width=True):
            reset_game()
            st.rerun()
    with col2:
        st.button("✅ Oyun Bitti", disabled=True, use_container_width=True)
