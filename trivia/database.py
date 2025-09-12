"""
Trivia database module for goobie-bot
Handles SQLite database operations for trivia questions, scores, and sessions
"""

import sqlite3
import logging
import json
from datetime import date
from typing import Optional, List, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TriviaDatabase:
    """Manages trivia database operations"""

    def __init__(self, db_path: str = "trivia/data/trivia.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # User scores and statistics
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trivia_scores (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT NOT NULL,
                        total_score INTEGER DEFAULT 0,
                        questions_answered INTEGER DEFAULT 0,
                        correct_answers INTEGER DEFAULT 0,
                        current_streak INTEGER DEFAULT 0,
                        best_streak INTEGER DEFAULT 0,
                        last_played DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Daily trivia questions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trivia_questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        question TEXT NOT NULL,
                        correct_answer TEXT NOT NULL,
                        wrong_answers TEXT NOT NULL,
                        category TEXT NOT NULL,
                        difficulty TEXT NOT NULL,
                        used_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Daily trivia sessions (posts in channels)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trivia_daily_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL UNIQUE,
                        channel_id INTEGER NOT NULL,
                        message_id INTEGER NOT NULL,
                        question_id INTEGER NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (question_id) REFERENCES trivia_questions(id)
                    )
                """)

                # User daily trivia attempts
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trivia_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date DATE NOT NULL,
                        question_id INTEGER NOT NULL,
                        score INTEGER DEFAULT 0,
                        time_taken REAL DEFAULT 0,
                        is_correct BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (question_id) REFERENCES trivia_questions(id),
                        UNIQUE(user_id, date)
                    )
                """)

                conn.commit()
                logger.info("Trivia database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing trivia database: {e}")
            raise

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)

    # User score operations
    def get_user_score(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's trivia score and statistics"""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM trivia_scores WHERE user_id = ?", (user_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting user score: {e}")
            return None

    def create_user_score(self, user_id: int, username: str) -> bool:
        """Create new user score record"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO trivia_scores (user_id, username) VALUES (?, ?)",
                    (user_id, username),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # User already exists, update username
            return self.update_user_username(user_id, username)
        except Exception as e:
            logger.error(f"Error creating user score: {e}")
            return False

    def update_user_username(self, user_id: int, username: str) -> bool:
        """Update user's username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE trivia_scores SET username = ? WHERE user_id = ?",
                    (username, user_id),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating username: {e}")
            return False

    def update_user_score(
        self, user_id: int, score: int, is_correct: bool, time_taken: float
    ) -> bool:
        """Update user's score after trivia attempt"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get current user data
                current = self.get_user_score(user_id)
                if not current:
                    return False

                # Calculate new values
                new_total_score = current["total_score"] + score
                new_questions_answered = current["questions_answered"] + 1
                new_correct_answers = current["correct_answers"] + (
                    1 if is_correct else 0
                )

                # Calculate streak
                if is_correct:
                    new_current_streak = current["current_streak"] + 1
                    new_best_streak = max(current["best_streak"], new_current_streak)
                else:
                    new_current_streak = 0
                    new_best_streak = current["best_streak"]

                # Update user score
                cursor.execute(
                    """
                    UPDATE trivia_scores 
                    SET total_score = ?, questions_answered = ?, correct_answers = ?,
                        current_streak = ?, best_streak = ?, last_played = ?
                    WHERE user_id = ?
                """,
                    (
                        new_total_score,
                        new_questions_answered,
                        new_correct_answers,
                        new_current_streak,
                        new_best_streak,
                        date.today(),
                        user_id,
                    ),
                )

                # Record the attempt
                cursor.execute(
                    """
                    INSERT INTO trivia_attempts 
                    (user_id, date, question_id, score, time_taken, is_correct)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (user_id, date.today(), 0, score, time_taken, is_correct),
                )

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Error updating user score: {e}")
            return False

    def has_user_played_today(self, user_id: int) -> bool:
        """Check if user has already played trivia today"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM trivia_attempts WHERE user_id = ? AND date = ?",
                    (user_id, date.today()),
                )
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking if user played today: {e}")
            return False

    # Question operations
    def add_question(
        self,
        question: str,
        correct_answer: str,
        wrong_answers: List[str],
        category: str,
        difficulty: str,
    ) -> bool:
        """Add a new trivia question"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO trivia_questions 
                    (question, correct_answer, wrong_answers, category, difficulty)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        question,
                        correct_answer,
                        json.dumps(wrong_answers),
                        category,
                        difficulty,
                    ),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding question: {e}")
            return False

    def get_random_question(
        self, category: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a random unused question"""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Get questions that haven't been used today
                if category:
                    cursor.execute(
                        """
                        SELECT * FROM trivia_questions 
                        WHERE category = ? AND (used_date IS NULL OR used_date != ?)
                        ORDER BY RANDOM() LIMIT 1
                    """,
                        (category, date.today()),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT * FROM trivia_questions 
                        WHERE used_date IS NULL OR used_date != ?
                        ORDER BY RANDOM() LIMIT 1
                    """,
                        (date.today(),),
                    )

                row = cursor.fetchone()
                if row:
                    question_data = dict(row)
                    question_data["wrong_answers"] = json.loads(
                        question_data["wrong_answers"]
                    )
                    return question_data
                return None

        except Exception as e:
            logger.error(f"Error getting random question: {e}")
            return None

    def mark_question_used(self, question_id: int) -> bool:
        """Mark a question as used today"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE trivia_questions SET used_date = ? WHERE id = ?",
                    (date.today(), question_id),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking question as used: {e}")
            return False

    # Daily post operations
    def create_daily_post(
        self, channel_id: int, message_id: int, question_id: int
    ) -> bool:
        """Record a daily trivia post"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO trivia_daily_posts 
                    (date, channel_id, message_id, question_id)
                    VALUES (?, ?, ?, ?)
                """,
                    (date.today(), channel_id, message_id, question_id),
                )
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error creating daily post: {e}")
            return False

    def get_daily_post(
        self, target_date: Optional[date] = None
    ) -> Optional[Dict[str, Any]]:
        """Get today's daily post info"""
        if target_date is None:
            target_date = date.today()

        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM trivia_daily_posts WHERE date = ?", (target_date,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting daily post: {e}")
            return None

    # Leaderboard operations
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top users leaderboard"""
        try:
            with self.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT username, total_score, questions_answered, 
                           correct_answers, best_streak, last_played
                    FROM trivia_scores 
                    ORDER BY total_score DESC, best_streak DESC
                    LIMIT ?
                """,
                    (limit,),
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []

    def get_user_rank(self, user_id: int) -> int:
        """Get user's rank in leaderboard"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT COUNT(*) + 1 as rank
                    FROM trivia_scores 
                    WHERE total_score > (
                        SELECT total_score FROM trivia_scores WHERE user_id = ?
                    )
                """,
                    (user_id,),
                )
                result = cursor.fetchone()
                return result[0] if result else 1
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return 1
