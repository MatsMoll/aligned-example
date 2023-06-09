from aligned import FeatureView, String, Int64
from examples.sources import aligned_db, redis
from aligned.schemas.text_vectoriser import TextVectoriserModel

class DocumentationSnippet(FeatureView):

    metadata = FeatureView.metadata_with(
        name="documentation_snippet",
        description="Features related to a snippet of the Aligned documentation",
        batch_source=aligned_db
    )

    id = Int64().as_entity()

    version_tag = String().description("The aligned version tag that the snippet is valid for").is_required()
    source_file = String().description("The file that the snippet is from").is_required()

    snippet = String().description("The documentation").is_required()

    combined_snippet = snippet.append("\n\nSource file: ").append(source_file)

    snippet_embedding = combined_snippet.embedding(
        TextVectoriserModel.huggingface("all-MiniLM-L6-v2")
    ).indexed(
        redis.index(
            "doc_index",
            initial_cap=1000,
        ),
        metadata=[
            version_tag,
            source_file
        ],
        embedding_size=384
    )
