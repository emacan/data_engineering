package it.uniroma3.idd.hw1;

import org.apache.lucene.analysis.core.KeywordAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.index.*;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.net.URL;
import java.nio.file.FileSystems;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class MergeList {

    public static void createIndex(String filepath ) throws IOException{
        StringBuilder jsonContent = new StringBuilder();
        System.out.println("Starting indexing..");
        long startTime = System.currentTimeMillis();
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath + "/quarter_split_processed.json"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                jsonContent.append(line);
            }
        }

        Directory directory = FSDirectory.open(FileSystems.getDefault().getPath(filepath));
        ObjectMapper objectMapper = new ObjectMapper();
        JsonNode rootNode = objectMapper.readTree(jsonContent.toString());
        IndexWriterConfig config = new IndexWriterConfig(new StandardAnalyzer());
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
        IndexWriter writer = new IndexWriter(directory, config);
        writer.deleteAll();

        Iterator<String> fieldNames = rootNode.fieldNames();

        while (fieldNames.hasNext()) {
            String columnName = fieldNames.next();
            JsonNode valueNode = rootNode.get(columnName);

            if (valueNode.isArray()) {
                for (int i = 0; i < valueNode.size(); i++) {
                    addDocument(writer, valueNode.get(i).asText(), columnName);
                }
                
            } else {
                System.err.println("Unexpected value type for key: " + columnName);
            }
        }

        writer.close();
        long endTime = System.currentTimeMillis();
        double elapsedSeconds = (endTime - startTime) / 1000.0;
        System.out.println("Indexing complete in "+ elapsedSeconds + " seconds");
    }

    private static void search(String path) throws Exception {
        Directory directory = FSDirectory.open(FileSystems.getDefault().getPath(path));

        IndexReader reader = DirectoryReader.open(directory);
        IndexSearcher searcher = new IndexSearcher(reader);

        // Sample query tokens
        //String[] queryTokens = {"dodecahedron", "icosahedron"};
        //String[] queryTokens = {"Manhattan", "West Long Branch"};
        String[] queryTokens = {"Lise Bouvier", "Madeline Minot"};
        //String[] queryTokens = {"ف", "ج", "ك"};

        Map<String, Integer> set2count = new HashMap<>();

        for (String token : queryTokens) {
            Query query = new QueryParser("valueName", new KeywordAnalyzer()).parse(token);
            TopDocs topDocs = searcher.search(query, Integer.MAX_VALUE);
            System.out.println(token + ":");
            System.out.println(topDocs.totalHits);

            for (ScoreDoc scoreDoc : topDocs.scoreDocs) {
                int docID = scoreDoc.doc;
                Document document = reader.document(docID);
                String[] values = document.getValues("columnName");
                for(String value : values){
                    set2count.put(value, set2count.getOrDefault(value, 0) + 1);
                }   
            }
        }

        PriorityQueue<Map.Entry<String, Integer>> sortedCandidates = new PriorityQueue<>(
                (e1, e2) -> Integer.compare(e2.getValue(), e1.getValue()));
        sortedCandidates.addAll(set2count.entrySet());

        int k = 3;
        for (int i = 0; i < k && !sortedCandidates.isEmpty(); i++) {
            Map.Entry<String, Integer> entry = sortedCandidates.poll();
            System.out.println(entry.getKey() + ": " + entry.getValue() + " intersecting tokens");
        }

        reader.close();

    }
    public static void main(String[] args) throws Exception {

        Enumeration<URL> sources = MergeList.class.getClassLoader().getResources("sources");
        String folderPath = "";

        if (sources.hasMoreElements()) { 
            URL resourceUrl = sources.nextElement();
            folderPath = resourceUrl.getPath();
        }

        createIndex(folderPath);

        search(folderPath);
  
    }

    private static void addDocument(IndexWriter writer, String valueName, String columnName) throws IOException {
        Document document = new Document();
        document.add(new StringField("valueName", valueName, Field.Store.YES));
        document.add(new StringField("columnName", columnName, Field.Store.YES));
        writer.addDocument(document);
    }
}
