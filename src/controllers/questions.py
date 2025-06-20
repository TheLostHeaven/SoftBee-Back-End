import json
from ..models.questions import QuestionModel

class QuestionController:
    def __init__(self, db):
        self.db = db
        self.model = QuestionModel
    
    def create_question(self, user_id, question_id, question_text, question_type, 
                    is_required=False, display_order=0, min_value=None, 
                    max_value=None, options=None, depends_on=None, is_active=True):
        """Creates a new question for a user"""
        if question_type == 'option' and (not options or len(options) < 2):
            raise ValueError("Option questions require at least 2 options")
        
        if question_type == 'number' and (min_value is None or max_value is None):
            raise ValueError("Number questions require min and max values")
        
        return self.model.create(
            self.db, user_id, question_id, question_text, question_type,
            is_required, display_order, min_value, max_value, options,
            depends_on, is_active)
    
    def get_question(self, question_id):
        """Gets question by ID"""
        return self.model.get_by_id(self.db, question_id)
    
    def get_user_questions(self, user_id, active_only=True):
        """Gets all questions for a user"""
        return self.model.get_by_user(self.db, user_id, active_only)
    
    def update_question(self, question_id, **kwargs):
        """Updates question information"""
        if 'question_type' in kwargs:
            if kwargs['question_type'] == 'option' and ('options' not in kwargs or len(kwargs['options']) < 2):
                raise ValueError("Option questions require at least 2 options")
            
            if kwargs['question_type'] == 'number' and ('min_value' not in kwargs or 'max_value' not in kwargs):
                raise ValueError("Number questions require min and max values")
        
        self.model.update(self.db, question_id, **kwargs)
    
    def delete_question(self, question_id):
        """Deletes a question"""
        self.model.delete(self.db, question_id)
    
    def reorder_questions(self, user_id, new_order):
        """Reorders questions for a user"""
        if len(new_order) != len(set(new_order)):
            raise ValueError("Duplicate question IDs in order list")
        
        current_questions = {q['id'] for q in self.get_user_questions(user_id, False)}
        if set(new_order) != current_questions:
            raise ValueError("Order list doesn't match user's questions")
        
        self.model.reorder(self.db, user_id, new_order)