from engine.ollama_integration import sophia_ollama

TEST_QUERIES = [
    "play cornfield chase on spotify",
    "open notepad",
    "search for python tutorials on youtube",
    "what is the weather today?",
    "can you explain how photosynthesis works?",
    "I'm feeling sad today",
    "how do I solve a quadratic equation?",
    "tell me a joke",
    "play chinni chinni asha from spotify app"
]

def main():
    print("Sophia Ollama Intent Extraction Test\n" + "="*40)
    for query in TEST_QUERIES:
        print(f"\nUser: {query}")
        response = sophia_ollama.process_query(query)
        print(f"Ollama Response:\n{response}")

if __name__ == "__main__":
    main() 