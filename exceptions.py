from fastapi import HTTPException, status


EmailAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Почта уже занята"
)

UsernameAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Юзернейм уже занят"
)

UsernameEmailAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Юзернейм и почта уже заняты"
)

IncorrectEmailLoginUserOrPassword = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверная почта, логин или пароль",
)

IncorrcetFormatUsername = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Имя пользователя может содержать только буквы, цифры и '_'. Длина имени пользователя должна быть от 3 до 20 символов.",
)

TokenAbsentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен отсутствует"
)

IncorrectTokenException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный формат токена",
)

TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
)

UserIsNotPresentException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

INVALID_REFRESH_SESSION = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный токен"
)
