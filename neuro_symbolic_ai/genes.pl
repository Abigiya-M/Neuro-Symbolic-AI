% genes.pl
% gene_assoc(Gene, Trait, EvidenceScore).
gene_assoc('BRCA1', 'breast_cancer', 0.98).
gene_assoc('BRCA2', 'breast_cancer', 0.95).
gene_assoc('TP53', 'breast_cancer', 0.90).
gene_assoc('TP53', 'lung_cancer', 0.88).
gene_assoc('APOE', 'alzheimers', 0.86).
gene_assoc('CFTR', 'cystic_fibrosis', 0.93).
gene_assoc('MTHFR', 'homocysteinemia', 0.60).

% strong association rule
strong_assoc(Gene, Trait) :- gene_assoc(Gene, Trait, Score), Score >= 0.8.

% shared trait genes
shared_trait_genes(Trait, Genes) :-
    findall(Gene, gene_assoc(Gene, Trait, _), Genes).
