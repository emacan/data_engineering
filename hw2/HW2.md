## Analyzers
Ho scelto di utilizzare l'`ItalianAnalyzer` per l'analisi del campo "filename". Questo è un buon approccio perché il campo "filename" contiene nomi di città italiane. Per il campo "content", ho utilizzato lo stesso `ItalianAnalyzer`, ma con un set personalizzato di stop words, inserendo parole comuni che spesso non contribuiscono in modo significativo all'indicizzazione e possono essere escluse per migliorare la precisione delle ricerche, ad esempio articoli e preposizioni.

## Experiments
### Statistics
I tempi di indicizzazione sono di `0.8 secondi` per un totale di `103 file`.

### Query Examples
- Porto
- Chiesa
- Monumenti
- Architettura rinascimentale
- Gabriele D’Annunzio
- Castello
- Spiagge sabbiose
- Arte
- Università
- Parmigiano Reggiano
