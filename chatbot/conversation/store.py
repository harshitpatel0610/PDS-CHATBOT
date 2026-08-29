from .session import ConversationSession


class ConversationStore:
    """
    Stores all active conversation sessions.
    """

    _sessions = {}

    @classmethod
    def get(cls, session_id: str) -> ConversationSession:

        if session_id not in cls._sessions:
            cls._sessions[session_id] = ConversationSession(session_id)

        return cls._sessions[session_id]

    @classmethod
    def save(cls, session: ConversationSession):

        cls._sessions[session.session_id] = session

    @classmethod
    def delete(cls, session_id: str):

        cls._sessions.pop(session_id, None)

    @classmethod
    def clear(cls):

        cls._sessions.clear()

    @classmethod
    def count(cls):

        return len(cls._sessions)

    @classmethod
    def all_sessions(cls):

        return cls._sessions