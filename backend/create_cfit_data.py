import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal  # noqa: E402
from app import models  # noqa: E402
from app.answer_keys import ANSWER_KEY  # noqa: E402


BASE_DIR = Path(__file__).parent
STATIC_ROOT = BASE_DIR / "static" / "images" / "tests"
INSTRUCTION_ROOT = STATIC_ROOT / "instructions"

# Простые подписи для тестов
TEST_NAMES = {
    "A": {
        1: "Часть A. Субтест 1",
        2: "Часть A. Субтест 2",
        3: "Часть A. Субтест 3",
        4: "Часть A. Субтест 4",
    },
    "B": {
        1: "Часть B. Субтест 1",
        2: "Часть B. Субтест 2",
        3: "Часть B. Субтест 3",
        4: "Часть B. Субтест 4",
    },
}

# Настройки времени: A1-3 по 4 минуты, остальные по 3 минуты
TIME_LIMITS = {
    ("A", 1): 240,
    ("A", 2): 240,
    ("A", 3): 240,
}
DEFAULT_TIME_LIMIT = 180  # секунды для всех остальных


def normalize_image_path(path: Path) -> str:
    """Вернуть путь относительно каталога static/images для StaticFiles."""
    relative = path.relative_to(STATIC_ROOT.parent)
    return str(relative).replace("\\", "/")


def upsert_test(db, test_part: str, test_number: int) -> models.Test:
    """Создать или обновить тест с привязкой инструкции."""
    test = (
        db.query(models.Test)
        .filter(
            models.Test.test_part == test_part,
            models.Test.test_number == test_number,
        )
        .first()
    )

    instruction_file = f"part_{'1' if test_part == 'A' else '2'}_test_{test_number}.png"
    instruction_path = INSTRUCTION_ROOT / instruction_file

    description_image = None
    if instruction_path.exists():
        description_image = normalize_image_path(instruction_path)

    # Выставляем лимит времени
    time_limit = TIME_LIMITS.get((test_part, test_number), DEFAULT_TIME_LIMIT)

    if not test:
        test = models.Test(
            test_part=test_part,
            test_number=test_number,
            name=TEST_NAMES[test_part][test_number],
            description_image=description_image,
            instruction_text="",
            time_limit=time_limit,
            is_active=True,
        )
        db.add(test)
        db.flush()
    else:
        test.name = TEST_NAMES[test_part][test_number]
        test.description_image = description_image
        test.time_limit = time_limit
        test.is_active = True
        db.add(test)

    return test


def upsert_questions(db, test: models.Test, questions_dir: Path):
    """Создать или обновить вопросы для теста."""
    # Берем только png с числовыми названиями
    files = sorted(
        [p for p in questions_dir.glob("*.png") if p.stem.isdigit()],
        key=lambda p: int(p.stem),
    )

    for file_path in files:
        q_number = int(file_path.stem)
        correct_answer = ANSWER_KEY.get(test.test_part, {}).get(
            test.test_number, {}
        ).get(q_number)

        image_path = normalize_image_path(file_path)

        question = (
            db.query(models.Question)
            .filter(
                models.Question.test_id == test.id,
                models.Question.question_number == q_number,
            )
            .first()
        )

        if not question:
            question = models.Question(
                test_id=test.id,
                question_number=q_number,
                image_path=image_path,
                correct_answer=correct_answer,
            )
            db.add(question)
        else:
            question.image_path = image_path
            question.correct_answer = correct_answer
            db.add(question)


def create_cfit_data():
    db = SessionLocal()
    try:
        for part in ["A", "B"]:
            part_dir = STATIC_ROOT / f"part{part}"
            if not part_dir.exists():
                print(f"Каталог с вопросами не найден: {part_dir}")
                continue

            for test_number in range(1, 5):
                test_dir = part_dir / f"test{test_number}"
                if not test_dir.exists():
                    print(f"Пропущен тест {part}{test_number}: нет каталога {test_dir}")
                    continue

                test = upsert_test(db, part, test_number)
                upsert_questions(db, test, test_dir)

        db.commit()
        print("✅ Данные CFIT успешно обновлены")
    except Exception as exc:
        db.rollback()
        print(f"❌ Ошибка при создании данных: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_cfit_data()

