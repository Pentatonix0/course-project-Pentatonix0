Feature: Security NFR Acceptance

Scenario: JWT access токен истекает через 15 минут
Given выдан access token пользователю
And текущая конфигурация содержит ACCESS_TOKEN_TTL=15m
When запрос к защищённому эндпоинту выполняется через 16 минут
Then ответ имеет статус 401
And тело ответа не содержит “Traceback” и секретов

Scenario: Защита от брутфорса на /auth/login
Given 5 неуспешных попыток логина за 1 минуту с одного IP
When выполняется 6-я попытка логина в ту же минуту
Then ответ 429 Too Many Requests

Scenario: Все модифицирующие эндпоинты требуют JWT
Given OpenAPI спецификация сервиса
When проверяется security для всех POST/PATCH/DELETE путей
Then каждый путь содержит требование BearerAuth

Scenario: Лишние поля в DTO отклоняются
Given схема создания квиза
When отправлен POST /quizzes с неизвестным полем “hack”
Then ответ 422 Unprocessable Entity

Scenario: Ошибка сервера не раскрывает детали
Given внутри обработчика возникает необработанное исключение
When клиент получает 500 Internal Server Error
Then тело ответа содержит generic сообщение без “Traceback”
And токены/секреты не встречаются в теле/заголовках
