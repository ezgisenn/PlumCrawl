import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plumcrawl.db')

class PlumSearchEngine:
    def __init__(self):
        # We don't hold a persistent connection to ensure we always read the freshest 
        # data that Agent 3 (Indexer) is writing concurrently.
        pass

    def _get_db_connection(self):
        # Connect using read-only mode via URI for maximum concurrency safety
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def calculate_relevancy(self, text, query_words, depth):
        """
        Calculates relevancy based on two primary factors:
        1. Term Frequency (How many times the words appear in the text)
        2. Tree Depth Penalty (Results closer to origin score higher)
        """
        text_lower = text.lower() if text else ""
        frequency_score = 0
        
        for word in query_words:
            frequency_score += text_lower.count(word)
            
        if frequency_score == 0:
            return 0
            
        # Depth penalty: Depth 0 gets a multiplier of 1.0. Depth 1 gets 0.5, etc.
        depth_weight = 1.0 / (depth + 1.0)
        
        # Final Score Formula
        return frequency_score * depth_weight

    def search(self, query, top_k=20):
        """
        Core Requirement: Given a query, return relevant URLs.
        Returns a list of triples: (relevant_url, origin_url, depth)
        """
        if not query.strip():
            return []

        query_words = query.lower().split()
        results = []
        
        print(f"[Agent 4] Searching for: '{query}'")
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Fetch all indexed pages to calculate dynamic scores
            cursor.execute("SELECT url, origin_url, depth, content FROM pages")
            
            for row in cursor.fetchall():
                score = self.calculate_relevancy(row['content'], query_words, row['depth'])
                if score > 0:
                    results.append({
                        'url': row['url'],
                        'origin_url': row['origin_url'],
                        'depth': row['depth'],
                        'score': score
                    })
                    
            conn.close()
            
            # Sort by highest relevancy score
            results.sort(key=lambda x: x['score'], reverse=True)
            
            # Format output strictly to the requested triples
            formatted_results = []
            for res in results[:top_k]:
                triple = (res['url'], res['origin_url'], res['depth'])
                formatted_results.append(triple)
                print(f"Match: {triple} (Score: {res['score']:.2f})")
                
            return formatted_results

        except sqlite3.OperationalError as e:
            print(f"[Agent 4] Database access error: {e}")
            return []

# --- Test Execution ---
if __name__ == "__main__":
    searcher = PlumSearchEngine()
    # Testing with a word we know exists in the example.com index
    searcher.search("domain")