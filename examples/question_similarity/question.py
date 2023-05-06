from aligned import FeatureView, String, Int32, PostgreSQLConfig, RedisConfig, Int64, Model
from aligned.schemas.text_vectoriser import TextVectoriserModel

redis_cluster = RedisConfig.localhost()
postgres = PostgreSQLConfig("QUESTION_DATABASE")


class Question(FeatureView):

    metadata = FeatureView.metadata_with(
        name="question",
        description="Features related to a question",
        batch_source=postgres.table("Task", mapping_keys={
            "topicID": "topic_id",
        })
    )

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



class QuestionSubtopicModel(Model):

    question = Question()

    metadata = Model.metadata_with(
        "question_subtopic",
        description="Predicts the expected subtopic, by comparing agains similar models",
        features=[
            question.question_embedding
        ],
    )

    predicted_id = question.topic_id.as_classification_target()