import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Bénin Insights Dashboard", page_icon="🇧🇯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap');
.stApp{background-color:#0D0D0D;font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"]{background-color:#111111;border-right:1px solid #1D9E75;}
[data-testid="stSidebar"] *{color:#E8E8E6 !important;}
.hero-title{font-family:'Playfair Display',serif;font-size:3rem;font-weight:900;color:#FFFFFF;line-height:1.1;margin:0;}
.hero-accent{color:#1D9E75;}
.hero-sub{font-size:1rem;color:#888780;font-weight:300;margin-top:0.5rem;letter-spacing:0.05em;text-transform:uppercase;}
.kpi-card{background:#161616;border:1px solid #222;border-top:3px solid #1D9E75;border-radius:8px;padding:1.25rem 1.5rem;margin-bottom:1rem;}
.kpi-value{font-family:'Playfair Display',serif;font-size:2.2rem;font-weight:700;color:#1D9E75;margin:0;line-height:1;}
.kpi-label{font-size:0.78rem;color:#888780;text-transform:uppercase;letter-spacing:0.08em;margin-top:0.4rem;}
.kpi-delta{font-size:0.85rem;color:#E8E8E6;margin-top:0.3rem;}
.section-title{font-family:'Playfair Display',serif;font-size:1.4rem;color:#FFFFFF;margin-bottom:0.2rem;}
.section-line{width:40px;height:3px;background:#1D9E75;margin-bottom:1.2rem;border:none;}
.insight-box{background:#161616;border-left:3px solid #1D9E75;border-radius:0 6px 6px 0;padding:1rem 1.25rem;margin-top:0.75rem;font-size:0.9rem;color:#C8C8C6;line-height:1.6;}
.insight-box strong{color:#1D9E75;}
.custom-divider{border:none;border-top:1px solid #222;margin:2rem 0;}
</style>
""", unsafe_allow_html=True)

CAMEO = {1:'Déclarations',2:'Appels',3:'Intentions',4:'Consultations',
    5:'Diplomatie',6:'Coopération',7:'Aide humanitaire',8:'Concessions',
    9:'Enquêtes',10:'Revendications',11:'Rejets',12:'Accusations',
    13:'Protestations',14:'Manifestations',15:'Menaces',16:'Sanctions',
    17:'Arrestations',18:'Violences verbales',19:'Violences armées'}

PAYS = {'BEN':'🇧🇯 Bénin','NGA':'🇳🇬 Nigeria','FRA':'🇫🇷 France',
    'AFR':'🌍 Afrique','WAF':'🌍 Afrique Ouest','NER':'🇳🇪 Niger',
    'BFA':'🇧🇫 Burkina Faso','TGO':'🇹🇬 Togo','GBR':'🇬🇧 Royaume-Uni',
    'USA':'🇺🇸 États-Unis','CHN':'🇨🇳 Chine','SEN':'🇸🇳 Sénégal',
    'CIV':"🇨🇮 Côte d'Ivoire",'GHA':'🇬🇭 Ghana'}

@st.cache_data
def charger_donnees():
    try:
        df = pd.read_csv('donnees_benin.csv', low_memory=False)
        df['date'] = pd.to_datetime(df['SQLDATE'].astype(str), format='%Y%m%d', errors='coerce')
        df = df.dropna(subset=['date'])
        df['mois'] = df['date'].dt.to_period('M').astype(str)
        df['EventLabel'] = df['EventRootCode'].map(CAMEO).fillna('Code '+df['EventRootCode'].astype(str))
        df['categorie'] = df['EventRootCode'].apply(
            lambda x: '🔴 Conflit' if x>=13 else ('🟢 Coopération' if x<=7 else '🟡 Neutre'))
        return df, False
    except:
        st.error("⚠️ Fichier donnees_benin.csv introuvable. Place-le dans le même dossier que app.py")
        st.stop()

df, _ = charger_donnees()

# SIDEBAR
with st.sidebar:
    st.markdown("<div style='text-align:center;padding:1rem 0 1.5rem;'><div style='font-size:2.5rem;'>🇧🇯</div><div style='font-family:Playfair Display,serif;font-size:1.1rem;color:#1D9E75;font-weight:700;'>Bénin Insights</div><div style='font-size:0.7rem;color:#666;text-transform:uppercase;'>GDELT · 2025</div></div>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Filtres")
    mois_dispo = sorted(df['mois'].unique())
    m1, m2 = st.select_slider("Période 2025", options=mois_dispo, value=(mois_dispo[0], mois_dispo[-1]))
    tous_pays = sorted(df['Actor1CountryCode'].dropna().unique())
    pays_sel = st.multiselect("Pays sources", options=tous_pays, format_func=lambda x: PAYS.get(x,x), default=tous_pays[:8])
    if not pays_sel: pays_sel = tous_pays
    tous_evt = sorted(df['EventRootCode'].unique())
    evt_sel = st.multiselect("Types d'événements", options=tous_evt, format_func=lambda x: CAMEO.get(x,f'Code {x}'), default=tous_evt)
    if not evt_sel: evt_sel = tous_evt
    st.markdown("---")
    st.success(f"✅ {len(df):,} événements réels GDELT")
    st.markdown("<div style='font-size:0.75rem;color:#555;margin-top:1rem;'>iSHEERO × DataCamp 2026<br>Données : GDELT Jan–Déc 2025</div>", unsafe_allow_html=True)

# FILTRES
dff = df[(df['mois']>=m1)&(df['mois']<=m2)&(df['Actor1CountryCode'].isin(pays_sel))&(df['EventRootCode'].isin(evt_sel))].copy()

# HEADER
c1,c2 = st.columns([3,1])
with c1:
    st.markdown("<div class='hero-title'>Bénin <span class='hero-accent'>Insights</span><br>Dashboard</div><div class='hero-sub'>iSHEERO × DataCamp Donates · Hackathon 2026</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='text-align:right;padding-top:1rem;'><div style='font-size:0.75rem;color:#555;text-transform:uppercase;'>Période</div><div style='font-size:1rem;color:#1D9E75;'>{m1} → {m2}</div><div style='font-size:0.75rem;color:#555;margin-top:0.5rem;'>{len(dff):,} événements</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# KPIs
k1,k2,k3,k4 = st.columns(4)
tm = dff['AvgTone'].mean() if len(dff)>0 else 0
gm = dff['GoldsteinScale'].mean() if len(dff)>0 else 0
np2 = dff['Actor1CountryCode'].nunique()
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{len(dff):,}</div><div class='kpi-label'>Événements GDELT</div><div class='kpi-delta'>données réelles 2025</div></div>", unsafe_allow_html=True)
with k2:
    cc='#E85555' if tm<0 else '#1D9E75'
    st.markdown(f"<div class='kpi-card'><div class='kpi-value' style='color:{cc};'>{tm:.2f}</div><div class='kpi-label'>Ton médiatique moyen</div><div class='kpi-delta'>{'↘ Négatif' if tm<0 else '↗ Positif'}</div></div>", unsafe_allow_html=True)
with k3:
    cc2='#E85555' if gm<0 else '#1D9E75'
    st.markdown(f"<div class='kpi-card'><div class='kpi-value' style='color:{cc2};'>{gm:.2f}</div><div class='kpi-label'>Score de Goldstein</div><div class='kpi-delta'>{'⚠️ Instabilité' if gm<0 else '✅ Stabilité'}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{np2}</div><div class='kpi-label'>Pays sources actifs</div><div class='kpi-delta'>médias couvrant le Bénin</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# VIZ 1 — GOLDSTEIN
st.markdown("<div class='section-title'>⚖️ Score de Goldstein — Stabilité 2025</div><hr class='section-line'>", unsafe_allow_html=True)
dg = dff.groupby('mois').agg(score=('GoldsteinScale','mean'),nb=('GoldsteinScale','count')).reset_index().sort_values('mois')
dg['lisse'] = dg['score'].rolling(3,center=True,min_periods=1).mean()
if len(dg)>0:
    sg = dg['score'].mean()
    f1 = go.Figure()
    f1.add_trace(go.Bar(x=dg['mois'],y=dg['score'],name='Score mensuel',
        marker_color=['rgba(232,85,85,0.5)' if v<0 else 'rgba(29,158,117,0.5)' for v in dg['score']],
        hovertemplate='<b>%{x}</b><br>%{y:.2f}<extra></extra>'))
    f1.add_trace(go.Scatter(x=dg['mois'],y=dg['lisse'],mode='lines+markers',
        line=dict(color='#534AB7',width=3),marker=dict(size=8),name='Tendance'))
    f1.add_hline(y=0,line_dash='dash',line_color='gray',annotation_text='Neutralité',annotation_position='top right')
    f1.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888780'),xaxis=dict(tickangle=-45,gridcolor='#1a1a1a'),
        yaxis=dict(gridcolor='#1a1a1a'),height=340,margin=dict(l=10,r=10,t=20,b=60),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,font=dict(color='#888780')))
    st.plotly_chart(f1,use_container_width=True)
    cc3='#E85555' if sg<0 else '#1D9E75'
    pire = dg.loc[dg['score'].idxmin()]
    st.markdown(f"<div class='insight-box'><strong>💡 Insight Q6 :</strong> Score moyen 2025 : <strong style='color:{cc3};'>{sg:.2f}/10</strong>. Contexte <strong>{'instable ⚠️' if sg<0 else 'stable ✅'}</strong>. Mois le plus bas : <strong>{pire['mois']}</strong> ({pire['score']:.2f}).</div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# VIZ 2 + VIZ 3
cv2,cv3 = st.columns([1,1],gap="large")

with cv2:
    st.markdown("<div class='section-title'>🗺️ Carte des événements</div><hr class='section-line'>", unsafe_allow_html=True)
    dg2 = dff.dropna(subset=['ActionGeo_Lat','ActionGeo_Long']).copy()
    dg2 = dg2[dg2['ActionGeo_Lat'].between(6.0,12.5)&dg2['ActionGeo_Long'].between(0.5,3.9)]
    if len(dg2)>0:
        dgg = dg2.groupby(['ActionGeo_Lat','ActionGeo_Long','ActionGeo_FullName']).agg(
            nb=('ActionGeo_Lat','count'),tone=('AvgTone','mean')).reset_index()
        fm = px.scatter_mapbox(dgg,lat='ActionGeo_Lat',lon='ActionGeo_Long',
            size='nb',color='tone',hover_name='ActionGeo_FullName',
            hover_data={'nb':True,'tone':':.1f','ActionGeo_Lat':False,'ActionGeo_Long':False},
            color_continuous_scale='RdYlGn',color_continuous_midpoint=0,
            size_max=40,zoom=5.8,center={'lat':9.3,'lon':2.3},
            mapbox_style='carto-darkmatter',height=380)
        fm.update_layout(paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fm,use_container_width=True)
        tl = dgg.nlargest(1,'nb').iloc[0]
        st.markdown(f"<div class='insight-box'><strong>💡 Insight Q9 :</strong> Zone la plus couverte : <strong>{tl['ActionGeo_FullName']}</strong> ({int(tl['nb'])} événements).</div>", unsafe_allow_html=True)

with cv3:
    st.markdown("<div class='section-title'>🌍 Pays qui citent le Bénin</div><hr class='section-line'>", unsafe_allow_html=True)
    tp = dff['Actor1CountryCode'].value_counts().head(12).reset_index()
    tp.columns=['code','count']
    tp['label'] = tp['code'].map(PAYS).fillna('🌐 '+tp['code'])
    tp = tp.sort_values('count',ascending=True)
    # Ton par pays
    ton_pays = dff.groupby('Actor1CountryCode')['AvgTone'].mean()
    tp['ton'] = tp['code'].map(ton_pays)
    f3 = go.Figure(go.Bar(
        x=tp['count'],y=tp['label'],orientation='h',
        marker=dict(color=tp['ton'],colorscale='RdYlGn',cmid=0,
            showscale=True,colorbar=dict(title='Ton',len=0.5)),
        text=tp['count'],textposition='outside',
        textfont=dict(color='#888780',size=11),
        hovertemplate='<b>%{y}</b><br>%{x} événements<extra></extra>'
    ))
    f3.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888780'),xaxis=dict(gridcolor='#1a1a1a'),
        yaxis=dict(tickfont=dict(color='#E8E8E6',size=12)),
        height=380,margin=dict(l=10,r=60,t=10,b=20),showlegend=False)
    st.plotly_chart(f3,use_container_width=True)
    t1=tp.iloc[-1]
    pct=tp.tail(3)['count'].sum()/tp['count'].sum()*100
    st.markdown(f"<div class='insight-box'><strong>💡 Insight Q7 :</strong> <strong>{t1['label']}</strong> domine. Top 3 = <strong>{pct:.0f}%</strong> de l'attention mondiale.</div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# VIZ 4 — VOLUME MENSUEL
st.markdown("<div class='section-title'>📅 Volume médiatique mensuel 2025</div><hr class='section-line'>", unsafe_allow_html=True)
dm = dff.groupby('mois').agg(nb=('GLOBALEVENTID','count'),articles=('NumArticles','sum')).reset_index().sort_values('mois')
if len(dm)>0:
    imax = dm['nb'].idxmax()
    f4 = go.Figure()
    f4.add_trace(go.Bar(x=dm['mois'],y=dm['nb'],name="Événements",
        marker_color='rgba(29,158,117,0.7)',
        hovertemplate='<b>%{x}</b><br>%{y} événements<extra></extra>'))
    f4.add_trace(go.Scatter(x=dm['mois'],y=dm['articles'],mode='lines+markers',
        name='Articles publiés',line=dict(color='#F59E0B',width=2.5),
        marker=dict(size=7),yaxis='y2'))
    f4.add_annotation(x=dm.loc[imax,'mois'],y=dm.loc[imax,'nb'],
        text=f"📍 Pic: {dm.loc[imax,'nb']}",showarrow=True,arrowhead=2,
        arrowcolor='#1D9E75',bgcolor='#1a2a24',bordercolor='#1D9E75',
        font=dict(color='#1D9E75',size=11))
    f4.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888780'),
        xaxis=dict(tickangle=-45,gridcolor='#1a1a1a'),
        yaxis=dict(gridcolor='#1a1a1a',titlefont=dict(color='#1D9E75')),
        yaxis2=dict(overlaying='y',side='right',titlefont=dict(color='#F59E0B')),
        height=320,margin=dict(l=10,r=60,t=20,b=60),
        legend=dict(orientation='h',yanchor='bottom',y=1.02,font=dict(color='#888780')))
    st.plotly_chart(f4,use_container_width=True)
    st.markdown(f"<div class='insight-box'><strong>💡 Insight Q8 :</strong> Pic médiatique en <strong>{dm.loc[imax,'mois']}</strong> avec {dm.loc[imax,'nb']} événements. Coïncide probablement avec un événement politique ou sécuritaire majeur au Bénin.</div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;padding:1.5rem 0;font-size:0.8rem;color:#444;'>🇧🇯 <strong style='color:#1D9E75;'>Bénin Insights Dashboard</strong> · iSHEERO × DataCamp 2026 · ✅ Données réelles GDELT 2025</div>", unsafe_allow_html=True)
