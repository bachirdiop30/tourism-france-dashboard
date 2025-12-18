# src/pages/home.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_home(df_dict):
    """
    Page d'accueil présentant le contexte et les indicateurs clés
    """
    st.title("🏖️ Tourisme International en France")
    st.markdown("### Dashboard d'analyse des flux touristiques et de leur impact économique")
    
    # ========================================
    # SECTION 1 : CONTEXTE ET OBJECTIF
    # ========================================
    with st.expander("📖 Contexte et objectif du projet", expanded=True):
        st.markdown("""
        ### 🎯 Objectif
        
        Ce dashboard analyse **le tourisme international en France** pour éclairer les décideurs publics 
        et les acteurs du secteur sur :
        
        - **L'origine géographique** des touristes (pays, régions du monde)
        - **L'évolution temporelle** des flux touristiques
        - **L'impact économique** (nuitées, durée de séjour)
        - **Les tendances** et opportunités de développement
        
        ### 🏛️ Intérêt public
        
        **Pour les collectivités territoriales :**
        - Planifier les infrastructures touristiques
        - Adapter les services publics aux pics de fréquentation
        - Développer des partenariats internationaux ciblés
        
        **Pour les acteurs économiques :**
        - Optimiser l'offre hôtelière et touristique
        - Identifier les marchés prioritaires
        - Anticiper les fluctuations saisonnières
        
        **Pour les politiques publiques :**
        - Élaborer des stratégies d'attractivité
        - Gérer les flux et leur impact environnemental
        - Valoriser le patrimoine français à l'international
        
        ### 📊 Source des données
        
        Données Open Data de fréquentation touristique en France (2024-2025)
        - Granularité mensuelle
        - Ventilation par pays et région d'origine
        - Indicateurs : arrivées, nuitées, durée de séjour
        """)
    
    # ========================================
    # SECTION 2 : CHIFFRES CLÉS
    # ========================================
    st.markdown("---")
    st.header("📊 Indicateurs Clés - Vue d'ensemble")
    
    # Récupération des données
    df_region = df_dict["frequentation_region"]
    
    # Conversion date si nécessaire
    if 'Mois' in df_region.columns:
        df_region['Mois'] = pd.to_datetime(df_region['Mois'])
    
    # Calcul des KPIs
    total_touristes = df_region['Nombre de touristes'].sum()
    total_nuitees = df_region['Nuitées touristiques'].sum()
    duree_moyenne = df_region['Durée de séjour moyenne'].mean()
    nb_pays = df_region['Pays'].nunique()
    nb_regions = df_region['Region'].nunique()
    
    # Affichage des métriques
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "🌍 Total Touristes",
            f"{total_touristes/1000:.1f}M",
            help="Nombre total d'arrivées de touristes internationaux"
        )
    
    with col2:
        st.metric(
            "🏨 Total Nuitées",
            f"{total_nuitees/1000:.1f}M",
            help="Nombre total de nuitées en hébergements touristiques"
        )
    
    with col3:
        st.metric(
            "⏱️ Séjour Moyen",
            f"{duree_moyenne:.1f} jours",
            help="Durée moyenne de séjour des touristes"
        )
    
    with col4:
        st.metric(
            "🗺️ Pays d'origine",
            nb_pays,
            help="Nombre de pays sources de touristes"
        )
    
    with col5:
        st.metric(
            "📍 Régions",
            nb_regions,
            help="Nombre de régions du monde représentées"
        )
    
    # ========================================
    # SECTION 3 : GRAPHIQUES DE SYNTHÈSE
    # ========================================
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("🌐 Répartition par Région du Monde")
        
        # Agrégation par région
        df_region_agg = df_region.groupby('Region', as_index=False).agg({
            'Nombre de touristes': 'sum'
        })
        df_region_agg = df_region_agg.sort_values('Nombre de touristes', ascending=False)
        
        # Graphique en barres horizontales
        fig_regions = px.bar(
            df_region_agg,
            x='Nombre de touristes',
            y='Region',
            orientation='h',
            color='Nombre de touristes',
            color_continuous_scale='Viridis',
            text='Nombre de touristes',
            title="Nombre de touristes par région d'origine"
        )
        
        fig_regions.update_traces(
            texttemplate='%{text:,.0f}k',
            textposition='outside'
        )
        fig_regions.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Nombre de touristes (milliers)",
            yaxis_title=""
        )
        
        st.plotly_chart(fig_regions, use_container_width=True)
    
    with col_right:
        st.subheader("🥇 Top 10 Pays")
        
        # Top 10 pays
        df_pays = df_region.groupby('Pays', as_index=False).agg({
            'Nombre de touristes': 'sum'
        })
        df_top10 = df_pays.nlargest(10, 'Nombre de touristes')
        
        fig_top10 = px.bar(
            df_top10.sort_values('Nombre de touristes', ascending=True),
            x='Nombre de touristes',
            y='Pays',
            orientation='h',
            color='Nombre de touristes',
            color_continuous_scale='Plasma',
            text='Nombre de touristes',
            title="Top 10 des pays émetteurs"
        )
        
        fig_top10.update_traces(
            texttemplate='%{text:,.0f}k',
            textposition='outside'
        )
        fig_top10.update_layout(
            showlegend=False,
            height=400,
            xaxis_title="Nombre de touristes (milliers)",
            yaxis_title=""
        )
        
        st.plotly_chart(fig_top10, use_container_width=True)
    
    # ========================================
    # SECTION 4 : ÉVOLUTION TEMPORELLE
    # ========================================
    if 'Mois' in df_region.columns:
        st.markdown("---")
        st.subheader("📈 Évolution Temporelle du Tourisme")
        
        # Agrégation mensuelle
        df_monthly = df_region.groupby('Mois', as_index=False).agg({
            'Nombre de touristes': 'sum',
            'Nuitées touristiques': 'sum'
        })
        
        # Graphique d'évolution
        fig_evolution = go.Figure()
        
        fig_evolution.add_trace(go.Scatter(
            x=df_monthly['Mois'],
            y=df_monthly['Nombre de touristes'],
            mode='lines+markers',
            name='Touristes',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        
        fig_evolution.update_layout(
            title="Évolution mensuelle des arrivées touristiques",
            xaxis_title="Mois",
            yaxis_title="Nombre de touristes (milliers)",
            hovermode='x unified',
            height=400,
            template='plotly_white'
        )
        
        st.plotly_chart(fig_evolution, use_container_width=True)
        
        # Analyse de tendance
        col_a, col_b = st.columns(2)
        
        with col_a:
            # Mois le plus fort
            mois_max = df_monthly.loc[df_monthly['Nombre de touristes'].idxmax()]
            st.info(f"""
            **📅 Pic de fréquentation**  
            {mois_max['Mois'].strftime('%B %Y')} : **{mois_max['Nombre de touristes']:,.0f}k** touristes
            """)
        
        with col_b:
            # Croissance
            if len(df_monthly) > 1:
                first_value = df_monthly.iloc[0]['Nombre de touristes']
                last_value = df_monthly.iloc[-1]['Nombre de touristes']
                growth = ((last_value - first_value) / first_value) * 100
                
                st.info(f"""
                **📊 Évolution sur la période**  
                {growth:+.1f}% entre {df_monthly.iloc[0]['Mois'].strftime('%B %Y')} et {df_monthly.iloc[-1]['Mois'].strftime('%B %Y')}
                """)
    
    # ========================================
    # SECTION 5 : QUESTIONS CLÉS ÉCLAIRÉES
    # ========================================
    st.markdown("---")
    st.header("🔍 Questions clés éclairées par ce dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🌍 Origine des flux
        - Quels sont les principaux marchés émetteurs ?
        - Comment se répartissent les touristes par continent ?
        - Quels pays émergent comme nouveaux marchés ?
        
        ### 📈 Tendances temporelles
        - Quelle est la saisonnalité du tourisme ?
        - Observe-t-on une croissance ou un déclin ?
        - Quels sont les pics et creux de fréquentation ?
        """)
    
    with col2:
        st.markdown("""
        ### 💰 Impact économique
        - Quel est le volume de nuitées générées ?
        - Quelle est la durée moyenne de séjour par marché ?
        - Quels touristes restent le plus longtemps ?
        
        ### 🎯 Opportunités stratégiques
        - Quels marchés développer en priorité ?
        - Comment mieux répartir les flux touristiques ?
        - Comment allonger la durée moyenne des séjours ?
        """)
    
    # ========================================
    # SECTION 6 : NAVIGATION
    # ========================================
    st.markdown("---")
    st.header("🧭 Explorer le Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        ### 🗺️ Régions
        Cartes interactives montrant l'origine géographique des touristes
        """)
    
    with col2:
        st.info("""
        ### 🌍 International
        Analyse détaillée par pays avec comparaisons et évolutions
        """)
    
    with col3:
        st.info("""
        ### 💼 Économie
        Impact économique : nuitées, durée de séjour, retombées
        """)
    
    st.success("👈 Utilisez le menu de navigation à gauche pour explorer les analyses détaillées")