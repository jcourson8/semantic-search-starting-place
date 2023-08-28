import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from supabase.client import Client
from langchain.vectorstores import SupabaseVectorStore
from langchain.docstore.document import Document
import csv


def create_embedding(content, openai_api_key, remove_newlines=True):
    if remove_newlines:
        content = content.replace("\n", " ")
    return OpenAIEmbeddings(openai_api_key=openai_api_key).embed_query(content)

def similarity_search(
        query,
        client,
        embedding,
        table= "match_vectors",
        k = 6,
        threshold = 0.5,
    ):
        vectors = embedding.embed_documents([query])
        query_embedding = vectors[0]
        res = client.rpc(
            table,
            {
                "query_embedding": query_embedding,
                "match_count": k,
            },
        ).execute()

        match_result = [
            (
                Document(
                    metadata=search.get("metadata", {}),  # type: ignore
                    page_content=search.get("content", ""),
                ),
                search.get("similarity", 0.0),
            )
            for search in res.data
            if search.get("content")
        ]

        documents = [doc for doc, _ in match_result]

        return documents

def load_json(file_path):
    with open(file_path, "r") as read_file:
        data = json.load(read_file)
    return data

def add_vecs(
    client,
    table_name: str,
    vectors,
    documents,
    ids,
):
    """Add vectors to Supabase table."""

    rows = [
        {
            "id": ids[idx],
            "content": documents[idx].page_content,
            "embedding": embedding,
            "metadata": documents[idx].metadata,  # type: ignore
        }
        for idx, embedding in enumerate(vectors)
    ]

    # According to the SupabaseVectorStore JS implementation, the best chunk size
    # is 500
    chunk_size = 500
    id_list = []
    for i in range(0, len(rows), chunk_size):
        chunk = rows[i : i + chunk_size]

        result = client.from_(table_name).upsert(chunk).execute()  # type: ignore

        if len(result.data) == 0:
            raise Exception("Error inserting: No rows added")

        # VectorStore.add_vectors returns ids as strings
        ids = [str(i.get("id")) for i in result.data if i.get("id")]

        id_list.extend(ids)

    return id_list

def main():
    load_dotenv()
    file_path = os.getenv("FILE_PATH")
    openai_key = os.getenv("OPENAI_KEY")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    supabase_client= create_client(supabase_url, supabase_key)
    
    data = load_json(file_path)

    docs = []
    ids = []
    vectors = []
    for (id, (uuid, details)) in enumerate(data.items()):
        print(id)
        details = {key: value for key, value in details.items() if value is not None}
        details_string = ", ".join(f"{key}: {value}" for key, value in details.items())
        print("String length: " + str(len(details_string)))
        # create documents
        docs.append(Document(
            page_content=details_string, metadata={'uuid': uuid}
        ))
        # create ids
        ids.append(uuid)
        # create vectors
        vectors.append(create_embedding(details_string, openai_key))

    # save docs, ids, vectors to csv first
    rows = [ids, docs, vectors]

    # open the file in the write mode
    with open('vectors_saved.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        # write the rows to the csv file
        writer.writerows(rows)


    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
    # # # create vector store
    vecstore = SupabaseVectorStore(supabase_client, embeddings, table_name="vectors")
    # # vector_store = SupabaseVectorStore.from_documents(docs, embeddings, client=supabase_client, )
    print("adding vectors")

    # add vecs 4 at a time to supabase
    for i in range(0, len(docs), 4):
        chunk_docs = docs[i : i + 4]
        chunk_ids = ids[i : i + 4]
        chunk_vectors = vectors[i : i + 4]
        print(chunk_docs)
        print(chunk_ids)
        print(chunk_vectors)
        vecstore.add_vectors(vectors=chunk_vectors, documents=chunk_docs, ids=chunk_ids)        

if __name__ == "__main__":
    main()
