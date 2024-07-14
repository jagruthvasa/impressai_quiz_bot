    
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")

    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)
        current_question_id = 0
    elif current_question_id == -1:
        success, error = record_current_answer(message, current_question_id, session)
    else:
        success, error = record_current_answer(message, current_question_id, session)
        current_question_id = current_question_id + 1

        if not success:
            return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    if current_question_id is None:
        return False, "No current question to answer."

    if current_question_id == -1:
        return True, "All Questions Attempted. Quiz is Completed."

    if "answers" not in session:
        session["answers"] = []

    current_question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = current_question["answer"]

    session["answers"].append({
        "question_id": current_question_id,
        "answer": answer,
        "is_correct": answer == correct_answer
    })

    return True, ""


def get_next_question(next_question_id):

    if next_question_id == -1 or next_question_id >= len(PYTHON_QUESTION_LIST):
        return None, -1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        next_question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
        next_question_options = PYTHON_QUESTION_LIST[next_question_id]["options"]
        next_question_combined = f"{next_question}<br><br>Options:<br><br>{'<br>'.join(next_question_options)}"
        return next_question_combined, next_question_id

    return None, None


def generate_final_response(session):
    if "answers" not in session:
        return "No answers recorded."

    correct_count = sum(1 for answer in session["answers"] if answer["is_correct"])
    total_questions = len(PYTHON_QUESTION_LIST)

    final_response = f"You answered {correct_count} out of {total_questions} questions correctly.<br><br>"

    for answer_record in session["answers"]:
        question_id = answer_record["question_id"]
        user_answer = answer_record["answer"]
        is_correct = answer_record["is_correct"]
        question = PYTHON_QUESTION_LIST[question_id]
        correct_answer = question["answer"]

        final_response += f"Question {question_id + 1}: {question['question_text']}<br>"
        final_response += f"Your answer: {user_answer} {'(Correct)' if is_correct else '(Incorrect)'}<br>"
        final_response += f"Correct answer: {correct_answer}<br><br>"

    return final_response
