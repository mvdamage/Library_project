import sqlite3

class Database:
    def __init__(self, db_name="library.db"):
        self.conn = sqlite3.connect(db_name)
        """self.conn.create_function(
            "py_lower",
            1,
            lambda value: "" if value is None else str(value).lower(),
        )"""
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """Создание таблицы книг, если она не существует"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                volume INTEGER,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                genre TEXT NOT NULL
            )
        ''')
        self.conn.commit()
    
    def add_book(self, title, volume, author, year, genre):
        """Добавление новой книги"""
        self.cursor.execute('''
            INSERT INTO library (title, volume, author, year, genre)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, volume, author, year, genre))
        self.conn.commit()
        return self.cursor.lastrowid
      
    def delete_book(self, book_id):
        """Удаление книги"""
        self.cursor.execute("DELETE FROM library WHERE id = ?", (book_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def update_book(self, book_id,  title, volume, author, year, genre):
        """Обновление информации о книге"""
        self.cursor.execute('''
            UPDATE library 
            SET title = ?, volume = ?, author = ?, year = ?, genre = ?
            WHERE id = ? 
        ''', (title, volume, author, year, genre, book_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def _norm_volume(self, volume):
        """Нормализация сохранения тома книги"""
        if volume is None:
            return ""
        s = str(volume).strip()
        return "" if not s else s

    def get_all_books(self):
        """Получение всех книг"""
        self.cursor.execute('''
            SELECT id, title, volume, author, year, genre 
            FROM library ORDER BY id
        ''')
        return self.cursor.fetchall()
    
    
    def search_book(self, search_term):
        """Поиск книги по автору, названию, году или жанру без учета регистра"""
        pattern = f'%{search_term.lower()}%'
        self.cursor.execute('''
            SELECT id, title, volume, author, year, genre
            FROM library
            WHERE py_lower(title) LIKE ? 
                OR py_lower(author) LIKE ? 
                OR py_lower(year) LIKE ? 
                OR py_lower(genre) LIKE ?
             ORDER BY id
        ''', (pattern, pattern, pattern, pattern))
        return self.cursor.fetchall()
    
    def count_books(self):
        """Общее количество книг"""
        self.cursor.execute("SELECT COUNT(*) FROM library")
        return self.cursor.fetchone()[0]
    
    def count_by_genre(self):
        """Количество книг по жанрам"""
        self.cursor.execute('''
            SELECT genre, COUNT(*)
            FROM library
            GROUP BY genre
            ORDER BY COUNT(*) DESC, genre
        ''')
        return self.cursor.fetchall()
    
    def count_by_author(self):
        """Количество книг по авторам"""
        self.cursor.execute('''
            SELECT author, COUNT(*)
            FROM library
            GROUP BY author
            ORDER BY COUNT(*) DESC, author
        ''')
        return self.cursor.fetchall()

    def is_duplicate_book(self, title, volume, author, year, genre, exclude_id=None):
        """ Проверка на дубликаты
        True, если в БД уже есть книга с теми же полями.
        exclude_id — id текущей книги при редактировании (её не считаем дубликатом).
        """
        title = (title or "").strip()
        author = (author or "").strip()
        genre = (genre or "").strip()
        year_s = str(year).strip() if year is not None else ""
        vol = self._norm_volume(volume)
        sql = """
            SELECT id FROM library
            WHERE title = ?
                AND author = ?
                AND genre = ?
                AND CAST(year AS TEXT) = ?
                AND COALESCE(TRIM(CAST(volume AS TEXT)), '') = ?
        """
        params = [title, author, genre, year_s, vol]
        if exclude_id is not None:
            sql += " AND id != ?"
            params.append(exclude_id)
        self.cursor.execute(sql, params)
        return self.cursor.fetchone() is not None
    
    def close(self):
        """Закрытие соединения с базой данных"""
        self.conn.close()