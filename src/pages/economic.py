# src/pages/economic.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def show_economic(df_dict):
    """
    Analyse de l'impact économique du tourisme international
    """
    st.title("💼 Impact Économique du Tourisme")
    st.markdown("Analyse des retombées économiques : nuitées, durée de séjour, intensité")
    
    # Récupération des données
    df_region = df_dict["frequentation_region"]
    df_hotel = df_dict.get("frequentation_hoteliere", df_region)
    
    # Conversion date
    if 'Mois' in df_region.columns:
        df_region['Mois'] = pd.to_datetime(df_region['Mois'])
    
    # ========================================
    # FILTRES
    # ========================================
    st.sidebar.title("🎛️ Filtres")
    
    regions_dispo = ['Tous'] + sorted(df_region['Region'].unique().tolist())
    region_filter = st.sidebar.selectbox("Région d'origine", regions_dispo)
    
    if region_filter != 'Tous':
        df_filtered = df_region[df_region['Region'] == region_filter].copy()
    else:
        df_filtered = df_region.copy()
    
    # ========================================
    # INDICATEURS ÉCONOMIQUES CLÉS
    # ========================================
    st.header("📊 Indicateurs Économiques Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_nuitees = df_filtered['Nuitées touristiques'].sum()
    total_touristes = df_filtered['Nombre de touristes'].sum()
    duree_moy = df_filtered['Durée de séjour moyenne'].mean()
    intensite = total_nuitees / total_touristes if total_touristes > 0 else 0
    
    with col1:
        st.metric(
            "🏨 Nuitées Totales",
            f"{total_nuitees/1000:.1f}M",
            help="Volume total de nuitées touristiques"
        )
    
    with col2:
        st.metric(
            "👥 Touristes",
            f"{total_touristes/1000:.1f}M",
            help="Nombre total d'arrivées"
        )
    
    with col3:
        st.metric(
            "⏱️ Séjour Moyen",
            f"{duree_moy:.1f} jours",
            help="Durée moyenne de séjour"
        )
    
    with col4:
        st.metric(
            "📈 Intensité",
            f"{intensite:.1f}",
            help="Nuitées par touriste (indicateur d'intensité économique)"
        )
    
    # ========================================
    # GRAPHIQUE : RATIO NUITÉES/TOURISTES
    # ========================================
    st.markdown("---")
    st.header("💰 Rentabilité Économique par Région")
    
    st.markdown("""
    **L'intensité économique** mesure le nombre de nuitées générées par touriste.  
    Plus ce ratio est élevé, plus l'impact économique est important.
    """)
    
    # Calcul par région
    df_ratio = df_filtered.groupby('Region', as_index=False).agg({
        'Nombre de touristes': 'sum',
        'Nuitées touristiques': 'sum',
        'Durée de séjour moyenne': 'mean'
    })
    
    df_ratio['Intensité économique'] = df_ratio['Nuitées touristiques'] / df_ratio['Nombre de touristes']
    df_ratio = df_ratio.sort_values('Intensité économique', ascending=False)
    
    # Graphique
    fig_ratio = px.bar(
        df_ratio,
        x='Intensité économique',
        y='Region',
        orientation='h',
        color='Intensité économique',
        color_continuous_scale='RdYlGn',
        text='Intensité économique',
        title="Intensité économique par région (nuitées/touriste)"
    )
    
    fig_ratio.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_ratio.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Nuitées par touriste"
    )
    
    st.plotly_chart(fig_ratio, use_container_width=True)
    
    # ========================================
    # SCATTER : VOLUME VS DURÉE
    # ========================================
    st.markdown("---")
    st.header("🎯 Volume vs Qualité du Séjour")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("""
        ### 📖 Interprétation
        
        **Quadrant supérieur droit** 🟢  
        → Volume ET durée élevés  
        → Marchés à fort potentiel
        
        **Quadrant supérieur gauche** 🟡  
        → Faible volume mais longue durée  
        → Marchés de niche à développer
        
        **Quadrant inférieur droit** 🟠  
        → Volume élevé mais courte durée  
        → Optimiser la durée de séjour
        
        **Quadrant inférieur gauche** 🔴  
        → Faible volume ET courte durée  
        → Marchés à faible priorité
        """)
    
    with col1:
        # Agrégation par pays
        df_scatter = df_filtered.groupby('Pays', as_index=False).agg({
            'Nombre de touristes': 'sum',
            'Durée de séjour moyenne': 'mean',
            'Nuitées touristiques': 'sum',
            'Region': 'first'
        })
        
        # Top 20 pays pour lisibilité
        df_scatter = df_scatter.nlargest(20, 'Nombre de touristes')
        
        fig_scatter = px.scatter(
            df_scatter,
            x='Nombre de touristes',
            y='Durée de séjour moyenne',
            size='Nuitées touristiques',
            color='Region',
            hover_name='Pays',
            hover_data={
                'Nombre de touristes': ':,.0f',
                'Nuitées touristiques': ':,.0f',
                'Durée de séjour moyenne': ':.1f'
            },
            title="Volume de touristes vs Durée moyenne de séjour",
            labels={
                'Nombre de touristes': 'Volume de touristes (milliers)',
                'Durée de séjour moyenne': 'Durée de séjour (jours)'
            }
        )
        
        # Lignes de référence
        median_touristes = df_scatter['Nombre de touristes'].median()
        median_duree = df_scatter['Durée de séjour moyenne'].median()
        
        fig_scatter.add_hline(
            y=median_duree, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Durée médiane"
        )
        fig_scatter.add_vline(
            x=median_touristes,
            line_dash="dash",
            line_color="gray",
            annotation_text="Volume médian"
        )
        
        fig_scatter.update_layout(height=500)
        
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # ========================================
    # ÉVOLUTION DE L'INTENSITÉ ÉCONOMIQUE
    # ========================================
    if 'Mois' in df_filtered.columns:
        st.markdown("---")
        st.header("📈 Évolution de l'Impact Économique")
        
        # Calcul mensuel
        df_monthly = df_filtered.groupby('Mois', as_index=False).agg({
            'Nombre de touristes': 'sum',
            'Nuitées touristiques': 'sum',
            'Durée de séjour moyenne': 'mean'
        })
        
        df_monthly['Intensité'] = df_monthly['Nuitées touristiques'] / df_monthly['Nombre de touristes']
        
        # Graphique double axe
        fig_evolution = go.Figure()
        
        # Nuitées (axe gauche)
        fig_evolution.add_trace(go.Bar(
            x=df_monthly['Mois'],
            y=df_monthly['Nuitées touristiques'],
            name='Nuitées',
            marker_color='lightblue',
            yaxis='y'
        ))
        
        # Intensité (axe droit)
        fig_evolution.add_trace(go.Scatter(
            x=df_monthly['Mois'],
            y=df_monthly['Intensité'],
            name='Intensité économique',
            line=dict(color='red', width=3),
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig_evolution.update_layout(
            title="Évolution des nuitées et de l'intensité économique",
            xaxis_title="Mois",
            yaxis=dict(title="Nuitées (milliers)", side='left'),
            yaxis2=dict(title="Intensité (nuitées/touriste)", side='right', overlaying='y'),
            hovermode='x unified',
            height=400,
            legend=dict(x=0.01, y=0.99)
        )
        
        st.plotly_chart(fig_evolution, use_container_width=True)
    
    # ========================================
    # CLASSEMENT PAR IMPACT ÉCONOMIQUE
    # ========================================
    st.markdown("---")
    st.header("🏆 Classement par Impact Économique")
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        critere = st.radio(
            "Critère de classement",
            ["Nuitées totales", "Intensité économique", "Durée de séjour"]
        )
        
        top_n = st.slider("Nombre de pays", 5, 20, 10)
    
    with col_b:
        # Mapping des critères
        critere_map = {
            "Nuitées totales": "Nuitées touristiques",
            "Intensité économique": "Intensité économique",
            "Durée de séjour": "Durée de séjour moyenne"
        }
        
        col_sort = critere_map[critere]
        
        # Préparation données
        df_classement = df_filtered.groupby('Pays', as_index=False).agg({
            'Nombre de touristes': 'sum',
            'Nuitées touristiques': 'sum',
            'Durée de séjour moyenne': 'mean'
        })
        
        df_classement['Intensité économique'] = (
            df_classement['Nuitées touristiques'] / df_classement['Nombre de touristes']
        )
        
        df_top = df_classement.nlargest(top_n, col_sort)
        
        fig_classement = px.bar(
            df_top.sort_values(col_sort, ascending=True),
            x=col_sort,
            y='Pays',
            orientation='h',
            color=col_sort,
            color_continuous_scale='Viridis',
            text=col_sort,
            title=f"Top {top_n} pays - {critere}"
        )
        
        fig_classement.update_traces(
            texttemplate='%{text:,.1f}',
            textposition='outside'
        )
        fig_classement.update_layout(showlegend=False, height=450)
        
        st.plotly_chart(fig_classement, use_container_width=True)
    
    # ========================================
    # ANALYSE COMPARATIVE
    # ========================================
    st.markdown("---")
    st.header("⚖️ Analyse Comparative")
    
    st.markdown("Comparez l'impact économique de différents marchés")
    
    pays_dispo = sorted(df_filtered['Pays'].unique())
    pays_comparer = st.multiselect(
        "Sélectionnez des pays à comparer",
        options=pays_dispo,
        default=pays_dispo[:5] if len(pays_dispo) >= 5 else pays_dispo
    )
    
    if pays_comparer:
        df_compare = df_filtered[df_filtered['Pays'].isin(pays_comparer)]
        
        df_compare_agg = df_compare.groupby('Pays', as_index=False).agg({
            'Nombre de touristes': 'sum',
            'Nuitées touristiques': 'sum',
            'Durée de séjour moyenne': 'mean'
        })
        
        # Graphique en barres groupées
        fig_compare = go.Figure()
        
        fig_compare.add_trace(go.Bar(
            name='Touristes (milliers)',
            x=df_compare_agg['Pays'],
            y=df_compare_agg['Nombre de touristes'],
            marker_color='lightblue'
        ))
        
        fig_compare.add_trace(go.Bar(
            name='Nuitées (milliers)',
            x=df_compare_agg['Pays'],
            y=df_compare_agg['Nuitées touristiques'],
            marker_color='lightcoral'
        ))
        
        fig_compare.update_layout(
            title="Comparaison : Touristes vs Nuitées",
            barmode='group',
            height=400,
            xaxis_title="",
            yaxis_title="Volume (milliers)"
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)
        
        # Tableau récapitulatif
        st.subheader("📋 Tableau récapitulatif")
        
        df_compare_agg['Intensité'] = (
            df_compare_agg['Nuitées touristiques'] / df_compare_agg['Nombre de touristes']
        )
        
        st.dataframe(
            df_compare_agg.style.format({
                'Nombre de touristes': '{:,.0f}',
                'Nuitées touristiques': '{:,.0f}',
                'Durée de séjour moyenne': '{:.1f}',
                'Intensité': '{:.1f}'
            }),
            use_container_width=True
        )
    
    # ========================================
    # INSIGHTS STRATÉGIQUES
    # ========================================
    st.markdown("---")
    st.header("💡 Insights Stratégiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pays à plus forte intensité
        df_top_intensite = df_classement.nlargest(3, 'Intensité économique')
        
        st.success(f"""
        **🎯 Marchés à forte intensité économique**
        
        Ces pays génèrent le plus de nuitées par touriste :
        
        {chr(10).join([f"- **{row['Pays']}** : {row['Intensité économique']:.1f} nuitées/touriste" 
                       for _, row in df_top_intensite.iterrows()])}
        
        → Priorité : fidéliser ces marchés
        """)
    
    with col2:
        # Pays à améliorer
        df_faible_duree = df_classement[
            df_classement['Nombre de touristes'] > df_classement['Nombre de touristes'].median()
        ].nsmallest(3, 'Durée de séjour moyenne')
        
        if not df_faible_duree.empty:
            st.warning(f"""
            **📊 Marchés à potentiel d'amélioration**
            
            Ces marchés ont du volume mais une courte durée :
            
            {chr(10).join([f"- **{row['Pays']}** : {row['Durée de séjour moyenne']:.1f} jours" 
                           for _, row in df_faible_duree.iterrows()])}
            
            → Opportunité : allonger les séjours
            """)