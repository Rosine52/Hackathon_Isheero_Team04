# Hackathon iSHEERO × DataCamp 2026 — Bénin Insights Challenge

## Modèle de Classification de Sentiment (Corrigé - J4)

Ce document décrit le modèle de classification de sentiment développé pour le challenge Bénin Insights, après la correction des fuites de données identifiées dans la version J3.

### 1. Contexte et Correction des Fuites de Données

La version précédente du modèle (J3) présentait des scores de performance irréalistes (F1=1.000, AUC=1.000). Après analyse, trois fuites de données majeures ont été identifiées et corrigées :


- AvgTone_scaled retiré : transformation directe de la cible
- tension_score_scaled retiré : contenait abs(AvgTone)
- sentiment_tb_score retiré : simulé depuis AvgTone / 10 + bruit

Ces corrections garantissent que le modèle apprend à partir de signaux réels et non de "réponses" cachées dans les features.

### 2. Modèle et Caractéristiques

*   **Type de Modèle :** RandomForestClassifier
*   **Version :** J4_corrige
*   **Nombre de Features utilisées :** 9
*   **Features Nettoyées :** GoldsteinScale_scaled, tension_score_v2_scaled, media_intensity_scaled, NumMentions_scaled, EventRootCode_enc, Actor1Type1Code_enc, Actor1CountryCode_enc, QuadClass, month

**Hyperparamètres du Modèle (Optimisés via RandomizedSearchCV) :**

  - class_weight: balanced
  - max_depth: 15
  - max_features: log2
  - min_samples_leaf: 1
  - min_samples_split: 5
  - n_estimators: 393

### 3. Performances sur le Jeu de Test

Les métriques suivantes ont été obtenues sur un jeu de test indépendant, après que toutes les fuites de données aient été corrigées. Elles représentent une évaluation plus réaliste des capacités du modèle.

*   **Accuracy :** 0.6028
*   **F1-Weighted :** 0.6033
*   **Precision-Weighted :** 0.6143
*   **Recall-Weighted :** 0.6028
*   **AUC-ROC (macro OvR) :** 0.7768

### 4. Cross-Validation (sur le jeu d'entraînement)

*   **Nombre de Folds :** 5
*   **F1-Weighted Moyen (CV) :** 0.5674
*   **Écart-type F1 (CV) :** 0.0148
*   **Écart F1 (Test vs CV) :** 0.0359 (Indicateur d'overfitting/généralisation)

### 5. Interprétation et Prochaines Étapes

Le F1-weighted de 0.6033 est un score réaliste pour la classification de sentiment sur des données GDELT structurelles, sans accès direct au texte brut des articles. Il reflète une capacité d'apprentissage authentique du modèle, maintenant que les fuites de données ont été éliminées.

Ce résultat est honnête et constitue une base solide pour d'éventuelles améliorations, telles que l'intégration de données textuelles si elles deviennent disponibles ou l'exploration de cibles de classification alternatives.

