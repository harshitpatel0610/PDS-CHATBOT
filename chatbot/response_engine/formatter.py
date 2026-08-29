class ResponseFormatter:

    @staticmethod
    def format_apply(data, entities):

        response = []

        response.append(
            "To apply for a ration card:\n"
        )

        if entities:

            response.append(
                f"Detected Information: {entities}\n"
            )

        response.append(
            "Required Documents:"
        )

        for doc in data["documents"]:

            response.append(
                f"• {doc}"
            )

        response.append("\nApplication Steps:")

        for i, step in enumerate(data["steps"], 1):

            response.append(
                f"{i}. {step}"
            )

        response.append(
            f"\nProcessing Time: {data['processing_time']}"
        )

        return "\n".join(response)