# Proje veri akışları

Bu diyagramlarda yalnız gerçek dosya, sınıf ve fonksiyon adları kullanılmıştır.

## JSON → MongoDB → Redash

```mermaid
flowchart TD
    A["data/raw/ulakbim_ubyt_wos_records.json"]
    B["infrastructure/json_reader.py<br/>iter_publications()<br/>ijson.items prefix:<br/>item.Data.Records.records.REC.item"]
    C["infrastructure/publication_mapper.py<br/>map_publication()"]
    D["domain/publication.py<br/>Publication"]
    E["application/import_publications.py<br/>import_publications()<br/>import_publication_records()"]
    F["application/publication_repository.py<br/>PublicationRepository Protocol"]
    G["infrastructure/mongodb_repository.py<br/>MongoDBRepository.upsert_publications()"]
    H["MongoDB<br/>ulakbim_analysis.publications<br/>uid_unique index"]
    I["docs/redash_queries/01..07.json<br/>MongoDB aggregations"]
    J["Redash MongoDB data source<br/>manuel kurulum: docs/redash_queries/README.md"]
    K["Redash grafik/dashboard<br/>canlı metadata repository'de yok"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J --> K
```

**[DOĞRULANDI]** Yazma composition root'u `ulakbim_analysis.main._run_import`;
indexi oluşturur, sonra application use case'ini concrete Mongo adapter ile
çalıştırır (`main.py:121-145`).

## Makale seçimi → embedding → Qdrant

```mermaid
flowchart TD
    A["data/raw/ulakbim_ubyt_wos_records.json"]
    B["json_reader.iter_publications()"]
    C["application/vector_experiment_selection.py<br/>SELECTIONS: 24 sabit UID<br/>select_experiment_articles()"]
    D{"abstract mevcut ve<br/>abstract_is_suspicious == false?"}
    E["domain/vector_experiment.py<br/>ExperimentArticle"]
    F["application/vector_experiment.py<br/>build_embedding_text()<br/>Başlık + Abstract"]
    G["infrastructure/local_embedding.py<br/>FastEmbedModel<br/>TextEmbedding.embed()"]
    H["domain/vector_experiment.py<br/>VectorPoint"]
    I["application/vector_experiment.py<br/>build_payload()"]
    J["infrastructure/qdrant_vector_store.py<br/>recreate_collection()"]
    K["uuid5(NAMESPACE_URL, uid)<br/>PointStruct"]
    L["QdrantVectorStore.upsert()"]
    M["Qdrant<br/>ulakbim_article_similarity_experiment<br/>384 / Cosine / 24 point"]

    A --> B --> C --> D
    D -- Evet --> E --> F --> G --> H
    E --> I --> H
    H --> J --> K --> L --> M
    D -- Hayır --> N["Atla"]
```

**[DOĞRULANDI]** `load_vector_experiment.main` bu yazma akışını çağırır.
`run_vector_experiment.main` önce aynı load'u, sonra similarity raporunu çağırır.
`recreate_collection` var olan collection'ı siler; bu nedenle audit sırasında bu
iki komut çalıştırılmamıştır.

## Qdrant → KMeans → PCA → raporlar

```mermaid
flowchart TD
    A["Qdrant 24 mevcut point"]
    B["infrastructure/qdrant_vector_store.py<br/>read_all_articles()<br/>scroll limit=100 + offset"]
    C["domain/vector_experiment.py<br/>StoredArticleVector"]
    D["application/cluster_article_vectors.py<br/>vectors = 384B özgün vektörler"]
    E["sklearn.decomposition.PCA<br/>n_components=2<br/>fit_transform(vectors)"]
    F["sklearn.cluster.KMeans<br/>k=3, random_state=42, n_init=10<br/>fit_predict(vectors)"]
    G["ClusterAssignment<br/>UID, title, label, pca_x, pca_y"]
    H["write_assignments_csv()"]
    I["write_summary()"]
    J["write_pca_plot()"]
    K["reports/article_cluster_assignments.csv"]
    L["reports/article_cluster_summary.md"]
    M["reports/article_clusters_pca.png"]

    A --> B --> C --> D
    D --> E --> G
    D --> F --> G
    E -->|explained_variance_ratio_| I
    F -->|inertia_| I
    G --> H --> K
    G --> I --> L
    G --> J --> M
```

**[DOĞRULANDI]** PCA kodda KMeans çağrısından önce hesaplanır, fakat KMeans
PCA koordinatlarını değil aynı özgün `vectors` listesini alır. Qdrant clustering
yapmaz.

## Clean architecture katman bağımlılıkları

```mermaid
flowchart TB
    subgraph Presentation["CLI / composition"]
      MAIN["src/ulakbim_analysis/main.py"]
      MODCLI["application/* içindeki __main__ modülleri"]
    end

    subgraph Application["application"]
      IMPORT["import_publications.py"]
      PORT["PublicationRepository Protocol"]
      VECTOR["vector_experiment.py<br/>Embedder + VectorStore Protocol"]
      SELECT["vector_experiment_selection.py"]
      CLUSTER["cluster_article_vectors.py"]
    end

    subgraph Domain["domain"]
      PUB["Publication"]
      VDM["ExperimentArticle / VectorPoint /<br/>StoredArticleVector / SimilarityResult"]
    end

    subgraph Infrastructure["infrastructure"]
      JSON["json_reader.py"]
      MAP["publication_mapper.py"]
      MONGO["MongoDBRepository"]
      EMB["FastEmbedModel"]
      QD["QdrantVectorStore"]
      SETTINGS["settings.py / vector_settings.py"]
    end

    MAIN --> IMPORT
    MAIN --> MONGO
    MODCLI --> Application
    IMPORT --> PORT
    IMPORT --> PUB
    IMPORT -. "doğrudan somut import" .-> JSON
    IMPORT -. "doğrudan somut import" .-> MAP
    VECTOR --> VDM
    VECTOR --> PUB
    SELECT --> VDM
    SELECT -. "doğrudan somut import" .-> JSON
    SELECT -. "doğrudan somut import" .-> MAP
    CLUSTER --> VDM
    CLUSTER -. "doğrudan concrete bağımlılık" .-> QD
    MONGO --> PORT
    MONGO --> PUB
    MAP --> PUB
    QD --> VDM
    EMB --> VECTOR
```

**[ÇIKARIM]** Domain bağımsız ve bazı use case'ler Protocol kullanıyor; fakat
application'ın somut infrastructure importları nedeniyle yapı tam dependency
inversion uygulayan clean architecture değil, clean-architecture esintili bir
katmanlamadır.
