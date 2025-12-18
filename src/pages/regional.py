# src/pages/regional.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_regional(df_dict):
    """
    Page d'analyse régionale avec VRAIES cartes interactives
    """
    st.title("🗺️ Analyse Géographique du Tourisme")
    
    # Récupération des données
    df_region = df_dict["frequentation_region"]
    
    # Vérifier les colonnes disponibles
    st.sidebar.info(f"Colonnes disponibles : {', '.join(df_region.columns)}")
    
    # Conversion Mois en datetime
    if 'Mois' in df_region.columns:
        df_region['Mois'] = pd.to_datetime(df_region['Mois'])
    
    # ========================================
    # FILTRES DYNAMIQUES DANS LA SIDEBAR
    # ========================================
    st.sidebar.title("🎛️ Filtres Interactifs")
    
    # Filtre temporel avec slider
    if 'Mois' in df_region.columns:
        dates_uniques = sorted(df_region['Mois'].dt.to_period('M').unique())
        dates_str = [str(d) for d in dates_uniques]
        
        if len(dates_str) > 1:
            periode_selectionnee = st.sidebar.select_slider(
                "📅 Sélectionnez la période",
                options=dates_str,
                value=(dates_str[0], dates_str[-1])
            )
            
            # Conversion en datetime pour filtrage
            date_debut = pd.to_datetime(periode_selectionnee[0])
            date_fin = pd.to_datetime(periode_selectionnee[1])
            
            df_filtered = df_region[
                (df_region['Mois'] >= date_debut) & 
                (df_region['Mois'] <= date_fin)
            ].copy()
        else:
            df_filtered = df_region.copy()
    else:
        df_filtered = df_region.copy()
    
    # Filtre sur indicateur
    indicateur = st.sidebar.radio(
        "📊 Indicateur à visualiser",
        ["Nombre de touristes", "Nuitées touristiques", "Durée de séjour moyenne"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📈 **{len(df_filtered)}** lignes affichées")
    
    # ========================================
    # CARTE 1 : CARTE DU MONDE - ORIGINE DES TOURISTES
    # ========================================
    st.header("🌍 Carte Mondiale - Origine des Touristes")
    
    # Mapping manuel des codes ISO3 pour les pays principaux
    iso3_mapping = {
        'Canada': 'CAN',
        'États-Unis': 'USA',
        'États-Unis (y compris Hawaii)': 'USA',
        'Mexique': 'MEX',
        'Brésil': 'BRA',
        'Argentine': 'ARG',
        'Chili': 'CHL',
        'Royaume-Uni': 'GBR',
        'Allemagne': 'DEU',
        'Italie': 'ITA',
        'Espagne': 'ESP',
        'Belgique': 'BEL',
        'Pays-Bas': 'NLD',
        'Suisse': 'CHE',
        'Chine': 'CHN',
        'Japon': 'JPN',
        'Corée du Sud': 'KOR',
        'Inde': 'IND',
        'Australie': 'AUS',
        'Nouvelle-Zélande': 'NZL',
        'Afrique du Sud': 'ZAF',
        'Maroc': 'MAR',
        'Tunisie': 'TUN',
        'Russie': 'RUS',
        'Turquie': 'TUR',
        'Arabie Saoudite': 'SAU',
        'Émirats Arabes Unis': 'ARE'
    }
    
    # Agrégation par pays
    df_pays = df_filtered.groupby('Pays', as_index=False).agg({
        'Nombre de touristes': 'sum',
        'Nuitées touristiques': 'sum',
        'Durée de séjour moyenne': 'mean'
    })
    
    # Ajouter les codes ISO3
    df_pays['ISO3'] = df_pays['Pays'].map(iso3_mapping)
    
    # Filtrer uniquement les pays avec ISO3 valide
    df_pays_valides = df_pays[df_pays['ISO3'].notna()].copy()
    
    if not df_pays_valides.empty:
        fig_monde = px.choropleth(
            df_pays_valides,
            locations='ISO3',
            color=indicateur,
            hover_name='Pays',
            hover_data={
                'ISO3': False,
                'Nombre de touristes': ':,.0f',
                'Nuitées touristiques': ':,.0f',
                'Durée de séjour moyenne': ':.1f'
            },
            color_continuous_scale='RdYlGn',
            title=f"{indicateur} par pays d'origine",
            labels={indicateur: indicateur}
        )
        
        fig_monde.update_layout(
            geo=dict(
                showframe=True,
                showcoastlines=True,
                projection_type='natural earth',
                bgcolor='rgba(240,240,240,0.5)'
            ),
            height=500,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig_monde, use_container_width=True)
    else:
        st.warning("⚠️ Aucun pays avec code ISO3 valide trouvé dans les données filtrées")
    
    # ========================================
    # CARTE 2 : SCATTER MAP - DÉTAIL PAR RÉGION
    # ========================================
    st.header("🎯 Carte Interactive - Régions d'origine")
    
    # Mapping manuel des coordonnées par région
    coords_regions = {
        'Europe': {'lat': 50, 'lon': 10},
        'Europe (hors France)': {'lat': 50, 'lon': 10},
        'Asie': {'lat': 35, 'lon': 105},
        'Amérique du Nord': {'lat': 45, 'lon': -100},
        'Amérique du Sud': {'lat': -15, 'lon': -60},
        'Amérique Centrale': {'lat': 15, 'lon': -90},
        'Afrique': {'lat': 0, 'lon': 20},
        'Océanie': {'lat': -25, 'lon': 135},
        'Moyen-Orient': {'lat': 30, 'lon': 45}
    }
    
    # Agrégation par région
    df_regions = df_filtered.groupby('Region', as_index=False).agg({
        'Nombre de touristes': 'sum',
        'Nuitées touristiques': 'sum',
        'Durée de séjour moyenne': 'mean'
    })
    
    # Ajouter les coordonnées
    df_regions['lat'] = df_regions['Region'].map(lambda x: coords_regions.get(x, {}).get('lat', 0))
    df_regions['lon'] = df_regions['Region'].map(lambda x: coords_regions.get(x, {}).get('lon', 0))
    
    # Supprimer les régions sans coordonnées
    df_regions = df_regions[df_regions['lat'] != 0]
    
    if not df_regions.empty:
        # Créer la carte scatter
        fig_scatter = px.scatter_geo(
            df_regions,
            lat='lat',
            lon='lon',
            size='Nombre de touristes',
            color=indicateur,
            hover_name='Region',
            hover_data={
                'lat': False,
                'lon': False,
                'Nombre de touristes': ':,.0f',
                'Nuitées touristiques': ':,.0f',
                'Durée de séjour moyenne': ':.1f'
            },
            color_continuous_scale='Viridis',
            size_max=50,
            title="Flux touristiques par région d'origine"
        )
        
        fig_scatter.update_layout(
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                coastlinecolor='rgb(204, 204, 204)',
                showocean=True,
                oceancolor='rgb(230, 245, 255)'
            ),
            height=500
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.warning("⚠️ Aucune région avec coordonnées valides")
    
    # ========================================
    # GRAPHIQUES DYNAMIQUES COMPLÉMENTAIRES
    # ========================================
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Top 10 Régions")
        
        # Sélecteur d'indicateur
        metric = st.selectbox(
            "Choisir l'indicateur",
            ["Nombre de touristes", "Nuitées touristiques"],
            key="metric_top10"
        )
        
        df_top = df_regions.nlargest(10, metric)
        
        fig_bar = px.bar(
            df_top,
            x=metric,
            y='Region',
            orientation='h',
            color=metric,
            color_continuous_scale='Blues',
            text=metric
        )
        
        fig_bar.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_bar.update_layout(showlegend=False, height=400)
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("🕐 Durée de Séjour Moyenne")
        
        df_duree = df_regions.sort_values('Durée de séjour moyenne', ascending=False).head(10)
        
        fig_duree = px.bar(
            df_duree,
            x='Durée de séjour moyenne',
            y='Region',
            orientation='h',
            color='Durée de séjour moyenne',
            color_continuous_scale='Oranges',
            text='Durée de séjour moyenne'
        )
        
        fig_duree.update_traces(texttemplate='%{text:.1f} jours', textposition='outside')
        fig_duree.update_layout(showlegend=False, height=400)
        
        st.plotly_chart(fig_duree, use_container_width=True)
    
    # ========================================
    # ÉVOLUTION TEMPORELLE INTERACTIVE
    # ========================================
    st.header("📈 Évolution Temporelle Interactive")
    
    if 'Mois' in df_filtered.columns:
        # Sélection multiple de régions
        regions_dispo = sorted(df_filtered['Region'].unique())
        regions_defaut = regions_dispo[:3] if len(regions_dispo) >= 3 else regions_dispo
        
        regions_selected = st.multiselect(
            "Sélectionnez les régions à comparer",
            options=regions_dispo,
            default=regions_defaut
        )
        
        if regions_selected:
            df_evolution = df_filtered[df_filtered['Region'].isin(regions_selected)]
            
            df_evolution_agg = df_evolution.groupby(
                ['Mois', 'Region'], 
                as_index=False
            )['Nombre de touristes'].sum()
            
            fig_line = px.line(
                df_evolution_agg,
                x='Mois',
                y='Nombre de touristes',
                color='Region',
                markers=True,
                title="Évolution du nombre de touristes",
                labels={'Nombre de touristes': 'Touristes (milliers)'}
            )
            
            fig_line.update_layout(
                hovermode='x unified',
                height=400,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("👆 Sélectionnez au moins une région pour voir l'évolution")
    
    # ========================================
    # KPIs DYNAMIQUES
    # ========================================
    st.header("📊 Indicateurs Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_touristes = df_filtered['Nombre de touristes'].sum()
    total_nuitees = df_filtered['Nuitées touristiques'].sum()
    nb_pays = df_filtered['Pays'].nunique()
    duree_moy = df_filtered['Durée de séjour moyenne'].mean()
    
    with col1:
        st.metric(
            "Total Touristes",
            f"{total_touristes/1000:.1f}M",
            help="Nombre total de touristes sur la période sélectionnée"
        )
    
    with col2:
        st.metric(
            "Total Nuitées",
            f"{total_nuitees/1000:.1f}M",
            help="Nombre total de nuitées touristiques"
        )
    
    with col3:
        st.metric(
            "Pays d'origine",
            nb_pays,
            help="Nombre de pays d'origine différents"
        )
    
    with col4:
        st.metric(
            "Durée moyenne",
            f"{duree_moy:.1f} j",
            help="Durée moyenne de séjour"
        )
    
    # ========================================
    # DONNÉES BRUTES AVEC FILTRE
    # ========================================
    with st.expander("📋 Voir les données brutes filtrées"):
        st.dataframe(
            df_filtered.sort_values('Nombre de touristes', ascending=False),
            use_container_width=True,
            height=400
        )
        
        # Bouton de téléchargement
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Télécharger les données (CSV)",
            data=csv,
            file_name='tourisme_filtre.csv',
            mime='text/csv'
        )