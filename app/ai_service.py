import openai
from typing import Optional, List
from app.config import settings
from app.schemas import AIJournalResponse

# Initialize OpenAI client
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key


class AIJournalService:
    def __init__(self):
        self.client = None
        if settings.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI client: {e}")
                self.client = None
    
    async def generate_journal_response(
        self, 
        journal_content: str, 
        mood_before: Optional[int] = None,
        previous_entries: Optional[List[str]] = None
    ) -> AIJournalResponse:
        """Generate an empathetic AI response to a journal entry"""
        
        if not self.client:
            return AIJournalResponse(
                response="I'm sorry, but the AI service is not available at the moment. Please try again later.",
                mood_after=mood_before,
                suggestions=["Consider talking to a trusted friend or professional"]
            )
        
        # Build context from previous entries if available
        context = ""
        if previous_entries:
            context = f"Previous journal entries for context:\n" + "\n".join(previous_entries[-3:]) + "\n\n"
        
        # Create mood context
        mood_context = ""
        if mood_before:
            mood_descriptions = {
                1: "very low",
                2: "low", 
                3: "somewhat low",
                4: "below average",
                5: "neutral",
                6: "above average",
                7: "good",
                8: "very good",
                9: "excellent",
                10: "outstanding"
            }
            mood_context = f"The user mentioned their mood was {mood_descriptions.get(mood_before, 'neutral')} ({mood_before}/10) before writing this entry.\n\n"
        
        prompt = f"""You are a compassionate and understanding AI journal companion. Your role is to provide empathetic, supportive, and helpful responses to users' journal entries. 

{context}{mood_context}User's journal entry:
"{journal_content}"

Please respond with:
1. Acknowledgment and validation of their feelings
2. Gentle insights or observations about their situation
3. Encouragement and support
4. Practical suggestions if appropriate
5. A question to encourage further reflection

Keep your response warm, empathetic, and conversational. Avoid being overly clinical or giving unsolicited advice. Focus on being a supportive listener who understands and cares.

Your response should be 2-3 paragraphs long and end with a thoughtful question to encourage continued reflection."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a compassionate AI journal companion who provides empathetic and supportive responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Generate suggestions based on the content
            suggestions = self._generate_suggestions(journal_content, mood_before)
            
            # Estimate mood after (simple heuristic)
            mood_after = self._estimate_mood_after(journal_content, mood_before)
            
            return AIJournalResponse(
                response=ai_response,
                mood_after=mood_after,
                suggestions=suggestions
            )
            
        except Exception as e:
            return AIJournalResponse(
                response=f"I'm here to listen and support you. Your thoughts and feelings are valid, and it's great that you're taking time to reflect through journaling. What would you like to explore further about your current situation?",
                mood_after=mood_before,
                suggestions=["Consider what you're grateful for today", "Think about what you need most right now"]
            )
    
    def _generate_suggestions(self, content: str, mood_before: Optional[int]) -> List[str]:
        """Generate helpful suggestions based on journal content"""
        suggestions = []
        
        # Mood-based suggestions
        if mood_before and mood_before <= 4:
            suggestions.extend([
                "Try a short breathing exercise",
                "Write down three things you're grateful for",
                "Consider reaching out to a friend"
            ])
        elif mood_before and mood_before >= 7:
            suggestions.extend([
                "Share your positive energy with someone else",
                "Set a small goal for tomorrow",
                "Reflect on what contributed to your good mood"
            ])
        else:
            suggestions.extend([
                "Take a short walk outside",
                "Practice mindfulness for 5 minutes",
                "Write about what you need most right now"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _estimate_mood_after(self, content: str, mood_before: Optional[int]) -> Optional[int]:
        """Simple heuristic to estimate mood after journaling"""
        if not mood_before:
            return None
        
        # Simple keyword-based mood estimation
        positive_words = ["happy", "good", "great", "excited", "grateful", "proud", "accomplished", "better", "relief"]
        negative_words = ["sad", "angry", "frustrated", "worried", "anxious", "stressed", "overwhelmed", "tired"]
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        # Adjust mood based on content
        if positive_count > negative_count:
            return min(10, mood_before + 1)
        elif negative_count > positive_count:
            return max(1, mood_before - 1)
        else:
            return mood_before


# Global instance
ai_journal_service = AIJournalService()
