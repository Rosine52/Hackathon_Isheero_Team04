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

@st.cache_data
def generer_donnees_demo():
    rng = np.random.default_rng(42)
    n = 8500
    dates = pd.date_range('2025-04-01', '2026-04-30', periods=n)
    pays_codes = ['FR','US','NG','GB','SN','CI','GH','TG','DE','CN','MA','CM','NE','BF','ML','ZA','BE','CA','RU','BR']
    pays_raw = np.array([22,18,12,8,6,5,4,4,4,3,2,2,2,2,1,1,1,1,1,1],dtype=float)
    pays_p = pays_raw / pays_raw.sum()
    event_codes = ['01','02','03','04','05','06','07','10','11','12','13','14','17','19']
    event_raw = np.array([18,14,12,10,9,8,6,5,5,4,4,3,1,1],dtype=float)
    event_p = event_raw / event_raw.sum()
    lieux = {'Cotonou':(6.365,2.419),'Porto-Novo':(6.497,2.628),'Parakou':(9.337,2.628),
             'Abomey-Calavi':(6.449,2.356),'Natitingou':(10.303,1.381),'Bohicon':(7.178,2.066),
             'Kandi':(11.134,2.937),'Ouidah':(6.353,2.084),'Lokossa':(6.644,1.718),'Djougou':(9.709,1.665)}
    lieux_list = list(lieux.keys())
    lieux_raw = np.array([38,15,12,10,5,5,5,4,3,3],dtype=float)
    lieux_p = lieux_raw / lieux_raw.sum()
    lc = rng.choice(lieux_list, n, p=lieux_p)
    lats = [lieux[l][0]+rng.normal(0,0.05) for l in lc]
    lons = [lieux[l][1]+rng.normal(0,0.05) for l in lc]
    gb = rng.normal(-0.8,3.2,n); ab = rng.normal(-2.1,4.5,n)
    mask = (dates>='2025-10-01')&(dates<='2025-10-31')
    gb[mask]+=rng.normal(-2,1,mask.sum()); ab[mask]+=rng.normal(-3,1.5,mask.sum())
    df = pd.DataFrame({'date':dates,'Actor1CountryCode':rng.choice(pays_codes,n,p=pays_p),
        'EventRootCode':rng.choice(event_codes,n,p=event_p),'GoldsteinScale':np.clip(gb,-10,10),
        'AvgTone':np.clip(ab,-15,15),'NumArticles':rng.integers(1,45,n),
        'ActionGeo_FullName':lc,'ActionGeo_Lat':lats,'ActionGeo_Long':lons})
    df['mois'] = df['date'].dt.to_period('M').astype(str)
    return df

@st.cache_data
def charger_donnees():
    try:
        raise FileNotFoundError
    except:
        return generer_donnees_demo(), True

df, mode_demo = charger_donnees()

PAYS_NOMS = {'FR':'🇫🇷 France','US':'🇺🇸 États-Unis','NG':'🇳🇬 Nigeria','GB':'🇬🇧 Royaume-Uni',
    'SN':'🇸🇳 Sénégal','CI':"🇨🇮 Côte d'Ivoire",'GH':'🇬🇭 Ghana','TG':'🇹🇬 Togo',
    'DE':'🇩🇪 Allemagne','CN':'🇨🇳 Chine','MA':'🇲🇦 Maroc','CM':'🇨🇲 Cameroun',
    'NE':'🇳🇪 Niger','BF':'🇧🇫 Burkina Faso','ML':'🇲🇱 Mali','ZA':'🇿🇦 Afrique du Sud',
    'BE':'🇧🇪 Belgique','CA':'🇨🇦 Canada','RU':'🇷🇺 Russie','BR':'🇧🇷 Brésil'}
CAMEO = {'01':'Déclarations','02':'Appels','03':'Intentions','04':'Consultations',
    '05':'Diplomatie','06':'Coopération','07':'Aide humanitaire','10':'Revendications',
    '11':'Rejets','12':'Accusations','13':'Protestations','14':'Manifestations',
    '17':'Arrestations','19':'Violences'}

with st.sidebar:
    st.markdown("<div style='text-align:center;padding:1rem 0 1.5rem;'><div style='font-size:2.5rem;'>🇧🇯</div><div style='font-family:Playfair Display,serif;font-size:1.1rem;color:#1D9E75;font-weight:700;'>Bénin Insights</div><div style='font-size:0.7rem;color:#666;text-transform:uppercase;'>GDELT · 2025–2026</div></div>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Filtres")
    mois_dispo = sorted(df['mois'].unique())
    m1, m2 = st.select_slider("Période", options=mois_dispo, value=(mois_dispo[0], mois_dispo[-1]))
    tous_pays = sorted(df['Actor1CountryCode'].dropna().unique())
    pays_sel = st.multiselect("Pays sources", options=tous_pays, format_func=lambda x: PAYS_NOMS.get(x,x), default=tous_pays[:8])
    if not pays_sel: pays_sel = tous_pays
    df['erc'] = df['EventRootCode'].astype(str).str.zfill(2)
    tous_evt = sorted(df['erc'].unique())
    evt_sel = st.multiselect("Types d'événements", options=tous_evt, format_func=lambda x: CAMEO.get(x,f'Code {x}'), default=tous_evt)
    if not evt_sel: evt_sel = tous_evt
    st.markdown("---")
    st.warning("⚠️ Mode démo") if mode_demo else st.success("✅ Données GDELT")
    st.markdown("<div style='font-size:0.75rem;color:#555;margin-top:1rem;'>iSHEERO × DataCamp 2026<br>Deadline : <strong style='color:#E85555;'>5 mai 23h59</strong></div>", unsafe_allow_html=True)

dff = df[(df['mois']>=m1)&(df['mois']<=m2)&(df['Actor1CountryCode'].isin(pays_sel))&(df['erc'].isin(evt_sel))].copy()

c1,c2 = st.columns([3,1])
with c1:
    st.markdown("<div class='hero-title'>Bénin <span class='hero-accent'>Insights</span><br>Dashboard</div><div class='hero-sub'>iSHEERO × DataCamp Donates · Hackathon 2026</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='text-align:right;padding-top:1rem;'><div style='font-size:0.75rem;color:#555;text-transform:uppercase;'>Période sélectionnée</div><div style='font-size:1rem;color:#1D9E75;'>{m1} → {m2}</div><div style='font-size:0.75rem;color:#555;margin-top:0.5rem;'>{len(dff):,} événements</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

k1,k2,k3,k4 = st.columns(4)
tm = dff['AvgTone'].mean() if len(dff)>0 else 0
gm = dff['GoldsteinScale'].mean() if len(dff)>0 else 0
np2 = dff['Actor1CountryCode'].nunique()
with k1: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{len(dff):,}</div><div class='kpi-label'>Événements analysés</div><div class='kpi-delta'>période sélectionnée</div></div>", unsafe_allow_html=True)
with k2:
    cc = '#E85555' if tm<0 else '#1D9E75'
    st.markdown(f"<div class='kpi-card'><div class='kpi-value' style='color:{cc};'>{tm:.2f}</div><div class='kpi-label'>Ton médiatique moyen</div><div class='kpi-delta'>{'↘ Négatif' if tm<0 else '↗ Positif'}</div></div>", unsafe_allow_html=True)
with k3:
    cc2 = '#E85555' if gm<0 else '#1D9E75'
    st.markdown(f"<div class='kpi-card'><div class='kpi-value' style='color:{cc2};'>{gm:.2f}</div><div class='kpi-label'>Score de Goldstein</div><div class='kpi-delta'>{'⚠️ Instabilité' if gm<0 else '✅ Stabilité'}</div></div>", unsafe_allow_html=True)
with k4: st.markdown(f"<div class='kpi-card'><div class='kpi-value'>{np2}</div><div class='kpi-label'>Pays sources actifs</div><div class='kpi-delta'>médias couvrant le Bénin</div></div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>📈 Évolution de la couverture médiatique</div><hr class='section-line'>", unsafe_allow_html=True)
dm = dff.groupby('mois').size().reset_index(name='nb').sort_values('mois')
if len(dm)>0:
    moy = dm['nb'].mean(); imax = dm['nb'].idxmax()
    f1 = go.Figure()
    f1.add_trace(go.Scatter(x=dm['mois'],y=dm['nb'],fill='tozeroy',fillcolor='rgba(29,158,117,0.12)',line=dict(color='#1D9E75',width=2.5),mode='lines+markers',marker=dict(size=7,color='#1D9E75'),hovertemplate='<b>%{x}</b><br>%{y} événements<extra></extra>'))
    f1.add_hline(y=moy,line_dash='dash',line_color='#F59E0B',line_width=1.5,annotation_text=f'Moy:{moy:.0f}',annotation_position='top right',annotation_font_color='#F59E0B')
    f1.add_annotation(x=dm.loc[imax,'mois'],y=dm.loc[imax,'nb'],text=f"📍 Pic:{dm.loc[imax,'nb']}",showarrow=True,arrowhead=2,arrowcolor='#1D9E75',bgcolor='#1a2a24',bordercolor='#1D9E75',font=dict(color='#1D9E75',size=11))
    f1.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#888780'),xaxis=dict(tickangle=-45,gridcolor='#1a1a1a'),yaxis=dict(gridcolor='#1a1a1a'),height=340,margin=dict(l=10,r=10,t=20,b=60),hovermode='x unified',showlegend=False)
    st.plotly_chart(f1,use_container_width=True)
    st.markdown(f"<div class='insight-box'><strong>💡 Insight :</strong> Moyenne de <strong>{moy:.0f} événements/mois</strong>. Pic en <strong>{dm.loc[imax,'mois']}</strong> avec {dm.loc[imax,'nb']} événements.</div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

cv2,cv3 = st.columns([1,1],gap="large")
with cv2:
    st.markdown("<div class='section-title'>🗺️ Carte des événements</div><hr class='section-line'>", unsafe_allow_html=True)
    dg = dff.dropna(subset=['ActionGeo_Lat','ActionGeo_Long']).copy()
    dg = dg[dg['ActionGeo_Lat'].between(6.0,12.5)&dg['ActionGeo_Long'].between(0.5,3.9)]
    if len(dg)>0:
        dgg = dg.groupby(['ActionGeo_Lat','ActionGeo_Long','ActionGeo_FullName']).agg(nb=('ActionGeo_Lat','count'),tone=('AvgTone','mean')).reset_index()
        fm = px.scatter_mapbox(dgg,lat='ActionGeo_Lat',lon='ActionGeo_Long',size='nb',color='tone',hover_name='ActionGeo_FullName',hover_data={'nb':True,'tone':':.1f','ActionGeo_Lat':False,'ActionGeo_Long':False},color_continuous_scale='RdYlGn',color_continuous_midpoint=0,size_max=40,zoom=5.8,center={'lat':9.3,'lon':2.3},mapbox_style='carto-darkmatter',height=380)
        fm.update_layout(paper_bgcolor='rgba(0,0,0,0)',margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fm,use_container_width=True)
        tl = dgg.nlargest(1,'nb').iloc[0]
        st.markdown(f"<div class='insight-box'><strong>💡 Insight :</strong> Zone la plus couverte : <strong>{tl['ActionGeo_FullName']}</strong> — {int(tl['nb'])} événements.</div>", unsafe_allow_html=True)

with cv3:
    st.markdown("<div class='section-title'>🌍 Pays qui citent le Bénin</div><hr class='section-line'>", unsafe_allow_html=True)
    tp = dff['Actor1CountryCode'].value_counts().head(12).reset_index()
    tp.columns=['code','count']
    tp['label'] = tp['code'].map(PAYS_NOMS).fillna(tp['code'])
    tp = tp.sort_values('count',ascending=True)
    afr = ['NG','SN','CI','GH','TG','NE','CM','ML','BF','MA','ZA','ET','BJ','GN']
    tp['color'] = tp['code'].apply(lambda x:'#1D9E75' if x in afr else '#3B7DD8')
    f3 = go.Figure(go.Bar(x=tp['count'],y=tp['label'],orientation='h',marker_color=tp['color'],text=tp['count'],textposition='outside',textfont=dict(color='#888780',size=11),hovertemplate='<b>%{y}</b><br>%{x} événements<extra></extra>'))
    f3.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#888780'),xaxis=dict(gridcolor='#1a1a1a'),yaxis=dict(tickfont=dict(color='#E8E8E6',size=12)),height=380,margin=dict(l=10,r=40,t=10,b=20),showlegend=False)
    st.plotly_chart(f3,use_container_width=True)
    t1=tp.iloc[-1]; pct=tp.tail(3)['count'].sum()/tp['count'].sum()*100
    st.markdown(f"<div class='insight-box'><strong>💡 Insight :</strong> <strong>{t1['label']}</strong> domine. Top 3 = <strong>{pct:.0f}%</strong> de l'attention mondiale.</div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>⚖️ Stabilité — Score de Goldstein</div><hr class='section-line'>", unsafe_allow_html=True)
dg2 = dff.groupby('mois')['GoldsteinScale'].mean().reset_index()
dg2.columns=['mois','score']
dg2 = dg2.sort_values('mois')
dg2['lisse'] = dg2['score'].rolling(3,center=True,min_periods=1).mean()
if len(dg2)>0:
    sg = dg2['score'].mean()
    f5 = go.Figure()
    f5.add_trace(go.Bar(x=dg2['mois'],y=dg2['score'],name='Score mensuel',marker_color=['rgba(232,85,85,0.35)' if v<0 else 'rgba(29,158,117,0.35)' for v in dg2['score']],hovertemplate='<b>%{x}</b><br>%{y:.2f}<extra></extra>'))
    f5.add_trace(go.Scatter(x=dg2['mois'],y=dg2['lisse'],mode='lines+markers',line=dict(color='#F59E0B',width=3),marker=dict(size=7,color='#F59E0B'),name='Tendance'))
    f5.add_hline(y=0,line_dash='dash',line_color='#555',line_width=1,annotation_text='Neutralité',annotation_font_color='#555')
    f5.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font=dict(color='#888780'),xaxis=dict(tickangle=-45,gridcolor='#1a1a1a'),yaxis=dict(gridcolor='#1a1a1a'),height=320,margin=dict(l=10,r=10,t=10,b=60),legend=dict(orientation='h',yanchor='bottom',y=1.02,font=dict(color='#888780')))
    st.plotly_chart(f5,use_container_width=True)
    cc3='#E85555' if sg<0 else '#1D9E75'
    st.markdown(f"<div class='insight-box'><strong>💡 Insight :</strong> Score moyen <strong style='color:{cc3};'>{sg:.2f}/10</strong>. Contexte globalement <strong>{'instable ⚠️' if sg<0 else 'stable ✅'}</strong>.</div>", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
st.markdown(f"<div style='text-align:center;padding:1.5rem 0;font-size:0.8rem;color:#444;'>🇧🇯 <strong style='color:#1D9E75;'>Bénin Insights Dashboard</strong> · iSHEERO × DataCamp 2026 · {'⚠️ Mode démo' if mode_demo else '✅ Données GDELT'}</div>", unsafe_allow_html=True)
