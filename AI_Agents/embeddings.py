# Import the OpenAI class from the openai library
from openai import OpenAI

# Initialize the OpenAI client.
# This assumes you have your API key configured in an environment variable (OPENAI_API_KEY).
# The client object handles authentication and communication with the OpenAI API.
client = OpenAI()

# Call the embeddings creation endpoint.
# This is the core API call to generate a numerical representation (embedding) of the text.
response = client.embeddings.create(
    # The 'input' parameter takes the text string you want to embed.
    # It can be a single string or a list of strings.
    input="Your text string goes here",
    
    # The 'model' parameter specifies which embedding model to use.
    # 'text-embedding-3-small' is a popular, cost-effective model for this task.
    model="text-embedding-3-small"
)

# The response object contains the embedding data.
# 'response.data' is a list of embedding objects.
# We access the first object with '[0]' since we only submitted one string.
# '.embedding' extracts the list of floating-point numbers that represents the text embedding.
# This embedding is a dense vector that captures the semantic meaning of the input text.
print(response.data[0].embedding)