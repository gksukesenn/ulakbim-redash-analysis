# Makale vektörleri keşifsel kümeleme özeti

- Toplam makale sayısı: **24**
- Kullanılan embedding modeli: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Qdrant uzaklık/benzerlik yöntemi: **Cosine** (cosine benzerliği, vektörlerin yönsel yakınlığını karşılaştırır).
- Kümeleme: KMeans, `k=3`, `random_state=42`, `n_init=10`.
- PCA açıklanan varyans: PC1 **23.86%**, PC2 **13.98%**, toplam **37.85%**.
- KMeans inertia (küme içi kareler toplamı): **7.615551**.

## Yöntem

PCA, 384 boyutlu embedding vektörlerindeki varyansı mümkün olduğunca koruyarak iki görsel eksene indirger. KMeans ise vektör uzayında Öklid uzaklığına göre noktaları üç küme merkezine atar. PCA yalnızca görselleştirme için kullanılmış; KMeans özgün embedding vektörleri üzerinde çalıştırılmıştır. Sonuçlar keşifseldir ve ground truth etiketi olarak yorumlanmamalıdır.

## Kümeler

### Küme 0 — 8 makale

- `WOS:001149960200001` — Applications of artificial neural network based battery management systems: A literature review
- `WOS:001144493500001` — Crystallinity tuning of LCNO/graphene nanocomposite cathode for high-performance lithium-ion batteries
- `WOS:001163332000001` — Gellan gum/PEDOT:PSS gel electrolyte and application on quasi-solid dye sensitized solar cells
- `WOS:001168109200001` — High-performance Na-ion full-cells with P2-type Na<sub>0.67</sub>Mn<sub>0.5-x</sub>Ni<sub>x</sub>Fe<sub>0.43</sub>Al<sub>0.07</sub>O<sub>2</sub> cathodes: Cost analysis for stationary battery storage systems
- `WOS:001143201300001` — Incorporating Gadolinium Oxide (Gd<sub>2</sub>O<sub>3</sub>) as a Rare Earth Metal Oxide in Carbon Nanofiber Skeleton for Supercapacitor Application
- `WOS:001168628400001` — Simulation and forecasting of power by energy harvesting method in photovoltaic panels using artificial neural network
- `WOS:001165771600001` — The effect of outer container geometry on the thermal management of lithium-ion batteries with a combination of phase change material and metal foam
- `WOS:001140575800001` — Understanding the role of water in the lyotropic liquid crystalline mesophase of high-performance flexible supercapacitor electrolytes using a rheological approach

### Küme 1 — 8 makale

- `WOS:001142171500001` — Biological Markers in Newly Diagnosed Generalized Anxiety Disorder Patients: 8-OHdG, S100B and Oxidative Stress
- `WOS:001157724100001` — Depression and life satisfaction after Kahramanmaraş earthquakes: The serial mediation roles of life meaning and coping with earthquake stress
- `WOS:001154920600001` — Effect of online health training/counseling and progressive muscle relaxation exercise on postpartum depression and maternal attachment: A randomized controlled trial
- `WOS:001163480800004` — Effects of a Mindfulness-Based Stress Reduction Program on Stress, Depression, and Psychological Well-being in Patients With Cancer
- `WOS:001148762500002` — Exploring adult attachment and anxiety: the role of intolerance of uncertainty and social support
- `WOS:001182798400001` — Multitask Learning for Mental Health: Depression, Anxiety, Stress (DAS) Using Wearables
- `WOS:001157189800001` — Predictors, moderators and mediators of psychological therapies for perinatal depression in low- and middle-income countries: a systematic review
- `WOS:001129852800002` — The effect of occupational therapy on anxiety, depression, and psychological well-being in older adults: a single-blind randomized-controlled study

### Küme 2 — 8 makale

- `WOS:001140573400001` — Acetate-based ionic liquid engineering for efficient and stable CsPbI<sub>2</sub>Br perovskite solar cells with an unprecedented fill factor over 83%
- `WOS:001143809700001` — Constructing Charge Bridge Path for High-Performance Tin Perovskite Photovoltaics
- `WOS:001167231700001` — Incorporation Mechanism of Potassium in FAPbI<sub>3</sub> Perovskite Solar Cell Materials
- `WOS:001173733800001` — Ion-Migration Inhibitor for Spiro-OMeTAD/Perovskite Contact toward Stable Perovskite Solar Cells
- `WOS:001131514500001` — Magnetic-biased chiral molecules enabling highly oriented photovoltaic perovskites
- `WOS:001178378200001` — Molecular modification of spiro[fluorene-9,9′-xanthene]-based dopant-free hole transporting materials for perovskite solar cells
- `WOS:001191208900001` — Molecularly Engineered Multifunctional Bridging Layer Derived from Dithiafulavene Capped Spiroxanthene for Stable and Efficient Perovskite Solar Cells
- `WOS:001158980200001` — Synergistic Effects of Energy Level Alignment and Trap Passivation via 3,4-Dihydroxyphenethylamine Hydrochloride for Efficient and Air-Stable Perovskite Solar Cells
