import csv
from chatbot.router.router import route

correct = 0
total = 0

print("=" * 100)

with open("intent_test_dataset.csv", newline="", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        query = row["query"]
        expected = row["expected_intent"]

        result = route(query)

        predicted = result.intent if result.is_pds else "None"

        status = "PASS" if predicted == expected else "FAIL"

        print(f"{status:5} | Expected: {expected:30} Predicted: {predicted:30}")
        print(f"Query: {query}")
        print("-" * 100)

        total += 1

        if predicted == expected:
            correct += 1

accuracy = (correct / total) * 100

print("\n")
print("=" * 100)
print(f"Accuracy : {accuracy:.2f}%")
print(f"Correct  : {correct}")
print(f"Wrong    : {total - correct}")
print("=" * 100)