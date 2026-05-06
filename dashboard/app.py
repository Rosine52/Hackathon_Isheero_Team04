# dashboard/app.py
# Dashboard Streamlit — Bénin Insights Challenge
# Lancement : streamlit run dashboard/app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="Bénin Insights 2025",
    page_icon="🌍",
    layout="wide",
)

# ── CHEMINS ───────────────────────────────────────────────────────────────────

ROOT_DIR    = Path(__file__).resolve().parent.parent
ASSETS_DIR  = Path(__file__).resolve().parent / "assets"
OUTPUTS_DIR = ROOT_DIR / "outputs"

# ── CONSTANTES ────────────────────────────────────────────────────────────────

LABELS_TON = {
    "tres_negatif": "Très négatif",
    "negatif":      "Négatif",
    "neutre":       "Neutre",
    "positif":      "Positif",
    "tres_positif": "Très positif",
}

LABELS_QUAD = {
    "cooperation_verbale":    "Coopération (verbale)",
    "cooperation_materielle": "Coopération (matérielle)",
    "conflit_verbal":         "Conflit (verbal)",
    "conflit_materiel":       "Conflit (matériel)",
}

LABELS_ZONES = {"nord": "Nord", "centre": "Centre", "sud": "Sud"}

NOMS_PAYS = {
    "NGA": "Nigeria",
    "AFR": "Afrique (générique)",
    "FRA": "France",
    "WAF": "Afrique de l'Ouest",
    "NER": "Niger",
    "BFA": "Burkina Faso",
    "TGO": "Togo",
    "GBR": "Royaume-Uni",
    "CHN": "Chine",
    "USA": "États-Unis",
    "SEN": "Sénégal",
    "GHA": "Ghana",
    "MDG": "Madagascar",
    "CIV": "Côte d'Ivoire",
    "CMR": "Cameroun",
    "RUS": "Russie",
    "EU":  "Union européenne",
    "EGY": "Égypte",
    "ZAF": "Afrique du Sud",
    "MAR": "Maroc",
}

DATE_MIN = date(2025, 1, 1)
DATE_MAX = date(2025, 12, 31)

MOIS_LABELS = {
    0:  "Toute l'année",
    1:  "Jan", 2:  "Fév", 3:  "Mar", 4:  "Avr",
    5:  "Mai", 6:  "Jun", 7:  "Jul", 8:  "Aoû",
    9:  "Sep", 10: "Oct", 11: "Nov", 12: "Déc",
}

# Dates anormales identifiées par approche multi-méthodes (Z-score + MAD + fenêtre glissante)
DATES_ANOMALIES = {
    "2025-01-10",
    "2025-04-17",
    "2025-12-07", "2025-12-08", "2025-12-09",
    "2025-12-10", "2025-12-11", "2025-12-12",
}

# Sources vérifiées :
# 2025-01-10 : Fête nationale du Vodoun (10 janv.) + Vodun Days à Ouidah
#              — AFP, Global Voices, Africanews (janv. 2025)
# 2025-04-17 : Attaque JNIM/GSIM dans le parc W (Bénin / Niger / Burkina Faso)
#              — France 24 (23 avr. 2025), Euronews, OPEX360
# 2025-12-07+ : Tentative de coup d'État (Lt.-Col. Pascal Tigri contre Patrice Talon)
#              — France 24, Wikipedia FR/EN, Jeune Afrique, CBS News, Euronews
DESCRIPTIONS_ANOMALIES = {
    "2025-01-10": (
        "Fête nationale du Vodoun et Vodun Days à Ouidah — "
        "célébration de 3 jours, +300 000 visiteurs attendus"
    ),
    "2025-04-17": (
        "Attaque du JNIM (Al-Qaïda) dans le parc W — "
        "54 militaires béninois tués, plus grande perte de l'armée béninoise"
    ),
    "2025-12-07": (
        "Tentative de coup d'État — Lt.-Col. Pascal Tigri attaque "
        "la résidence de Talon, déjouée par la Garde républicaine"
    ),
    "2025-12-08": (
        "Lendemain du coup — putschistes en fuite, aide militaire du Nigeria, "
        "réactions France / CEDEAO / UA"
    ),
    "2025-12-09": (
        "Traque des mutins — déclarations CEDEAO, soutien français "
        "en renseignement confirmé par Macron"
    ),
    "2025-12-10": (
        "Couverture internationale soutenue — "
        "crise institutionnelle et sécuritaire au Bénin"
    ),
    "2025-12-11": (
        "Arrestations — premières personnes écrouées, "
        "Tigri toujours en cavale, enquête judiciaire ouverte"
    ),
    "2025-12-12": (
        "Bilan judiciaire — une trentaine de personnes écrouées "
        "(majorité militaires), mutins recherchés"
    ),
}

# Bounding box Bénin pour filtrage géographique (lat/lon)
BENIN_LAT = (5.5, 12.5)
BENIN_LON = (0.5,  3.8)
MAP_MAX_POINTS = 2000


# ── CHARGEMENT DES DONNÉES ────────────────────────────────────────────────────

@st.cache_data
def charger_donnees():
    chemin_parquet = ROOT_DIR / "data/processed/benin_enrichi.parquet"
    chemin_csv     = ROOT_DIR / "data/processed/benin_enrichi.csv"
    if chemin_parquet.exists():
        df = pd.read_parquet(chemin_parquet)
    elif chemin_csv.exists():
        df = pd.read_csv(chemin_csv)
    else:
        return None
    df["SQLDATE"] = pd.to_datetime(df["SQLDATE"], errors="coerce")
    return df


# ── EN-TÊTE ───────────────────────────────────────────────────────────────────

_armoiries = ASSETS_DIR / "armoiries_benin.png"
col_logo, col_titre = st.columns([1, 11])
with col_logo:
    if _armoiries.exists():
        try:
            st.image(str(_armoiries), width=72)
        except Exception:
            pass
with col_titre:
    st.markdown("## Bénin Insights 2025")
    st.markdown(
        "**iSHEERO × DataCamp Hackathon 2026** "
        "— Couverture médiatique internationale du Bénin · Source : GDELT"
    )

st.divider()

df = charger_donnees()

if df is None:
    st.error(
        "Fichier de données introuvable. "
        "Exécutez d'abord `Pipeline.py` pour générer `data/processed/benin_enrichi.parquet`."
    )
    st.stop()


# ── FILTRES TEMPORELS HORIZONTAUX ─────────────────────────────────────────────

st.markdown("**Période d'analyse**")
col_mois, col_dates = st.columns([7, 3])

with col_mois:
    mois_sel = st.radio(
        "Mois :",
        options=list(MOIS_LABELS.keys()),
        format_func=lambda x: MOIS_LABELS[x],
        horizontal=True,
        index=0,
        key="mois_radio",
    )

with col_dates:
    if mois_sel == 0:
        periode = st.date_input(
            "Plage de dates :",
            value=(DATE_MIN, DATE_MAX),
            min_value=DATE_MIN,
            max_value=DATE_MAX,
            format="DD/MM/YYYY",
            key="plage_dates",
        )
    else:
        st.caption(f"Filtre actif : **{MOIS_LABELS[mois_sel]} 2025**")
        periode = None

st.divider()

# ── FILTRES THÉMATIQUES (SIDEBAR) ─────────────────────────────────────────────

st.sidebar.header("Filtres thématiques")

tons = sorted(df["ton_categorie"].dropna().unique().tolist())
ton_sel = st.sidebar.multiselect(
    "Ton médiatique",
    options=tons,
    format_func=lambda x: LABELS_TON.get(x, x),
    default=tons,
)

quadclasses = sorted(df["quadclass_label"].dropna().unique().tolist())
quad_sel = st.sidebar.multiselect(
    "Type d'événement",
    options=quadclasses,
    format_func=lambda x: LABELS_QUAD.get(x, x),
    default=quadclasses,
)

# ── APPLICATION DES FILTRES ───────────────────────────────────────────────────

if mois_sel != 0:
    df_date = df[df["SQLDATE"].dt.month == mois_sel]
else:
    if isinstance(periode, (list, tuple)) and len(periode) == 2:
        d_start = pd.Timestamp(periode[0])
        d_end   = pd.Timestamp(periode[1])
    elif isinstance(periode, date):
        d_start = d_end = pd.Timestamp(periode)
    else:
        d_start = pd.Timestamp(DATE_MIN)
        d_end   = pd.Timestamp(DATE_MAX)
    df_date = df[(df["SQLDATE"] >= d_start) & (df["SQLDATE"] <= d_end)]

df_filtre = df_date[
    df_date["ton_categorie"].isin(ton_sel)
    & df_date["quadclass_label"].isin(quad_sel)
]

vide = len(df_filtre) == 0

# ── SECTION 1 — VUE D'ENSEMBLE ────────────────────────────────────────────────

st.subheader("Vue d'ensemble")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Événements", f"{len(df_filtre):,}" if not vide else "—")
with col2:
    val = f"{df_filtre['AvgTone'].mean():.2f}" if not vide else "—"
    st.metric("Ton médiatique moyen", val)
with col3:
    val = f"{df_filtre['GoldsteinScale'].mean():.2f}" if not vide else "—"
    st.metric("Score Goldstein moyen", val)
with col4:
    val = str(df_filtre["SQLDATE"].dt.date.nunique()) if not vide else "—"
    st.metric("Jours couverts", val)

st.caption(
    "Ton : −100 (très négatif) → +100 (très positif)   ·   "
    "Goldstein : −10 (déstabilisant) → +10 (stabilisant)"
)
st.divider()

# ── SECTION 2 — ÉVOLUTION TEMPORELLE ─────────────────────────────────────────

st.subheader("Évolution temporelle")
col_ton, col_gold = st.columns(2)

with col_ton:
    if not vide:
        tone_mensuel = (
            df_filtre.groupby("mois_annee")["AvgTone"]
            .mean().reset_index().sort_values("mois_annee")
            .rename(columns={"mois_annee": "Mois", "AvgTone": "Ton moyen"})
        )
        fig1 = px.line(
            tone_mensuel, x="Mois", y="Ton moyen", markers=True,
            title="Ton médiatique mensuel (AvgTone)",
        )
        fig1.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

with col_gold:
    if not vide:
        gold_mensuel = (
            df_filtre.groupby("mois_annee")["GoldsteinScale"]
            .mean().reset_index().sort_values("mois_annee")
            .rename(columns={"mois_annee": "Mois", "GoldsteinScale": "Goldstein moyen"})
        )
        fig_gold = px.line(
            gold_mensuel, x="Mois", y="Goldstein moyen", markers=True,
            title="Stabilité géopolitique — score Goldstein",
            color_discrete_sequence=["#2ca02c"],
        )
        fig_gold.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="0")
        st.plotly_chart(fig_gold, use_container_width=True)
    else:
        st.info("Aucune donnée pour les filtres sélectionnés.")

st.divider()

# ── SECTION 3 — MOMENTS MARQUANTS ─────────────────────────────────────────────
# Calculé sur le dataset complet — résultats fixes, indépendants des filtres actifs

st.subheader("Moments marquants de 2025")

df_anom = df[df["SQLDATE"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)]
if len(df_anom) > 0:
    stats_anom = (
        df_anom.groupby(df_anom["SQLDATE"].dt.strftime("%Y-%m-%d"))
        .agg(
            Événements=("GLOBALEVENTID", "count"),
            Mentions=("NumMentions", "sum"),
            ton_moyen=("AvgTone", "mean"),
            goldstein_moyen=("GoldsteinScale", "mean"),
        )
        .reset_index()
        .rename(columns={"SQLDATE": "Date"})
        .sort_values("Date")
    )
    stats_anom["Ton moyen"]       = stats_anom["ton_moyen"].round(2)
    stats_anom["Goldstein moyen"] = stats_anom["goldstein_moyen"].round(2)
    stats_anom["Événement probable"] = stats_anom["Date"].map(DESCRIPTIONS_ANOMALIES)
    stats_anom = stats_anom[[
        "Date", "Événements", "Mentions",
        "Ton moyen", "Goldstein moyen", "Événement probable",
    ]]
    st.dataframe(stats_anom.set_index("Date"), use_container_width=True)

st.caption(
    "Dates détectées par approche multi-méthodes (Z-score + MAD + fenêtre glissante) — "
    "notebook EDA section 7   ·   "
    "Événements : sources AFP, France 24, Euronews, Jeune Afrique (2025)"
)
st.write("")

if not vide:
    volume_quotidien = (
        df_filtre.dropna(subset=["SQLDATE"])
        .groupby(df_filtre["SQLDATE"].dt.date)
        .size().reset_index(name="Événements")
        .rename(columns={"SQLDATE": "Date"})
    )
    volume_quotidien["Date"] = pd.to_datetime(volume_quotidien["Date"])

    fig2 = px.line(
        volume_quotidien, x="Date", y="Événements",
        title="Volume d'événements par jour",
    )
    anomalies_visibles = volume_quotidien[
        volume_quotidien["Date"].dt.strftime("%Y-%m-%d").isin(DATES_ANOMALIES)
    ]
    if len(anomalies_visibles) > 0:
        fig2.add_scatter(
            x=anomalies_visibles["Date"],
            y=anomalies_visibles["Événements"],
            mode="markers",
            marker=dict(color="crimson", size=10, symbol="x"),
            name="Date anormale",
        )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Aucune donnée pour les filtres sélectionnés.")

st.divider()

# ── SECTION 4 — CARTE DES ÉVÉNEMENTS ──────────────────────────────────────────

st.subheader("Carte des événements au Bénin")

df_geo = df_filtre.dropna(subset=["ActionGeo_Lat", "ActionGeo_Long"]).copy()
df_geo = df_geo[
    (df_geo["ActionGeo_Lat"]  >= BENIN_LAT[0]) & (df_geo["ActionGeo_Lat"]  <= BENIN_LAT[1]) &
    (df_geo["ActionGeo_Long"] >= BENIN_LON[0]) & (df_geo["ActionGeo_Long"] <= BENIN_LON[1])
]

if vide or len(df_geo) == 0:
    st.info(
        "Aucune coordonnée géographique disponible pour les filtres sélectionnés. "
        "Les événements sans localisation précise (hors bounding box Bénin) sont exclus."
    )
else:
    n_total = len(df_geo)
    if n_total > MAP_MAX_POINTS:
        df_geo = df_geo.sample(MAP_MAX_POINTS, random_state=42)

    df_geo["Zone"]   = df_geo["zone_benin"].map(LABELS_ZONES).fillna("Inconnu")
    df_geo["Taille"] = (df_geo["NumMentions"].clip(upper=100).fillna(5) / 10 + 4).round(1)
    df_geo["Lieu"]   = df_geo["ActionGeo_FullName"].fillna("Localisation inconnue")

    fig_map = px.scatter_mapbox(
        df_geo,
        lat="ActionGeo_Lat",
        lon="ActionGeo_Long",
        color="AvgTone",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        range_color=[-6, 6],
        size="Taille",
        size_max=14,
        hover_name="Lieu",
        hover_data={
            "AvgTone":        ":.2f",
            "Zone":           True,
            "Taille":         False,
            "ActionGeo_Lat":  False,
            "ActionGeo_Long": False,
        },
        zoom=5.5,
        center={"lat": 9.3, "lon": 2.3},
        mapbox_style="carto-positron",
        title=(
            f"Localisation des événements — {len(df_geo):,} points"
            + (f" (échantillon sur {n_total:,})" if n_total > MAP_MAX_POINTS else "")
        ),
        labels={"AvgTone": "Ton"},
    )
    fig_map.update_layout(height=520, margin={"r": 0, "l": 0, "t": 40, "b": 0})
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(
        "Couleur : ton médiatique — rouge = négatif · vert = positif   ·   "
        "Taille : volume de mentions   ·   "
        "Coordonnées : ActionGeo_Lat / ActionGeo_Long (GDELT)"
    )

    # Export pour le PowerPoint
    with st.expander("Exporter la carte pour le pitch (PNG)"):
        st.markdown(
            "Génère `outputs/carte_benin_pitch.png` à insérer dans le PowerPoint.\n\n"
            "Nécessite `kaleido` (`pip install kaleido`) ou utilise matplotlib en fallback."
        )
        if st.button("Générer carte_benin_pitch.png"):
            OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
            out_path = OUTPUTS_DIR / "carte_benin_pitch.png"
            exported = False

            # Tentative 1 : kaleido (meilleure qualité)
            try:
                import plotly.io as pio
                pio.write_image(fig_map, str(out_path), width=1400, height=800, scale=2)
                exported = True
                st.success(f"Carte exportée (kaleido) : `{out_path}`")
            except Exception:
                pass

            # Tentative 2 : matplotlib (sans dépendance kaleido)
            if not exported:
                try:
                    import matplotlib
                    matplotlib.use("Agg")
                    import matplotlib.pyplot as plt

                    fig_mpl, ax = plt.subplots(figsize=(12, 9))
                    sc = ax.scatter(
                        df_geo["ActionGeo_Long"],
                        df_geo["ActionGeo_Lat"],
                        c=df_geo["AvgTone"],
                        cmap="RdYlGn",
                        vmin=-6, vmax=6,
                        s=df_geo["Taille"] * 12,
                        alpha=0.65,
                        edgecolors="none",
                    )
                    plt.colorbar(sc, ax=ax, label="Ton médiatique (AvgTone)")
                    ax.set_xlim(BENIN_LON[0] - 0.2, BENIN_LON[1] + 0.2)
                    ax.set_ylim(BENIN_LAT[0] - 0.2, BENIN_LAT[1] + 0.2)
                    ax.set_title(
                        "Événements médiatiques au Bénin — 2025",
                        fontsize=14, pad=12,
                    )
                    ax.set_xlabel("Longitude")
                    ax.set_ylabel("Latitude")
                    ax.grid(True, alpha=0.25, linestyle="--")
                    plt.tight_layout()
                    plt.savefig(str(out_path), dpi=150, bbox_inches="tight")
                    plt.close()
                    exported = True
                    st.success(f"Carte exportée (matplotlib) : `{out_path}`")
                except Exception as e2:
                    st.error(f"Export impossible : {e2}")

st.divider()

# ── SECTION 5 — GÉOGRAPHIE INTERNE ───────────────────────────────────────────

st.subheader("Géographie interne — nord, centre, sud")

if not vide:
    zones = (
        df_filtre.groupby("zone_benin")
        .agg(
            nb_evenements=("GLOBALEVENTID", "count"),
            ton_moyen=("AvgTone", "mean"),
            goldstein_moyen=("GoldsteinScale", "mean"),
        )
        .reset_index()
    )
    zones["Zone"]            = zones["zone_benin"].map(LABELS_ZONES)
    zones["Ton moyen"]       = zones["ton_moyen"].round(2)
    zones["Goldstein moyen"] = zones["goldstein_moyen"].round(2)

    fig3 = px.bar(
        zones.sort_values("ton_moyen"),
        x="Ton moyen", y="Zone", orientation="h",
        title="Ton médiatique moyen par zone",
        color="Ton moyen",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        text="Ton moyen",
    )
    fig3.add_vline(x=0, line_dash="dash", line_color="gray")
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

    zones_display = zones[["Zone", "nb_evenements", "Ton moyen", "Goldstein moyen"]].copy()
    zones_display.columns = ["Zone", "Nb événements", "Ton moyen", "Goldstein moyen"]
    st.dataframe(zones_display.set_index("Zone"), use_container_width=True)
else:
    st.info("Aucune donnée pour les filtres sélectionnés.")

st.divider()

# ── SECTION 6 — NARRATIFS ET ACTEURS ─────────────────────────────────────────

st.subheader("Narratifs et acteurs")
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Types d'événements**")
    if not vide:
        quad_counts = (
            df_filtre.groupby("quadclass_label")
            .size().reset_index(name="Nb")
            .sort_values("Nb", ascending=False)
        )
        quad_counts["Type"] = (
            quad_counts["quadclass_label"]
            .map(LABELS_QUAD)
            .fillna(quad_counts["quadclass_label"])
        )
        fig4 = px.bar(
            quad_counts, x="Nb", y="Type", orientation="h",
            title="Répartition par type d'événement",
            labels={"Nb": "Nb d'événements", "Type": ""},
        )
        fig4.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Aucune donnée.")

with col_right:
    st.markdown("**Pays impliqués dans les événements (hors Bénin)**")
    if not vide:
        top_acteurs = (
            df_filtre[df_filtre["Actor1CountryCode"] != "BEN"]["Actor1CountryCode"]
            .value_counts().head(10).reset_index()
        )
        top_acteurs.columns = ["Code", "Nb"]
        top_acteurs["Pays"] = (
            top_acteurs["Code"].map(NOMS_PAYS).fillna(top_acteurs["Code"])
        )
        fig5 = px.bar(
            top_acteurs, x="Nb", y="Pays", orientation="h",
            title="Top 10 pays des acteurs impliqués",
            labels={"Nb": "Nb d'événements", "Pays": ""},
        )
        fig5.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig5, use_container_width=True)
        st.caption(
            "Ces pays correspondent aux acteurs des événements, "
            "pas aux pays sources des médias."
        )
    else:
        st.info("Aucune donnée.")

st.divider()
st.caption(
    "Source : GDELT Project · iSHEERO × DataCamp Hackathon 2026 · Équipe 04   ·   "
    "Événements contextuels : AFP, France 24, Euronews, Jeune Afrique"
)
