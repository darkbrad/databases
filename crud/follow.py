from schemas.user import UserModel
import sqlite3


class FollowCRUD:
    def exists(
        self, conn: sqlite3.Connection, user: UserModel, to_follow: UserModel
    ) -> bool:
        cur = conn.cursor()

        try:
            cur.execute(
                "SELECT COUNT(*) FROM Follow WHERE follower=? AND follows=?",
                (user.id, to_follow.id),
            )
            count, *_ = cur.fetchone()
            return count == 1
        finally:
            cur.close()

    def create(
        self, conn: sqlite3.Connection, user: UserModel, to_follow: UserModel
    ) -> None:
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO Follow VALUES(?, ?)", (user.id, to_follow.id))
        finally:
            cur.close()

    def delete(
        self, conn: sqlite3.Connection, user: UserModel, to_unfollow: UserModel
    ) -> None:
        cur = conn.cursor()

        try:
            cur.execute(
                "DELETE FROM Follow WHERE follower=? AND follows=?",
                (user.id, to_unfollow.id),
            )
        finally:
            cur.close()