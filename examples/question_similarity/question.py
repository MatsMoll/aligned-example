from aligned import feature_view, model_contract, String, Int32, PostgreSQLConfig, RedisConfig, Int64
from aligned.schemas.text_vectoriser import TextVectoriserModel

redis_cluster = RedisConfig.localhost()
postgres = PostgreSQLConfig("QUESTION_DATABASE")


@feature_view(
    name="question",
    description="Features related to a question",
    source=postgres.table("Task", mapping_keys={
        "topicID": "topic_id",
    })
)
class Question:

    id = Int64().as_entity()

    topic_id = Int32()
    description = String()
    question = String()

    full_question = description.append(question)

    question_embedding = full_question.embedding(
        TextVectoriserModel.huggingface("all-MiniLM-L6-v2")
    ).indexed(
        storage=redis_cluster.index("question_embedding_index"),
        metadata=[topic_id],
        embedding_size=384
    )



question = Question()

@model_contract(
    "question_subtopic",
    description="Predicts the expected subtopic, by comparing agains similar models",
    features=[
        question.question_embedding
    ],
)
class QuestionSubtopicModel:

    predicted_id = question.topic_id.as_classification_label()
