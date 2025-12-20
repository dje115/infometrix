#!/usr/bin/env python3
"""
EnforceSense AI Service for Enforcement API

Handles AI-powered note improvement and case analysis
"""

import logging
import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timezone

# Import models from Enforcement API
from app.modules.enforcesense.models import CaseNote, EnforcementCase, Debtor

logger = logging.getLogger(__name__)


class EnforceSenseAIService:
    """
    AI service for EnforceSense module
    
    Handles:
    - Note improvement (cleaning, grammar, professional tone)
    - Risk flag extraction
    - Note summarization
    """
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def improve_note(self, note_id: str) -> Dict[str, Any]:
        """
        Improve a case note using AI
        
        Args:
            note_id: ID of the note to improve
            
        Returns:
            Dict with improved note data
        """
        try:
            # Get note
            stmt = select(CaseNote).where(
                and_(
                    CaseNote.id == note_id,
                    CaseNote.tenant_id == self.tenant_id,
                    CaseNote.is_deleted == False
                )
            )
            result = await self.db.execute(stmt)
            note = result.scalar_one_or_none()
            
            if not note:
                raise ValueError(f"Note {note_id} not found")
            
            # Get case context
            case_stmt = select(EnforcementCase).where(
                and_(
                    EnforcementCase.id == note.case_id,
                    EnforcementCase.tenant_id == self.tenant_id
                )
            )
            case_result = await self.db.execute(case_stmt)
            case = case_result.scalar_one_or_none()
            
            if not case:
                raise ValueError(f"Case {note.case_id} not found")
            
            # Get debtor context
            debtor_context = ""
            if case.debtor_id:
                debtor_stmt = select(Debtor).where(
                    and_(
                        Debtor.id == case.debtor_id,
                        Debtor.tenant_id == self.tenant_id
                    )
                )
                debtor_result = await self.db.execute(debtor_stmt)
                debtor = debtor_result.scalar_one_or_none()
                if debtor:
                    debtor_context = f"Debtor: {debtor.name} ({debtor.entity_type.value if hasattr(debtor.entity_type, 'value') else debtor.entity_type})"
            
            # Build prompt for AI
            prompt = f"""You are an AI assistant helping enforcement agents write professional, clear, and compliant case notes.

Original Note:
{note.original_note or note.note}

Case Context:
- Case Reference: {case.case_reference}
- Status: {case.status.value if hasattr(case.status, 'value') else case.status}
- Original Amount: £{case.original_amount}
- Current Balance: £{case.current_balance}
{debtor_context}

Please:
1. Clean up the note (fix grammar, spelling, improve clarity)
2. Make it professional and compliant
3. Extract any risk flags (e.g., "payment refused", "threats made", "address changed")
4. Create a brief summary (1-2 sentences)

Return JSON format:
{{
    "cleaned_note": "improved note text",
    "summary": "brief summary",
    "risk_flags": ["flag1", "flag2"]
}}
"""
            
            # Call AI service
            # TODO: Implement AI provider service for Enforcement API
            # For now, use OpenAI directly as a placeholder
            try:
                import os
                from openai import AsyncOpenAI
                
                openai_key = os.getenv("OPENAI_API_KEY")
                if not openai_key:
                    raise ValueError("OPENAI_API_KEY not set")
                
                client = AsyncOpenAI(api_key=openai_key)
                
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a professional enforcement case note assistant. Always return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                
                ai_result = json.loads(response.choices[0].message.content)
                
                # Update note with AI improvements
                note.ai_improved_note = ai_result.get('cleaned_note', '')
                note.ai_summary = ai_result.get('summary', '')
                note.risk_flags = ai_result.get('risk_flags', [])
                note.ai_processing_status = 'completed'
                
                # Update the main note field to show improved version
                if note.ai_improved_note:
                    note.note = note.ai_improved_note
                
                await self.db.commit()
                await self.db.refresh(note)
                
                return {
                    "success": True,
                    "improved_note": note.ai_improved_note,
                    "summary": note.ai_summary,
                    "risk_flags": note.risk_flags
                }
                
            except Exception as ai_error:
                logger.error(f"AI processing error: {ai_error}", exc_info=True)
                note.ai_processing_status = 'failed'
                await self.db.commit()
                raise
            
        except Exception as e:
            logger.error(f"Error improving note {note_id}: {e}", exc_info=True)
            # Update note status to failed
            try:
                note_stmt = select(CaseNote).where(
                    and_(
                        CaseNote.id == note_id,
                        CaseNote.tenant_id == self.tenant_id
                    )
                )
                note_result = await self.db.execute(note_stmt)
                note = note_result.scalar_one_or_none()
                if note:
                    note.ai_processing_status = 'failed'
                    await self.db.commit()
            except:
                pass
            
            raise



