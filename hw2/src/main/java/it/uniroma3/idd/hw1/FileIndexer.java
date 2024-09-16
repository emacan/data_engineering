/*
 Put header here
 */
package it.uniroma3.idd.hw1;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.CharArraySet;
import org.apache.lucene.analysis.it.ItalianAnalyzer;
import org.apache.lucene.analysis.miscellaneous.PerFieldAnalyzerWrapper;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.File;
import java.net.URL;
import java.nio.file.FileSystems;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class FileIndexer {
	
    public static void main(String[] args) throws Exception {
        // Indicizza i file
        Enumeration<URL> sources = FileIndexer.class.getClassLoader().getResources("sources");
        String folderPath = "";

        if (sources.hasMoreElements()) { // Check if at least one resource was found
            URL resourceUrl = sources.nextElement();
            folderPath = resourceUrl.getPath();
        }
        indexFiles(folderPath);

        // Esegui una query
        search(folderPath);
    }

    private static void indexFiles(String indexPath) throws Exception {
        Directory directory = FSDirectory.open(FileSystems.getDefault().getPath(indexPath));
        Map<String, Analyzer> perFieldAnalyzers = new HashMap<>();
        
        CharArraySet stopWords = new CharArraySet(Arrays.asList("il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "alcuni", "alcune", 
        														"di", "a", "da", "in", "con", "su", "per", "tra", "fra", "e", "o", "ma", "se", "perché"), true);
        
        perFieldAnalyzers.put("filename", new ItalianAnalyzer());
        perFieldAnalyzers.put("content", new ItalianAnalyzer(stopWords));
        Analyzer analyzer = new PerFieldAnalyzerWrapper(new ItalianAnalyzer(),
        perFieldAnalyzers);
        
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter indexWriter = new IndexWriter(directory, config);

        File folder = new File(indexPath);
        File[] files = folder.listFiles();

        if (files != null) {
            for (File file : files) {
                if (file.isFile() && file.getName().endsWith(".txt")) {
                    Document document = new Document();
	                // Aggiunge un campo "filename" all'indice
	                document.add(new TextField("filename", file.getName(), Field.Store.YES));
	                // Aggiunge un campo "content" all'indice con il contenuto del file
	                document.add(new TextField("content", new Scanner(file).useDelimiter("\\Z").next(), Field.Store.YES));
	                System.out.println("Document added!");
                    indexWriter.addDocument(document);
                }
            }
        }

        indexWriter.close();
        directory.close();
    }

    private static void search(String path) throws Exception {
        Path indexPath = FileSystems.getDefault().getPath(path);
        Directory directory = FSDirectory.open(indexPath);
        IndexSearcher indexSearcher = new IndexSearcher(DirectoryReader.open(directory));
        Analyzer analyzer = new ItalianAnalyzer();

        Scanner scanner = new Scanner(System.in);
        System.out.println("Inserisci la tua query:");
        String queryString = scanner.nextLine();

        QueryParser queryParser = new QueryParser("content", analyzer);
        Query query = queryParser.parse(queryString);

        TopDocs topDocs = indexSearcher.search(query, 10);

        System.out.println("Risultati della query:");
        for (ScoreDoc scoreDoc : topDocs.scoreDocs) {
            Document document = indexSearcher.doc(scoreDoc.doc);
            System.out.println("Nome del file: " + document.get("filename"));
            System.out.println("Contenuto del file: " + document.get("content"));
            System.out.println("Score: " + scoreDoc.score);
            System.out.println("-----");
        }

        directory.close();
    }
}
