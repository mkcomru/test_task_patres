# API для библиотечной системы

RESTful API для управления библиотечным каталогом с использованием FastAPI, SQLAlchemy и JWT-аутентификации.

## Инструкция по запуску

### Предварительные требования

- Python 3.8+
- PostgreSQL или SQLite

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Настройка базы данных

1. Создайте базу данных (PostgreSQL) или используйте SQLite
2. Настройте переменные окружения в файле `.env`:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
# или для SQLite
DATABASE_URL=sqlite:///./library.db
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Применение миграций

```bash
alembic upgrade head
```

### Запуск сервера

```bash
uvicorn app.main:app --reload
```

### Регистрация первого пользователя

Для регистрации первого пользователя (библиотекаря) выполните POST-запрос на эндпоинт `/api/v1/auth/register`:

```json
{
  "email": "librarian@example.com",
  "password": "secure_password"
}
```

После регистрации вы можете получить JWT-токен через эндпоинт `/api/v1/auth/login` с теми же учетными данными.

## Описание принятых решений по структуре БД

### Таблицы

1. **users** - Пользователи системы (библиотекари)
   - id (PK) - Первичный ключ
   - email (уникальный) - Email пользователя
   - hashed_password - Хешированный пароль
   - is_active - Статус активности пользователя
   - created_at - Дата создания
   - updated_at - Дата обновления

2. **books** - Книги в библиотеке
   - id (PK) - Первичный ключ
   - title - Название книги (обязательное)
   - author - Автор книги (обязательное)
   - publication_year - Год публикации (опционально)
   - isbn - Уникальный идентификатор книги (опционально)
   - quantity - Количество экземпляров (по умолчанию 1)
   - description - Описание книги (опционально, добавлено во второй миграции)
   - created_at - Дата создания
   - updated_at - Дата обновления

3. **readers** - Читатели библиотеки
   - id (PK) - Первичный ключ
   - name - Имя читателя (обязательное)
   - email - Email читателя (уникальный, обязательное)
   - created_at - Дата создания
   - updated_at - Дата обновления

4. **borrowed_books** - Выданные книги
   - id (PK) - Первичный ключ
   - book_id (FK) - Внешний ключ к таблице books
   - reader_id (FK) - Внешний ключ к таблице readers
   - borrow_date - Дата выдачи
   - return_date - Дата возврата (NULL для невозвращенных книг)

### Связи между таблицами

- **borrowed_books.book_id** -> **books.id** (Many-to-One): Одна книга может быть выдана много раз
- **borrowed_books.reader_id** -> **readers.id** (Many-to-One): Один читатель может брать много книг

### Индексы

- **books.isbn** - Уникальный индекс для быстрого поиска по ISBN
- **readers.email** - Уникальный индекс для быстрого поиска по email
- **users.email** - Уникальный индекс для быстрого поиска по email

## Объяснение реализации бизнес-логики

### Бизнес-логика 1: Выдача книги при наличии экземпляров

Реализация находится в `crud_borrowed_book.py` в функции `borrow_book()`:

```python
def borrow_book(db: Session, borrow_data: BorrowBookCreate) -> BorrowedBook:
    db_book = db.query(Book).filter(Book.id == borrow_data.book_id).first()
    if db_book.quantity <= 0:
        raise ValueError("Нет доступных экземпляров книги")
    
    # ... остальной код ...
    
    db_book.quantity -= 1
    db.add(db_book)
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow
```

При выдаче книги проверяется наличие доступных экземпляров (`db_book.quantity > 0`). Если экземпляры есть, количество уменьшается на 1, и создается запись о выдаче. Если экземпляров нет, генерируется исключение.

**Сложности и решения**: Необходимо было обеспечить атомарность операции уменьшения количества книг и создания записи о выдаче. Решение - использовать транзакции SQLAlchemy, которые гарантируют, что либо обе операции выполнятся успешно, либо ни одна из них.

### Бизнес-логика 2: Ограничение на количество книг у читателя

Реализация также находится в `crud_borrowed_book.py`:

```python
def count_active_borrowed_books_by_reader(db: Session, reader_id: int) -> int:
    return db.query(BorrowedBook).filter(
        and_(
            BorrowedBook.reader_id == reader_id,
            BorrowedBook.return_date.is_(None)
        )
    ).count()

def borrow_book(db: Session, borrow_data: BorrowBookCreate) -> BorrowedBook:
    # ... проверка наличия книги ...
    
    active_books_count = count_active_borrowed_books_by_reader(
        db, reader_id=borrow_data.reader_id
    )
    if active_books_count >= 3:
        raise ValueError("Читатель уже взял максимальное количество книг (3)")
    
    # ... остальной код ...
```

Перед выдачей книги проверяется количество активных (невозвращенных) книг у читателя. Если их 3 или больше, выдача запрещается.

**Сложности и решения**: Необходимо было эффективно подсчитывать только активные выдачи (где return_date is NULL). Решение - использовать SQL-запрос с фильтрацией по условию `return_date.is_(None)`.

### Бизнес-логика 3: Проверка при возврате книги

Реализация в функции `return_book()`:

```python
def return_book(db: Session, db_borrow: BorrowedBook) -> BorrowedBook:
    if db_borrow.return_date:
        raise ValueError("Книга уже возвращена")
    
    db_borrow.return_date = datetime.utcnow()
    db.add(db_borrow)
    
    db_book = db.query(Book).filter(Book.id == db_borrow.book_id).first()
    db_book.quantity += 1
    db.add(db_book)
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow
```

При возврате книги проверяется, была ли она выдана этому читателю и не возвращена ли она уже. Если книга уже возвращена (поле `return_date` не NULL), генерируется исключение.

**Сложности и решения**: Необходимо было обеспечить корректное обновление количества книг при возврате. Решение - использовать транзакции SQLAlchemy для атомарного обновления записи о выдаче и увеличения количества книг.

## Реализация аутентификации

### Используемые библиотеки

- **python-jose**: Для создания и проверки JWT-токенов
- **passlib[bcrypt]**: Для безопасного хеширования и проверки паролей

### Генерация и проверка токенов

Генерация JWT-токена происходит в модуле `security/jwt.py`:

```python
def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
```

Токен содержит идентификатор пользователя (`sub`) и время истечения (`exp`). Он подписывается с использованием секретного ключа и алгоритма HS256.

Проверка токена происходит в функции `decode_token()`:

```python
def decode_token(token: str) -> Optional[TokenPayload]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if datetime.fromtimestamp(token_data.exp) < datetime.utcnow():
            return None
        
        return token_data
    except (jwt.JWTError, ValidationError):
        return None
```

### Хеширование паролей

Хеширование паролей реализовано в модуле `security/password.py` с использованием библиотеки passlib:

```python
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Защищенные эндпоинты

Все эндпоинты, кроме регистрации и входа, защищены JWT-токеном. Защита реализована с помощью зависимости FastAPI `get_current_active_user`:

```python
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id=int(token_data.sub))
    if user is None:
        raise credentials_exception
    
    return user
```

Эта зависимость используется во всех защищенных эндпоинтах:

```python
@router.get("/", response_model=List[Book])
def read_books(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    books = crud_book.get_books(db, skip=skip, limit=limit)
    return books
```

Я решил защитить все эндпоинты API, включая получение списка книг, так как в реальной библиотечной системе информация о книгах и их наличии должна быть доступна только авторизованным сотрудникам библиотеки.

## Дополнительная фича: Система штрафов за просрочку возврата

Предлагается добавить систему штрафов за несвоевременный возврат книг:

### Реализация:

1. **Модификация модели BorrowedBook**:
   - Добавить поле `due_date` (дата, к которой книга должна быть возвращена)

2. **Создание новой модели Fine**:
   ```python
   class Fine(Base):
       __tablename__ = "fines"
       
       id = Column(Integer, primary_key=True, index=True)
       borrowed_book_id = Column(Integer, ForeignKey("borrowed_books.id"))
       amount = Column(Float, nullable=False)
       paid = Column(Boolean, default=False)
       created_at = Column(DateTime(timezone=True), server_default=func.now())
       paid_at = Column(DateTime(timezone=True), nullable=True)
       
       borrowed_book = relationship("BorrowedBook", back_populates="fine")
   ```

3. **Логика расчета штрафа**:
   - При возврате книги проверять, не просрочен ли срок возврата
   - Если просрочен, рассчитывать штраф по формуле: `(текущая_дата - due_date) * дневная_ставка`
   - Создавать запись о штрафе в таблице `fines`

4. **Новые эндпоинты**:
   - `GET /api/v1/fines/reader/{reader_id}` - получение всех штрафов читателя
   - `POST /api/v1/fines/{fine_id}/pay` - отметка штрафа как оплаченного
   - `GET /api/v1/fines/report` - генерация отчета по штрафам за период

Эта фича позволит библиотеке отслеживать своевременность возврата книг, мотивировать читателей возвращать книги вовремя и получать дополнительный доход для покрытия расходов на обновление фонда.
