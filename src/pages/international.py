# src/pages/international.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_international(df_dict):
    """
    Analyse internationale avec carte interactive par pays
    """
    st.title("🌍 Analyse Internationale du Tourisme")
    
    df_region = df_dict["frequentation_region"]
    
    # Conversion date
    if 'Mois' in df_region.columns:
        df_region['Mois'] = pd.to_datetime(df_region['Mois'])
    
    # ========================================
    # FILTRES INTERACTIFS
    # ========================================
    st.sidebar.title("🎯 Filtres")
    
    # Sélection de région
    regions_dispo = ['Tous'] + sorted(df_region['Region'].unique().tolist())
    region_selected = st.sidebar.selectbox(
        "Choisir une région",
        regions_dispo
    )
    
    # Filtre par région
    if region_selected != 'Tous':
        df_filtered = df_region[df_region['Region'] == region_selected].copy()
    else:
        df_filtered = df_region.copy()
    
    # Filtre temporel
    if 'Mois' in df_filtered.columns:
        annees = sorted(df_filtered['Mois'].dt.year.unique())
        if len(annees) > 1:
            annee_selected = st.sidebar.select_slider(
                "Année",
                options=annees,
                value=annees[-1]
            )
            df_filtered = df_filtered[df_filtered['Mois'].dt.year == annee_selected]
    
    # Sélection métrique
    metric = st.sidebar.radio(
        "Métrique à afficher",
        ["Nombre de touristes", "Nuitées touristiques", "Durée de séjour moyenne"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.metric("Pays affichés", df_filtered['Pays'].nunique())
    
    # ========================================
    # MAPPING ISO3 MANUEL
    # ========================================
    iso3_mapping = {
        'Canada': 'CAN',
        'États-Unis': 'USA',
        'États-Unis (y compris Hawaii)': 'USA',
        'Mexique': 'MEX',
        'Brésil': 'BRA',
        'Argentine': 'ARG',
        'Chili': 'CHL',
        'Colombie': 'COL',
        'Pérou': 'PER',
        'Royaume-Uni': 'GBR',
        'Allemagne': 'DEU',
        'Italie': 'ITA',
        'Espagne': 'ESP',
        'France': 'FRA',
        'Belgique': 'BEL',
        'Pays-Bas': 'NLD',
        'Suisse': 'CHE',
        'Autriche': 'AUT',
        'Portugal': 'PRT',
        'Grèce': 'GRC',
        'Pologne': 'POL',
        'Suède': 'SWE',
        'Norvège': 'NOR',
        'Danemark': 'DNK',
        'Finlande': 'FIN',
        'Irlande': 'IRL',
        'Chine': 'CHN',
        'Japon': 'JPN',
        'Corée du Sud': 'KOR',
        'Inde': 'IND',
        'Thaïlande': 'THA',
        'Vietnam': 'VNM',
        'Singapour': 'SGP',
        'Malaisie': 'MYS',
        'Indonésie': 'IDN',
        'Philippines': 'PHL',
        'Australie': 'AUS',
        'Nouvelle-Zélande': 'NZL',
        'Afrique du Sud': 'ZAF',
        'Maroc': 'MAR',
        'Tunisie': 'TUN',
        'Algérie': 'DZA',
        'Égypte': 'EGY',
        'Russie': 'RUS',
        'Turquie': 'TUR',
        'Arabie Saoudite': 'SAU',
        'Émirats Arabes Unis': 'ARE',
        'Israël': 'ISR',
        'Liban': 'LBN'
    }
    
    # ========================================
    # CARTE CHOROPLÈTHE INTERACTIVE PAR PAYS
    # ========================================
    st.header(f"🗺️ Carte Interactive - {metric}")
    
    # Agrégation par pays
    df_pays = df_filtered.groupby('Pays', as_index=False).agg({
        'Nombre de touristes': 'sum',
        'Nuitées touristiques': 'sum',
        'Durée de séjour moyenne': 'mean',
        'Region': 'first'
    })
    
    # Ajouter ISO3
    df_pays['ISO3'] = df_pays['Pays'].map(iso3_mapping)
    
    # Supprimer lignes sans ISO3
    df_pays_valides = df_pays[df_pays['ISO3'].notna()].copy()
    
    if not df_pays_valides.empty:
        # Créer la carte
        fig_map = px.choropleth(
            df_pays_valides,
            locations='ISO3',
            color=metric,
            hover_name='Pays',
            hover_data={
                'ISO3': False,
                'Region': True,
                'Nombre de touristes': ':,.0f',
                'Nuitées touristiques': ':,.0f',
                'Durée de séjour moyenne': ':.1f'
            },
            color_continuous_scale='Plasma',
            title=f"{metric} par pays d'origine",
            labels={metric: metric}
        )
        
        fig_map.update_layout(
            geo=dict(
                showframe=True,
                showcoastlines=True,
                projection_type='natural earth',
                bgcolor='aliceblue',
                showlakes=True,
                lakecolor='lightblue'
            ),
            height=600
        )
        
        st.plotly_chart(fig_map, use_container_width=True)
        
        # Info sur pays non affichés
        nb_pays_sans_iso = len(df_pays) - len(df_pays_valides)
        if nb_pays_sans_iso > 0:
            st.info(f"ℹ️ {nb_pays_sans_iso} pays non affichés sur la carte (code ISO3 manquant)")
    else:
        st.warning("⚠️ Aucun pays avec code ISO3 valide dans les données filtrées")
    
    # ========================================
    # GRAPHIQUE DYNAMIQUE : TOP PAYS
    # ========================================
    st.header("🏆 Classement des Pays")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        top_n = st.slider("Nombre de pays à afficher", 5, 30, 15)
        tri_ordre = st.radio("Ordre", ["Décroissant", "Croissant"])
    
    with col2:
        df_top = df_pays.nlargest(top_n, metric) if tri_ordre == "Décroissant" else df_pays.nsmallest(top_n, metric)
        
        fig_bar = px.bar(
            df_top.sort_values(metric, ascending=(tri_ordre == "Croissant")),
            x=metric,
            y='Pays',
            orientation='h',
            color=metric,
            color_continuous_scale='Turbo',
            text=metric,
            title=f"Top {top_n} pays - {metric}"
        )
        
        fig_bar.update_traces(
            texttemplate='%{text:,.0f}' if metric != "Durée de séjour moyenne" else '%{text:.1f}j',
            textposition='outside'
        )
        fig_bar.update_layout(showlegend=False, height=500)
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # ========================================
    # COMPARAISON PAYS (GRAPHIQUE INTERACTIF)
    # ========================================
    st.header("⚖️ Comparaison entre Pays")
    
    pays_dispo = sorted(df_filtered['Pays'].unique())
    pays_selected = st.multiselect(
        "Sélectionnez des pays à comparer",
        options=pays_dispo,
        default=pays_dispo[:5] if len(pays_dispo) >= 5 else pays_dispo
    )
    
    if pays_selected:
        df_compare = df_filtered[df_filtered['Pays'].isin(pays_selected)]
        
        # Agrégation
        df_compare_agg = df_compare.groupby('Pays', as_index=False).agg({
            'Nombre de touristes': 'sum',
            'Nuitées touristiques': 'sum',
            'Durée de séjour moyenne': 'mean'
        })
        
        # Graphique radar
        fig_radar = go.Figure()
        
        # Normalisation des données pour le radar
        metrics_radar = ['Nombre de touristes', 'Nuitées touristiques', 'Durée de séjour moyenne']
        
        for _, row in df_compare_agg.iterrows():
            max_touristes = df_compare_agg['Nombre de touristes'].max()
            max_nuitees = df_compare_agg['Nuitées touristiques'].max()
            max_duree = df_compare_agg['Durée de séjour moyenne'].max()
            
            values = [
                row['Nombre de touristes'] / max_touristes * 100 if max_touristes > 0 else 0,
                row['Nuitées touristiques'] / max_nuitees * 100 if max_nuitees > 0 else 0,
                row['Durée de séjour moyenne'] / max_duree * 100 if max_duree > 0 else 0
            ]
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values + [values[0]],
                theta=metrics_radar + [metrics_radar[0]],
                fill='toself',
                name=row['Pays']
            ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            title="Comparaison multi-critères (normalisée à 100)",
            height=500
        )
        
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # ========================================
    # ÉVOLUTION TEMPORELLE PAR PAYS
    # ========================================
    if 'Mois' in df_filtered.columns and pays_selected:
        st.header("📈 Évolution Temporelle")
        
        df_evolution = df_filtered[df_filtered['Pays'].isin(pays_selected)]
        
        df_evolution_agg = df_evolution.groupby(
            ['Mois', 'Pays'],
            as_index=False
        )['Nombre de touristes'].sum()
        
        fig_line = px.line(
            df_evolution_agg,
            x='Mois',
            y='Nombre de touristes',
            color='Pays',
            markers=True,
            title="Évolution mensuelle du nombre de touristes",
            labels={'Nombre de touristes': 'Touristes (milliers)'}
        )
        
        fig_line.update_layout(
            hovermode='x unified',
            height=400,
            legend=dict(orientation="h", y=-0.2)
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
    
    # ========================================
    # STATISTIQUES DÉTAILLÉES
    # ========================================
    st.header("📊 Statistiques Détaillées")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Touristes",
            f"{df_filtered['Nombre de touristes'].sum():,.0f}k"
        )
    
    with col2:
        moyenne_pays = df_pays['Nombre de touristes'].mean()
        st.metric(
            "Moyenne par pays",
            f"{moyenne_pays:,.0f}k"
        )
    
    with col3:
        if not df_pays.empty:
            pays_top = df_pays.loc[df_pays['Nombre de touristes'].idxmax(), 'Pays']
            st.metric(
                "Pays le plus actif",
                pays_top
            )
        else:
            st.metric("Pays le plus actif", "N/A")
    
    with col4:
        st.metric(
            "Durée moyenne",
            f"{df_filtered['Durée de séjour moyenne'].mean():.1f} jours"
        )
    
    # ========================================
    # TABLE INTERACTIVE
    # ========================================
    with st.expander("📋 Tableau détaillé des pays"):
        # Options d'affichage
        col_a, col_b = st.columns(2)
        
        with col_a:
            tri_col = st.selectbox(
                "Trier par",
                ['Nombre de touristes', 'Nuitées touristiques', 'Durée de séjour moyenne']
            )
        
        with col_b:
            tri_sens = st.radio("Ordre", ["⬇️ Décroissant", "⬆️ Croissant"], horizontal=True)
        
        df_display = df_pays.sort_values(
            tri_col,
            ascending=(tri_sens == "⬆️ Croissant")
        )
        
        st.dataframe(
            df_display[['Pays', 'Region', 'Nombre de touristes', 'Nuitées touristiques', 'Durée de séjour moyenne']],
            use_container_width=True,
            height=400
        )
        
        # Export CSV
        csv = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            "⬇️ Télécharger (CSV)",
            csv,
            "tourisme_international.csv",
            "text/csv"
        )