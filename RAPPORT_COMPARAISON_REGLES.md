# 📋 Rapport de Comparaison des Règles

## Analyse : Règles du fichier "Untitled" vs Implémentation actuelle

---

## ✅ **PARTIE 1 : Règles d'identification des documents (OCR)**

### État actuel
Les règles d'identification sont définies dans `ony_/backend/app/services/analyzer.py` (lignes 45-162).

### Comparaison avec le fichier "Untitled"

#### ✅ **Déjà implémentées** (mais incomplètes)

| DocumentType | Mots-clés manquants dans le projet |
|--------------|-----------------------------------|
| **CERFA** | ❌ "demande de permis d'aménager", "permis d'aménager" |
| **PC1** | ❌ "références cadastrales", "parcelle cadastrale" |
| **PC2** | ✅ Tous les mots-clés sont présents |
| **PC3** | ❌ "profil du terrain naturel" |
| **PC4** | ❌ "notice décrivant le terrain et le projet", "courte description du projet" |
| **PC5** | ❌ "plan des façades et des toitures" |
| **PC6** | ✅ Tous les mots-clés sont présents |
| **PC7** | ❌ "photographie environnement proche" |
| **PC8** | ❌ "photographie paysage lointain" |
| **AVIS_EP** | ❌ "loi sur l'eau" |
| **AVIS_DEA** | ❌ "installations individuelles d'assainissement" |

### 📝 **Recommandation**
Mettre à jour `IDENTIFICATION_RULES` dans `analyzer.py` avec les mots-clés supplémentaires du fichier "Untitled" pour améliorer la détection.

---

## ⚠️ **PARTIE 2 : Règles de conformité pour projets < 240 m²**

### État actuel
- Le fichier `rules.yml` définit un profil `small` mais **tous les champs sont commentés**.
- Le `ComplianceEngine` vérifie seulement la présence de champs/documents, **pas les calculs ni les règles métier**.

### Règles du fichier "Untitled" (lignes 1-15)

#### ❌ **NON IMPLÉMENTÉES**

1. **Formulaire d'instruction des projets** ✅ (déjà détecté via CERFA)
2. **Plan de masse** ✅ (déjà détecté via PC2)
3. **Vérification du calcul de surface imperméabilisée** ❌
   - Formule : `surface imperméabilisée = surface des toitures non végétalisées + surface des stationnements, voiries et accès imperméabilisés + surface des terrasses sur support imperméable + surface des stationnements perméables sur support imperméables`
4. **Cartographie du ruissellement** ❌ (document non détecté)
5. **Test d'infiltration** ❌ (présence non vérifiée)
6. **Calcul du volume à mettre en œuvre** ❌
   - **Si test d'infiltration OUI** : `Volume = Surface imperméable × 0,045 – Surface d'infiltration × Vitesse d'infiltration × 0,002`
   - **Si test d'infiltration NON** : `Volume = Surface imperméable × 0,045`
   - **Vérification** : Volume doit être ≥ `0,015 m³/m² imperméabilisé`

### 📝 **Recommandation**
Ajouter ces règles dans `ComplianceEngine.evaluate()` avec des calculs et validations.

---

## ⚠️ **PARTIE 3 : Règles de conformité pour projets ≥ 240 m²**

### État actuel
- Le fichier `rules.yml` définit un profil `big` mais **tous les champs sont commentés**.
- Aucune validation des règles spécifiques aux gros projets.

### Règles du fichier "Untitled" (lignes 16-28)

#### ❌ **NON IMPLÉMENTÉES**

1. **Note de calcul DEA** ❌ (document non détecté)
2. **Plan de masse** ✅ (déjà détecté via PC2)
3. **Test de perméabilité de type Matsuo** ❌ (présence non vérifiée)
4. **Rétention de pluie > 15 mm pour pluies courantes** ❌
5. **Rétention de pluie > 45 mm pour pluies moyennes à fortes** ❌
6. **Calcul du volume à mettre en œuvre** ❌
   - Formule : `Surface imperméable × 0,045 – Surface d'infiltration × Vitesse d'infiltration × 0,002`
   - Vérification : Volume doit être ≥ `0,015 m³/m² imperméabilisé`

### 📝 **Recommandation**
Implémenter ces validations dans `ComplianceEngine` avec des règles conditionnelles selon la taille du projet.

---

## ❌ **PARTIE 4 : Règles complètes de la Notice – Zonage pluvial**

### État actuel
**AUCUNE** des 43 règles détaillées (lignes 149-253 du fichier "Untitled") n'est implémentée.

### Règles manquantes par catégorie

#### **1. Champ d'application** (2 règles)
- ❌ Application uniquement aux "eaux pluviales strictes"
- ❌ Application à tout aménagement modifiant l'écoulement

#### **2. Règles communes** (4 règles)
- ❌ Dispositifs séparatifs (sans connexion eaux usées)
- ❌ Dispositifs spécifiques pour surfaces à risque de pollution
- ❌ Entretien approprié + cahier d'entretien
- ❌ Interdiction débourbeurs-déshuileurs pour pollution chronique

#### **3. Seuil petits/gros projets** (3 règles)
- ✅ Seuil 240 m² (déjà utilisé pour `is_small_project`)
- ❌ Démontrer impossibilité technique pour petits projets

#### **4. Gros projets - Pluies courantes** (5 règles)
- ❌ Infiltration/évapotranspiration à la source
- ❌ Espace dédié ≥ 15 L/m² imperméabilisé
- ❌ Solutions de faible profondeur (< 1 m)
- ❌ Puits d'infiltration non appropriés pour pluies courantes
- ❌ Application sur chaque lot dans opérations d'ensemble

#### **5. Gros projets - Pluies moyennes à fortes** (3 règles)
- ❌ Principe "zéro rejet" (infiltration)
- ❌ Dérogation avec débit de rejet régulé
- ❌ Gestion imperméabilisation supplémentaire dans opérations d'ensemble

#### **6. Gros projets - Exigences de conception** (4 règles)
- ❌ Fonctionnement gravitaire + entretien aisé
- ❌ Interdiction raccordements surverses sur ouvrages publics enterrés
- ❌ Interdiction puits d'infiltration pour voiries
- ❌ Conditions pour puits d'infiltration (3 conditions)

#### **7. Gros projets - Tests d'infiltration** (3 règles)
- ❌ Tests d'infiltration représentatifs obligatoires
- ❌ Conditions de représentativité
- ❌ Tests comme condition pour dérogation

#### **8. Gros projets - Dérogation + rejet régulé** (4 règles)
- ❌ Conditions d'autorisation rejet régulé
- ❌ Débit max = 5 L/s/ha (ou 1 L/s minimum)
- ❌ Application à l'échelle opération pour lots individuels

#### **9. Gros projets - Dimensionnement** (3 règles)
- ❌ Méthode des pluies
- ❌ Coefficients de ruissellement (1, 0,5, 0,2, 0)
- ❌ Période de retour d'insuffisance minimale : 30 ans

#### **10. Gros projets - Pluies exceptionnelles** (2 règles)
- ❌ Anticipation conséquences pluies exceptionnelles
- ❌ Interdiction raccordements surverses sur ouvrages publics enterrés

#### **11. Petits projets - Règles générales** (5 règles)
- ❌ Infiltration des écoulements
- ❌ Minimiser conséquences pluies exceptionnelles
- ❌ Interdiction raccordements surverses
- ❌ Fonctionnement gravitaire (relevage interdit)
- ❌ Conditions pour puits d'infiltration

#### **12. Petits projets - Dimensionnement** (3 règles)
- ✅ Formule sans test : `Volume = Surface × 0,045` (mentionnée dans "Untitled")
- ✅ Formule avec test : `Volume = Surface × 0,045 – Surface infiltration × Vitesse × 0,002` (mentionnée)
- ✅ Volume minimum : `0,015 m³/m²` (mentionné)

#### **13. Autres règles spécifiques** (2 règles)
- ❌ Extensions : règles appliquées à surface extension + 50%
- ❌ Busage de fossés interdit sans autorisation

---

## 📊 **Résumé global**

| Catégorie | État | Pourcentage |
|-----------|------|-------------|
| **Règles d'identification OCR** | ⚠️ Partiellement implémentées | ~70% |
| **Règles projets < 240 m²** | ❌ Non implémentées | ~10% |
| **Règles projets ≥ 240 m²** | ❌ Non implémentées | ~5% |
| **Règles complètes Notice** | ❌ Non implémentées | ~0% |

---

## 🎯 **Actions recommandées par priorité**

### **Priorité 1 : Règles essentielles**
1. ✅ Mettre à jour `IDENTIFICATION_RULES` avec les mots-clés manquants
2. ✅ Implémenter les calculs de volume pour petits et gros projets
3. ✅ Vérifier la présence de documents spécifiques (cartographie ruissellement, note de calcul DEA, test infiltration/Matsuo)

### **Priorité 2 : Validations métier**
4. ✅ Ajouter validation surface imperméabilisée (formule complète)
5. ✅ Ajouter validation rétention pluie (15 mm et 45 mm)
6. ✅ Ajouter validation volume minimum (0,015 m³/m²)

### **Priorité 3 : Règles avancées**
7. ⚠️ Implémenter les règles communes (dispositifs séparatifs, entretien, etc.)
8. ⚠️ Implémenter les règles de dimensionnement avancées (méthode des pluies, coefficients)
9. ⚠️ Implémenter les règles de dérogation et rejet régulé


