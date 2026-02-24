from app.services.feedback_service import FeedbackService


class FeedbackWorker:

    def __init__(self):
        self.service = FeedbackService()

    def process_batch(self, refs, students, scores):

        feedbacks = []

        for r, s, sc in zip(refs, students, scores):
            fb = self.service.generate(r, s, sc)
            feedbacks.append(fb)

        return feedbacks
