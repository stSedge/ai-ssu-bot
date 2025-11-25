from app.core.database import PostgresDatabase
from app.repository.session_repository import SessionRepository
from app.repository.message_repository import MessageRepository
from app.repository.faq_repository import FAQRepository

from app.service.session_service import SessionService
from app.service.message_service import MessageService
from app.service.faq_service import FAQService

database = PostgresDatabase()
session_repo = SessionRepository()
message_repo = MessageRepository()
faq_repo = FAQRepository()

session_service = SessionService(session_repo)
message_service = MessageService(message_repo, session_repo)
faq_service = FAQService(faq_repo)
