import json
import re
from typing import Dict, List

from summarization.output_validation import validate_structured_summary


def parse_json_structure(text) -> List[Dict[str, List[str]]]:
    text = re.sub(r'^```json', "", text)
    text = re.sub(r'```$', "", text)
    try:
        return json.loads(text)
    except:
        return []


def process_list_structure(entities):
    entities_list = entities.split(",")
    return [kw.strip() for kw in entities_list]


if __name__ == "__main__":
    text = """
    ```json
[
    {
        "topic": "Представление участников",
        "points": [
            "Настя рассказала о своем опыте в NLP и бизнес-задачах, а также о работе в компании 'Звук'.",
            "Саша Мурзина представила свою роль в компании Positive Technologies, занимающейся защитой от хакерских атак.",
            "Дмитрий Колодьев упомянул свою работу в промсофте и участие в ОДС-лаб.",
            "Валентин Малых отметил свой опыт в машинном обучении с 2011 года и работу в компании Huawei.",
            "Антон Воронов рассказал о своем опыте в ML и текущей роли в 'Киберроме'."
        ]
    },
    {
        "topic": "Рынок труда в IT",
        "points": [
            "Обсудили текущие проблемы на рынке труда, включая трудности с наймом специалистов.",
            "Сравнили количество вакансий и резюме, подчеркнув разницу между ними.",
            "Разговор о том, как бизнес адаптируется к изменениям на рынке.",
            "Поделились статистикой о высоком уровне профессионального выгорания среди IT-специалистов."
        ]
    },
    {
        "topic": "Собеседования и подготовка кандидатов",
        "points": [
            "Обсуждалась важность качественной подготовки кандидатов к собеседованиям.",
            "Упоминание о том, что многие кандидаты проходят курсы повышения квалификации, но не могут найти работу.",
            "Поделились опытом участников относительно собеседований и типов вопросов, связанных с ML и Data Science."
        ]
    },
    {
        "topic": "Состояние индустрии машинного обучения",
        "points": [
            "Было отмечено развитие технологий машинного обучения за последние годы.",
            "Обсуждение новых трендов и требований к специалистам в области ML.",
            "Упоминание о специализированных событиях и мероприятиях для специалистов по ML."
        ]
    },
    {
        "topic": "Психологические аспекты работы в IT",
        "points": [
            "Упоминание о высоком уровне стресса и выгорания среди сотрудников в IT.",
            "Обсуждение технологий и стратегий для борьбы с профессиональным выгоранием.",
            "Обсуждение значимости поддержки со стороны коллег и управления компанией."
        ]
    }
]
```
"""
    structured_summary = parse_json_structure(text)
    print(validate_structured_summary(structured_summary))
