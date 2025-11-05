def before_all(context):
    context.broker_url = context.config.userdata.get("broker_url", "http://localhost:50051")
