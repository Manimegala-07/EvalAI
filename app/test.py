from app.services.scoring_service import ScoringService

scorer = ScoringService()

refs = ["Photosynthesis is how plants make food"]
students = ["Plants use sunlight to produce food"]

result = scorer.grade_batch(refs, students)

print(result)
