"""
Script to seed sample paper data into Neo4j for demonstration.
Run this after Neo4j is connected to populate the database.
"""

import sys
sys.path.insert(0, '/app/backend')

from db.neo4j import Neo4jConnection

SAMPLE_PAPERS = [
    {
        "id": "paper_001",
        "title": "Deep Learning for Natural Language Processing: A Comprehensive Survey",
        "abstract": "This paper provides a comprehensive survey of deep learning techniques applied to natural language processing tasks, including sentiment analysis, machine translation, and question answering.",
        "year": 2023,
        "authors": ["John Smith", "Maria Garcia"],
        "venue": "Journal of Machine Learning Research",
        "url": "https://example.com/paper001"
    },
    {
        "id": "paper_002",
        "title": "Attention Mechanisms in Neural Networks: Theory and Applications",
        "abstract": "We present a detailed analysis of attention mechanisms in neural networks, discussing their theoretical foundations and practical applications in computer vision and NLP.",
        "year": 2023,
        "authors": ["Alice Johnson", "Bob Williams"],
        "venue": "NeurIPS 2023",
        "url": "https://example.com/paper002"
    },
    {
        "id": "paper_003",
        "title": "Transformer Architectures: From BERT to GPT-4",
        "abstract": "An evolutionary perspective on transformer-based language models, tracing the development from early attention models to modern large language models.",
        "year": 2024,
        "authors": ["David Chen", "Emily Brown"],
        "venue": "ACL 2024",
        "url": "https://example.com/paper003"
    },
    {
        "id": "paper_004",
        "title": "Graph Neural Networks for Knowledge Representation",
        "abstract": "This work explores the application of graph neural networks to knowledge graph completion and reasoning tasks.",
        "year": 2023,
        "authors": ["Michael Lee", "Sarah Davis"],
        "venue": "ICLR 2023",
        "url": "https://example.com/paper004"
    },
    {
        "id": "paper_005",
        "title": "Reinforcement Learning in Robotics: Recent Advances",
        "abstract": "A survey of recent advances in applying reinforcement learning algorithms to robotic manipulation and navigation tasks.",
        "year": 2024,
        "authors": ["James Wilson", "Lisa Anderson"],
        "venue": "IEEE Robotics and Automation",
        "url": "https://example.com/paper005"
    },
    {
        "id": "paper_006",
        "title": "Federated Learning for Privacy-Preserving Machine Learning",
        "abstract": "We propose a novel federated learning framework that enables collaborative model training while preserving data privacy.",
        "year": 2023,
        "authors": ["Robert Taylor", "Jennifer Martinez"],
        "venue": "ICML 2023",
        "url": "https://example.com/paper006"
    },
    {
        "id": "paper_007",
        "title": "Computer Vision Applications in Medical Imaging",
        "abstract": "This paper reviews the latest applications of computer vision and deep learning in medical image analysis and diagnosis.",
        "year": 2024,
        "authors": ["William Thomas", "Amanda White"],
        "venue": "Nature Medicine",
        "url": "https://example.com/paper007"
    },
    {
        "id": "paper_008",
        "title": "Quantum Computing and Machine Learning: A New Frontier",
        "abstract": "Exploring the intersection of quantum computing and machine learning, including quantum neural networks and variational algorithms.",
        "year": 2024,
        "authors": ["Christopher Harris", "Elizabeth Clark"],
        "venue": "Physical Review X",
        "url": "https://example.com/paper008"
    },
    {
        "id": "paper_009",
        "title": "Explainable AI: Making Black-Box Models Transparent",
        "abstract": "A comprehensive review of techniques for explaining and interpreting machine learning model predictions.",
        "year": 2023,
        "authors": ["Daniel Robinson", "Michelle Lewis"],
        "venue": "AI Magazine",
        "url": "https://example.com/paper009"
    },
    {
        "id": "paper_010",
        "title": "Neural Architecture Search: Automating Deep Learning",
        "abstract": "This work presents efficient methods for automatically designing neural network architectures using evolutionary algorithms and reinforcement learning.",
        "year": 2023,
        "authors": ["Matthew Walker", "Rachel Hall"],
        "venue": "CVPR 2023",
        "url": "https://example.com/paper010"
    },
    {
        "id": "paper_011",
        "title": "Generative Adversarial Networks for Image Synthesis",
        "abstract": "A detailed study of GAN architectures for high-quality image generation and style transfer applications.",
        "year": 2023,
        "authors": ["John Smith", "Alice Johnson"],
        "venue": "SIGGRAPH 2023",
        "url": "https://example.com/paper011"
    },
    {
        "id": "paper_012",
        "title": "Time Series Forecasting with Deep Learning",
        "abstract": "Novel deep learning approaches for time series prediction in financial markets and weather forecasting.",
        "year": 2024,
        "authors": ["Maria Garcia", "Bob Williams"],
        "venue": "KDD 2024",
        "url": "https://example.com/paper012"
    },
    {
        "id": "paper_013",
        "title": "Multi-Modal Learning: Bridging Vision and Language",
        "abstract": "This paper explores techniques for learning joint representations from visual and textual data.",
        "year": 2024,
        "authors": ["David Chen", "Sarah Davis"],
        "venue": "EMNLP 2024",
        "url": "https://example.com/paper013"
    },
    {
        "id": "paper_014",
        "title": "Efficient Training of Large Language Models",
        "abstract": "Techniques for reducing computational costs and memory requirements when training billion-parameter language models.",
        "year": 2024,
        "authors": ["Emily Brown", "Michael Lee"],
        "venue": "MLSys 2024",
        "url": "https://example.com/paper014"
    },
    {
        "id": "paper_015",
        "title": "Causal Inference in Machine Learning",
        "abstract": "A framework for incorporating causal reasoning into machine learning models for improved generalization.",
        "year": 2023,
        "authors": ["James Wilson", "Jennifer Martinez"],
        "venue": "UAI 2023",
        "url": "https://example.com/paper015"
    }
]

# Citation relationships (paper_id -> cites these papers)
CITATIONS = [
    ("paper_002", "paper_001"),
    ("paper_003", "paper_001"),
    ("paper_003", "paper_002"),
    ("paper_004", "paper_001"),
    ("paper_006", "paper_001"),
    ("paper_007", "paper_001"),
    ("paper_007", "paper_002"),
    ("paper_009", "paper_001"),
    ("paper_009", "paper_004"),
    ("paper_010", "paper_002"),
    ("paper_011", "paper_002"),
    ("paper_011", "paper_010"),
    ("paper_012", "paper_001"),
    ("paper_012", "paper_003"),
    ("paper_013", "paper_002"),
    ("paper_013", "paper_003"),
    ("paper_013", "paper_011"),
    ("paper_014", "paper_003"),
    ("paper_014", "paper_010"),
    ("paper_015", "paper_001"),
    ("paper_015", "paper_009"),
]


def seed_data():
    driver = Neo4jConnection.get_driver()
    if not driver:
        print("Failed to connect to Neo4j")
        return False
    
    with driver.session() as session:
        # Check if data exists
        result = session.run("MATCH (p:Paper) RETURN count(p) as count")
        count = result.single()["count"]
        if count > 0:
            print(f"Database already has {count} papers. Skipping seed.")
            return True
        
        print("Seeding sample data...")
        
        # Create papers, authors, and venues
        for paper in SAMPLE_PAPERS:
            # Create Paper node
            session.run("""
                CREATE (p:Paper {
                    id: $id,
                    title: $title,
                    abstract: $abstract,
                    year: $year,
                    url: $url
                })
            """, paper)
            
            # Create Venue and relationship
            session.run("""
                MERGE (v:Venue {name: $venue})
                WITH v
                MATCH (p:Paper {id: $id})
                CREATE (p)-[:PUBLISHED_IN]->(v)
            """, {"venue": paper["venue"], "id": paper["id"]})
            
            # Create Authors and relationships
            for author in paper["authors"]:
                session.run("""
                    MERGE (a:Author {name: $author})
                    WITH a
                    MATCH (p:Paper {id: $id})
                    CREATE (a)-[:WROTE]->(p)
                """, {"author": author, "id": paper["id"]})
        
        # Create citation relationships
        for citing_id, cited_id in CITATIONS:
            session.run("""
                MATCH (citing:Paper {id: $citing_id})
                MATCH (cited:Paper {id: $cited_id})
                CREATE (citing)-[:CITES]->(cited)
            """, {"citing_id": citing_id, "cited_id": cited_id})
        
        print(f"Seeded {len(SAMPLE_PAPERS)} papers with {len(CITATIONS)} citations")
        
        # Verify
        result = session.run("""
            MATCH (p:Paper)
            RETURN count(p) as papers
        """)
        print(f"Total papers in database: {result.single()['papers']}")
        
        return True


if __name__ == "__main__":
    seed_data()
