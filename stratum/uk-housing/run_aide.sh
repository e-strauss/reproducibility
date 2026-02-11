# load .env
source .env

# run aide
aide data_dir="data" \
    agent.code.model="gemini" \
    agent.feedback.model=
    agent.steps=10 \
    goal="Create a pipeline that predicts the price of a UK housing dataset. Use simple models and go deep into the data engineering, you can do all kind of complex data engineering. You can go real crazy." \
    eval="use scikit learns r2_score"
